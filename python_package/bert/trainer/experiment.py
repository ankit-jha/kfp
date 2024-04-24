import os

import hypertune
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from trainer import metadata, model, utils
from transformers import AutoTokenizer, EvalPrediction, Trainer, TrainerCallback, TrainingArguments


class HPTuneCallback(TrainerCallback):
    """
    A custom callback class that reports a metric to hypertuner
    at the end of each epoch.
    """

    def __init__(self, metric_tag, metric_value):
        super(HPTuneCallback, self).__init__()
        self.metric_tag = metric_tag
        self.metric_value = metric_value
        self.hpt = hypertune.HyperTune()

    def on_evaluate(self, args, state, control, **kwargs):
        print(f"HP metric {self.metric_tag}={kwargs['metrics'][self.metric_value]}")
        self.hpt.report_hyperparameter_tuning_metric(
            hyperparameter_metric_tag=self.metric_tag,
            metric_value=kwargs["metrics"][self.metric_value],
            global_step=state.epoch,
        )


def compute_metrics(pred: EvalPrediction):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}


def train(args, model, train_dataset, test_dataset):
    """Create the training loop to load pretrained model and tokenizer and
    start the training process

    Args:
      args: read arguments from the runner to set training hyperparameters
      model: The neural network that you are training
      train_dataset: The training dataset
      test_dataset: The test dataset for evaluation
    """

    # initialize the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        metadata.PRETRAINED_MODEL_NAME,
    )

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            padding="max_length",
            truncation=True,
            max_length=128,
            # return_tensors='pt',
        )

    sentiment_dataset_train = train_dataset.map(tokenize, batched=True, batch_size=32)
    sentiment_dataset_test = test_dataset.map(tokenize, batched=True, batch_size=32)

    sentiment_dataset_train.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
    sentiment_dataset_test.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

    # set training arguments
    training_args = TrainingArguments(
        output_dir=os.path.join("/tmp", args.model_name),
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        warmup_steps=500,
        weight_decay=args.weight_decay,
        save_total_limit=5,
        evaluation_strategy="steps",
        eval_steps=500,
        logging_dir="./logs",
    )

    # initialize our Trainer
    model_trainer = Trainer(
        model,
        args=training_args,
        compute_metrics=compute_metrics,
        train_dataset=sentiment_dataset_train,
        eval_dataset=sentiment_dataset_test,
    )

    # add hyperparameter tuning callback to report metrics when enabled
    if args.hp_tune == "y":
        model_trainer.add_callback(HPTuneCallback("accuracy", "eval_accuracy"))

    # training
    model_trainer.train()

    return model_trainer


def run(args):
    """Load the data, train, evaluate, and export the model for serving and
     evaluating.

    Args:
      args: experiment parameters.
    """
    # Open our dataset
    train_dataset, test_dataset = utils.load_data(args)

    label_list = train_dataset.unique("labels")
    num_labels = len(label_list)

    # Create the model, loss function, and optimizer
    text_classifier = model.create(num_labels=num_labels)

    # Train / Test the model
    model_trainer = train(args, text_classifier, train_dataset, test_dataset)

    metrics = model_trainer.evaluate()
    model_trainer.save_metrics("all", metrics)

    # Export the trained model
    model_trainer.save_model(os.path.join("/tmp", args.model_name))

    # Save the model to GCS
    if args.job_dir:
        utils.save_model(args)
    else:
        print(f"Saved model files at {os.path.join('/tmp', args.model_name)}")
        print(f"To save model files in GCS bucket, please specify job_dir starting with gs://")

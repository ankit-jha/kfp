from kfp.v2.dsl import component


# Training Component
@component(
    packages_to_install=[
        "google-cloud-storage",
        "datasets",
        "torch",
        "transformers",
        "scikit-learn",
    ]
)
def training(gcp_bucket_name: str, gcp_dataset_name: str):

    import logging

    import pandas as pd
    from google.cloud import storage
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    from transformers import (
        AutoTokenizer,
        BertForSequenceClassification,
        Trainer,
        TrainingArguments,
    )

    client = storage.Client()
    logging.info("Client created using default project: {}".format(client.project))
    bucket = client.get_bucket(gcp_bucket_name)
    logging.info("Bucket name: {}".format(bucket.name))

    blobs = bucket.list_blobs()
    logging.info("Blobs in {}:".format(bucket.name))
    for item in blobs:
        logging.info("\t" + item.name)

    blob = bucket.get_blob(gcp_dataset_name)
    logging.info("Name: {}".format(blob.name))

    data_file = "test.csv"
    blob.download_to_filename(data_file)
    negative_df = pd.read_csv(data_file)
    from datasets import Dataset
    from sklearn.model_selection import train_test_split

    sentiment_dataset_train, sentiment_dataset_test = train_test_split(
        negative_df[["text", "labels"]], test_size=0.0125
    )

    # write to CSV for reference
    sentiment_dataset_train.to_pickle("train.pkl")
    sentiment_dataset_test.to_pickle("test.pkl")

    # model upload
    source_file_name = "train.pkl"
    blob_name = f"data/transformers_test_data/{source_file_name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(source_file_name)

    source_file_name = "test.pkl"
    blob_name = f"data/transformers_test_data/{source_file_name}"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(source_file_name)

    logging.info("File uploaded to {}.".format(bucket.name))
    # sub sample sentiment TRAINING set, level test set at the same ratio
    sentiment_dataset_train = sentiment_dataset_train[sentiment_dataset_train.labels == 1].append(
        sentiment_dataset_train[sentiment_dataset_train.labels == 0].sample(
            sentiment_dataset_train.labels.sum() * 9
        )
    )

    # sentiment_dataset_train = pd.read_pickle("data/transformers_test_data/train.pkl")
    # sentiment_dataset_test = pd.read_pickle("data/transformers_test_data/test.pkl")

    sentiment_dataset_train = Dataset.from_pandas(sentiment_dataset_train[["labels", "text"]])
    sentiment_dataset_test = Dataset.from_pandas(sentiment_dataset_test[["labels", "text"]])
    model = BertForSequenceClassification.from_pretrained("bert-base-uncased")
    # tokenizer = DistilBertTokenizerFast.from_pretrained('results/checkpoint-52000/')
    # tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            padding="max_length",
            truncation=True,
            max_length=128,
            # return_tensors='pt',
        )

    sentiment_dataset_train = sentiment_dataset_train.map(tokenize, batched=True, batch_size=32)
    # batch_size=len(sentiment_dataset_train))
    sentiment_dataset_test = sentiment_dataset_test.map(tokenize, batched=True, batch_size=32)
    # batch_size=len(sentiment_dataset_train))

    sentiment_dataset_train.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
    sentiment_dataset_test.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

    def compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
        acc = accuracy_score(labels, preds)
        return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=1,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=32,
        warmup_steps=500,
        weight_decay=0.01,
        save_total_limit=5,
        evaluation_strategy="steps",
        eval_steps=500,
        logging_dir="./logs",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        compute_metrics=compute_metrics,
        train_dataset=sentiment_dataset_train,
        eval_dataset=sentiment_dataset_test,
    )

    trainer.train()

    # Upload model to staging bucket
    client = storage.Client()
    logging.info("Client created using default project: {}".format(client.project))
    bucket = client.get_bucket(gcp_bucket_name)
    logging.info("Bucket name: {}".format(bucket.name))
    bucket.blob("results/checkpoint-1500/pytorch_model.bin").upload_from_filename(
        "./results/checkpoint-1500/pytorch_model.bin"
    )
    bucket.blob("results/checkpoint-1500/config.json").upload_from_filename(
        "./results/checkpoint-1500/config.json"
    )
    logging.info("Files uploaded to {}.".format(bucket.name))

    # Evaluate
    trainer.evaluate()

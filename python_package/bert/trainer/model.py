from trainer import metadata
from transformers import BertForSequenceClassification


def create(num_labels):
    """create the model by loading a pretrained model or define your
    own

    Args:
      num_labels: number of target labels
    """
    # Create the model, loss function, and optimizer
    model = BertForSequenceClassification.from_pretrained(
        metadata.PRETRAINED_MODEL_NAME, num_labels=num_labels
    )

    return model

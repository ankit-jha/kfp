import json
import logging
import os

from transformers import AutoTokenizer, BertForSequenceClassification, pipeline
from ts.torch_handler.base_handler import BaseHandler

import torch

logger = logging.getLogger(__name__)


class TransformersClassifierHandler(BaseHandler):
    """
    The handler takes an input string and returns the classification text
    based on the serialized transformers checkpoint.
    """

    sentiment_classifier = None

    def __init__(self):
        self.sentiment_classifier = pipeline(
            "sentiment-analysis", model=self.model, tokenizer=self.tokenizer
        )
        super(TransformersClassifierHandler, self).__init__()
        self.initialized = False

    def initialize(self, ctx):
        """Loads the model.pt file and initialized the model object.
        Instantiates Tokenizer for preprocessor to use
        Loads labels to name mapping file for post-processing inference response
        """
        self.manifest = ctx.manifest

        properties = ctx.system_properties
        model_dir = properties.get("model_dir")
        self.device = torch.device(
            "cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu"
        )

        # Read model serialize/pt file
        serialized_file = self.manifest["model"]["serializedFile"]
        model_pt_path = os.path.join(model_dir, serialized_file)
        if not os.path.isfile(model_pt_path):
            raise RuntimeError("Missing the model.pt or pytorch_model.bin file")

        # Load model
        self.model = BertForSequenceClassification.from_pretrained(model_dir)
        self.model.to(self.device)
        self.model.eval()
        logger.debug("Transformer model from path {0} loaded successfully".format(model_dir))

        # Ensure to use the same tokenizer used during training
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

        # Read the mapping file, index to object name
        mapping_file_path = os.path.join(model_dir, "index_to_name.json")

        if os.path.isfile(mapping_file_path):
            with open(mapping_file_path) as f:
                self.mapping = json.load(f)
        else:
            logger.warning("Missing the index_to_name.json file. Inference output will default.")
            self.mapping = {"0": "Negative", "1": "Positive"}

        self.initialized = True

    def preprocess(self, data):
        """Preprocessing input request
        Extend with your own preprocessing steps as needed
        """
        logger.info("Received data: '%s'", data)
        # Needed for local testing
        inputs = data[0].get("body")
        if inputs is None:
            inputs = data
        return inputs

    def inference(self, inputs):
        """Predict the class of a text using a trained transformer model."""
        logging.info("Invoking Prediction Service")
        keys = texts = []
        for x in inputs:
            keys.append(list(x.keys())[0])
            texts.append(list(x.values())[0])
        inferences = []
        predictions = self.sentiment_classifier(texts)
        for key, pred in zip(keys, predictions):
            inferences.append({key: ({"label": pred["label"]}, {"score": pred["score"]})})
        logger.info("Model inferences: '%s'", inferences)
        return [inferences]

    def postprocess(self, inference_output):
        return inference_output

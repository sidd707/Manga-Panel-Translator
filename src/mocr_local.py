# mocr_local.py
import os

os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

from PIL import Image
import torch
from transformers import (
    TrOCRProcessor,  # <-- correct processor class
    AutoFeatureExtractor,
    AutoTokenizer,
    AutoModelForVision2Seq,  # v4.41+; keep until you migrate to AutoModelForImageTextToText
)


class LocalMangaOcr:
    def __init__(self, model_dir: str):
        # load pieces separately so the vision branch is never skipped
        feature_extractor = AutoFeatureExtractor.from_pretrained(
            model_dir, local_files_only=True
        )
        tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
        self.processor = TrOCRProcessor(feature_extractor, tokenizer)

        self.model = AutoModelForVision2Seq.from_pretrained(
            model_dir, use_safetensors=True, local_files_only=True
        )
        self.model.eval()

    def __call__(self, image: Image.Image) -> str:
        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            generated_ids = self.model.generate(**inputs)
        text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
        return text[0] if text else ""

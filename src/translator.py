from deep_translator import GoogleTranslator
from transformers import pipeline
import translators as ts


class MangaTranslator:
    def __init__(self, source="ja", target="en"):
        self.source = source
        self.target = target

    def translate(self, text, method="google"):
        text = self._preprocess_text(text)
        if method == "google":
            return (
                GoogleTranslator(source=self.source, target=self.target).translate(text)
                or text
            )
        else:
            return text

    def _preprocess_text(self, text):
        return text.replace("．", ".")

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from app.config import DEBERTA_MODEL, DEBERTA_INJECTION_THRESHOLD

class DeBERTaClassifier:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(DEBERTA_MODEL)
        self.model = AutoModelForSequenceClassification.from_pretrained(DEBERTA_MODEL)
        self.model.eval()

    def predict(self, text: str):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        prob = torch.softmax(logits, dim=1)[0][1].item()
        return prob > DEBERTA_INJECTION_THRESHOLD, prob

deberta_clf = None
def load_classifier():
    global deberta_clf
    deberta_clf = DeBERTaClassifier()
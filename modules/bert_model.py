import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import joblib
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "models" / "distilbert_drug_model"
LABEL_ENCODER_PATH = MODEL_DIR / "label_encoder.joblib"

# Load tokenizer & model
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR, local_files_only=True)
model.eval()

# Load label encoder
label_encoder = joblib.load(LABEL_ENCODER_PATH)

def predict_drug(text: str):
    """Predict drug name and confidence from symptom text"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
        predicted_id = torch.argmax(probs, dim=1).item()
        confidence = float(probs[0, predicted_id] * 100)
        predicted_label = label_encoder.inverse_transform([predicted_id])[0]
    return predicted_label, round(confidence, 2)

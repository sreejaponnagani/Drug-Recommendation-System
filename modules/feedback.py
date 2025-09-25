# feedback.py
import json
from pathlib import Path
from datetime import datetime

# Path to store feedback data
BASE_DIR = Path(__file__).parent
FEEDBACK_FILE = BASE_DIR / "feedback_log.json"

# Initialize feedback file if it doesn't exist
if not FEEDBACK_FILE.exists():
    with open(FEEDBACK_FILE, "w") as f:
        json.dump([], f, indent=4)


def update_feedback(
    user_id: str,
    symptoms: str,
    recommended_drug: str,
    rating: int,
    feedback_text: str,
    input_type: str,
    is_compatible: bool = None
):
    """
    Logs feedback and updates knowledge base for reinforcement.

    Args:
        user_id (str): Unique ID of the user.
        symptoms (str): Symptoms provided by the user.
        recommended_drug (str): Drug recommended by the system.
        rating (int): Rating given by user (1-5).
        feedback_text (str): Optional textual feedback.
        input_type (str): "text", "voice", or "image".
        is_compatible (bool, optional): Compatibility result for image input.
    """
    feedback_entry = {
        "timestamp": str(datetime.now()),
        "user_id": user_id,
        "symptoms": symptoms,
        "recommended_drug": recommended_drug,
        "rating": rating,
        "feedback_text": feedback_text,
        "input_type": input_type,
        "is_compatible": is_compatible
    }

    # Load existing feedback
    with open(FEEDBACK_FILE, "r") as f:
        feedback_data = json.load(f)

    # Append new feedback
    feedback_data.append(feedback_entry)

    # Save updated feedback
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback_data, f, indent=4)

    # Optionally, improve drug-symptom knowledge
    _update_knowledge_base(symptoms, recommended_drug, rating, is_compatible)


# ---- Internal function for simple reinforcement ----
KNOWN_DRUGS_FILE = BASE_DIR / "known_drugs.json"

# Initialize known drugs file if missing
if not KNOWN_DRUGS_FILE.exists():
    # Basic known drugs dictionary
    known_drugs = {
        "headache": ["Paracetamol", "Ibuprofen", "Aspirin"],
        "fever": ["Paracetamol", "Ibuprofen"],
        "pain": ["Ibuprofen", "Naproxen", "Aspirin"],
        "inflammation": ["Ibuprofen", "Naproxen"],
        "allergy": ["Loratadine", "Cetirizine"]
    }
    with open(KNOWN_DRUGS_FILE, "w") as f:
        json.dump(known_drugs, f, indent=4)


def _update_knowledge_base(symptoms, recommended_drug, rating, is_compatible):
    """
    Improves known_drugs dictionary based on user feedback.
    - Positive feedback (rating >=4) → add drug to matching symptoms
    - Negative feedback (rating <=2) → optionally remove or flag drug
    """
    with open(KNOWN_DRUGS_FILE, "r") as f:
        known_drugs = json.load(f)

    symptoms_lower = symptoms.lower()

    for condition in known_drugs.keys():
        if condition in symptoms_lower:
            if rating >= 4:
                if recommended_drug not in known_drugs[condition]:
                    known_drugs[condition].append(recommended_drug)
            elif rating <= 2:
                if recommended_drug in known_drugs[condition]:
                    # Optional: flag instead of removing
                    known_drugs[condition].remove(recommended_drug)

    # Save updated knowledge
    with open(KNOWN_DRUGS_FILE, "w") as f:
        json.dump(known_drugs, f, indent=4)

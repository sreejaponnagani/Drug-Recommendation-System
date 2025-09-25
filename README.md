# 💊 Drug Recommendation System

An AI-powered drug recommendation system that takes patient symptoms as input, matches them with a curated drug dataset, performs sentiment analysis on reviews, and recommends the best drugs.
The system is modular and extendable, with support for text, voice, and image inputs.

---

## 🚀 Features

* **Symptom-based search** – Users can enter symptoms and get drug suggestions.
* **Sentiment analysis on reviews** – Ranks drugs based on user feedback.
* **Voice input** – (optional) Users can speak their symptoms.
* **Pill image recognition** – Identify drugs from uploaded pill images.
* **Modular codebase** – All core functionalities split into modules/submodules.

---

## 📂 Project Structure

```
major_project/
│
├── modules/
│   ├── data_processing/        # Preprocessing, cleaning datasets
│   │   ├── __init__.py
│   │   └── preprocess.py
│   │
│   ├── models/                 # ML models (no large weights in repo)
│   │   ├── distilbert_drug_model/   # DistilBERT model directory (excluded weights)
│   │   └── train.py
│   │
│   ├── recommendation/         # Core recommendation logic
│   │   ├── __init__.py
│   │   └── recommend.py
│   │
│   ├── ui/                     # Streamlit interface and chatbot
│   │   ├── __init__.py
│   │   └── app.py
│   │
│   └── utils/                  # Helper functions
│       ├── __init__.py
│       └── helpers.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🛠️ Installation

> **Prerequisites**:
> – Python **3.11** installed
> – Git installed

1. **Clone the repository:**

```bash
git clone https://github.com/sreejaponnagani/Drug-Recommendation-System.git
cd Drug-Recommendation-System
```

2. **Create and activate a virtual environment (Python 3.11):**

Windows PowerShell:

```bash
python3.11 -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

3. **Install requirements:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📦 Typical `requirements.txt`

```
streamlit==1.28.0
pandas==2.1.0
numpy==1.26.0
scikit-learn==1.3.0
torch==2.1.0
transformers==4.34.0
sentencepiece
sounddevice
SpeechRecognition
opencv-python
Pillow
```

*(Adjust versions to your actual environment.)*

---

## ▶️ Running the Application

Run the Streamlit interface:

```bash
streamlit run modules/ui/app.py
```

This will launch the app in your browser at `http://localhost:8501`.

---

## 📝 Usage

1. Enter symptoms in the chatbot (or use voice input).
2. The system fetches matching drugs from the dataset.
3. It performs sentiment analysis on reviews to rank drugs.
4. Optionally upload a pill image for identification.

---

## 🧩 Modules Explained

| Module / Submodule           | Purpose                                                                         |
| ---------------------------- | ------------------------------------------------------------------------------- |
| **modules/data_processing/** | Data loading, cleaning, and feature engineering                                 |
| **modules/models/**          | Contains model training code and HuggingFace model directory (weights excluded) |
| **modules/recommendation/**  | Main drug recommendation engine                                                 |
| **modules/ui/**              | Streamlit frontend (chatbot, voice input, pill image upload)                    |
| **modules/utils/**           | Utility functions (logging, config, helpers)                                    |

---

## 📜 Notes

* Model weights (`.safetensors`, `.pt`, `.bin`) and large datasets are excluded from GitHub (use Hugging Face Hub, Google Drive, or Git LFS).
* Before running the app, ensure the model files are downloaded/placed in `modules/models/distilbert_drug_model/` if needed.
* Python version pinned to **3.11** for compatibility.

---

## 🤝 Contributing

Pull requests are welcome. Please open an issue first to discuss what you would like to change.


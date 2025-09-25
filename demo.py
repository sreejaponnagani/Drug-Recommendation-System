import joblib
encoder = joblib.load('models/label_encoder.pkl')
print(type(encoder))

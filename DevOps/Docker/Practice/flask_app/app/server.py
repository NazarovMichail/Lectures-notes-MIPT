from flask import Flask, request, jsonify
import joblib
import numpy as np


HOST = '0.0.0.0'
PORT = 80


app = Flask(__name__)
model = joblib.load('models/model.pkl')

@app.route("/")
def main_page():
    return "App is running!"

@app.route("/predict", methods=['POST'])
def predict():
    features = request.json
    features = np.array(features).reshape(1, 4)
    result = model.predict(features)
    result = result[0]

    return jsonify({'prediction':result})


if __name__ == "__main__":
    app.run(HOST, PORT)

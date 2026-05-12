from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import joblib

app = Flask(__name__)
CORS(app)

# Load ward data
with open('wards_data.json') as f:
    wards = json.load(f)

# Load XGBoost model
model = joblib.load('flood_model.pkl')

# Risk Level Function
def get_risk_level(score):

    if score > 120:
        return "HIGH"

    elif score >= 80:
        return "MEDIUM"

    else:
        return "LOW"

# Reason Generator
def generate_reason(elevation, water_distance):

    if elevation < 4 and water_distance < 0.5:
        return "Low elevation and very close to water"

    elif elevation < 5:
        return "Low elevation increases flood risk"

    elif water_distance < 0.5:
        return "Close to water body increases risk"

    else:
        return "Moderate conditions"

# HOME ROUTE
@app.route('/')
def home():

    rainfall = float(request.args.get('rainfall', 200))

    result = []

    for ward in wards:

        elevation = ward['elevation']
        water_distance = ward['water_distance']

        # XGBoost Prediction
        score = model.predict([
            [rainfall, elevation, water_distance]
        ])[0]

        # Convert float32 → float
        score = float(round(score, 2))

        level = get_risk_level(score)

        reason = generate_reason(
            elevation,
            water_distance
        )

        result.append({

            "ward_no": ward['ward_no'],

            "ward_name": f"Ward {ward['ward_no']}",

            "score": score,

            "level": level,

            "elevation": elevation,

            "water_distance": water_distance,

            "rainfall": rainfall,

            "reason": reason
        })

    return jsonify(result)

# API ROUTE
@app.route('/get-risk', methods=['GET'])
def get_risk():

    rainfall = request.args.get('rainfall')

    if rainfall is None:

        return jsonify({
            "error": "Rainfall required"
        }), 400

    try:

        rainfall = float(rainfall)

    except:

        return jsonify({
            "error": "Invalid rainfall"
        }), 400

    result = []

    for ward in wards:

        elevation = ward['elevation']
        water_distance = ward['water_distance']

        # XGBoost Prediction
        score = model.predict([
            [rainfall, elevation, water_distance]
        ])[0]

        # Convert float32 → float
        score = float(round(score, 2))

        level = get_risk_level(score)

        reason = generate_reason(
            elevation,
            water_distance
        )

        result.append({

            "ward_no": ward['ward_no'],

            "ward_name": f"Ward {ward['ward_no']}",

            "score": score,

            "level": level,

            "elevation": elevation,

            "water_distance": water_distance,

            "rainfall": rainfall,

            "reason": reason
        })

    return jsonify({
    "rainfall": rainfall,
    "wards": result
})
# Run Flask Server
if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000)
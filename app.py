from flask import Flask, render_template, request, jsonify
import json
import math
import os

app = Flask(__name__)

def load_db():
    try:
        with open('formulations.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        # Capture form data
        area = float(request.form.get('area', 1.0))
        unit = request.form.get('area_unit', 'Hectare')
        dosage = float(request.form.get('dosage', 0))
        water = float(request.form.get('water', 0))
        pump = float(request.form.get('pump', 20))
        
        # Core Calculation Logic
        # Total Product = Area * Dosage
        total_product = area * dosage
        
        # Total Water = Area * Water per unit
        total_water = area * water
        
        # Refills = (Water amount ÷ Pump size) × Area
        pump_refills = math.ceil(total_water / pump) if pump > 0 else 0
        
        # Dose per refill = Total product ÷ Pump refills
        dose_per_refill = total_product / pump_refills if pump_refills > 0 else 0
        
        results = {
            "total_product": round(total_product, 2),
            "pump_refills": pump_refills,
            "dose_per_refill": round(dose_per_refill, 2),
            "area": area,
            "unit": unit,
            "dosage": dosage,
            "water": water,
            "pump": pump
        }
        
    return render_template('index.html', results=results)

@app.route('/search_formulation')
def search_formulation():
    query = request.args.get('q', '').lower()
    db = load_db()
    
    if not query:
        return jsonify([])

    results = []
    # Search through keys (chemical names), names, and nested crops/pests
    for key, val in db.items():
        # Check if query matches the chemical name or any of its crops
        crop_match = any(query in crop.lower() for crop in val.get('options', {}).keys())
        
        if query in key or query in val['name'].lower() or crop_match:
           
            results.append(val)
    
    return jsonify(results[:5]) 

if __name__ == '__main__':
    app.run(debug=True)
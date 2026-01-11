# backend.py
from flask import Flask, request, jsonify
from advanced_fertilizer_calculator import AdvancedFertilizerCalculator
import json

app = Flask(__name__)
calculator = AdvancedFertilizerCalculator()

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    crop = data.get('crop')
    quantity = data.get('quantity')
    
    try:
        nutrients = calculator.calculate_nutrient_requirement(crop, quantity)
        fertilizers = calculator.calculate_basic_fertilizers(nutrients['total_kg'])
        costs = calculator.calculate_cost(fertilizers)
        
        return jsonify({
            'success': True,
            'nutrients': nutrients,
            'fertilizers': fertilizers,
            'costs': costs
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/crops', methods=['GET'])
def get_crops():
    categories = calculator.get_crop_categories()
    return jsonify(categories)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
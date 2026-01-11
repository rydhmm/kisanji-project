#!/usr/bin/env python3
"""
Advanced Fertilizer Calculator - With Complete Nutrient Analysis
Supports: N, P, K, Ca, Mg, S, Fe, Mn, Zn
Includes 100+ Indian crops
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class AdvancedFertilizerCalculator:
    def __init__(self, crop_db_path: str = "crop_database.json", 
                 fertilizer_db_path: str = "fertilizer_database.json"):
        """Initialize calculator with external JSON databases"""
        self.crop_db_path = crop_db_path
        self.fertilizer_db_path = fertilizer_db_path
        
        # Load databases
        self.crop_data = self._load_crop_database()
        self.fertilizer_data = self._load_fertilizer_database()
        
        # Nutrient list
        self.nutrients = ["N", "P", "K", "Ca", "Mg", "S", "Fe", "Mn", "Zn"]
        self.macronutrients = ["N", "P", "K"]
        self.secondary_nutrients = ["Ca", "Mg", "S"]
        self.micronutrients = ["Fe", "Mn", "Zn"]
    
    def _load_crop_database(self) -> Dict:
        """Load crop database from JSON file"""
        try:
            with open(self.crop_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded {len(data['crops'])} crops from database")
            return data['crops']
        except FileNotFoundError:
            print(f"❌ Error: {self.crop_db_path} not found!")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing {self.crop_db_path}: {e}")
            return {}
    
    def _load_fertilizer_database(self) -> Dict:
        """Load fertilizer database from JSON file"""
        try:
            with open(self.fertilizer_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded {len(data['fertilizers'])} fertilizers from database")
            return data['fertilizers']
        except FileNotFoundError:
            print(f"❌ Error: {self.fertilizer_db_path} not found!")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing {self.fertilizer_db_path}: {e}")
            return {}
    
    def get_crop_categories(self) -> Dict[str, List[str]]:
        """Get crops organized by category"""
        categories = {}
        for crop_id, crop_info in self.crop_data.items():
            category = crop_info.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'id': crop_id,
                'name': crop_info['name']
            })
        return categories
    
    def calculate_nutrient_requirement(self, crop: str, quantity: float, 
                                      unit_type: str = 'tree') -> Dict[str, Dict]:
        """
        Calculate complete nutrient requirements
        
        Args:
            crop: Crop ID (e.g., 'apple', 'rice')
            quantity: Number of trees/plants or hectares
            unit_type: 'tree', 'plant', or 'hectare'
        
        Returns:
            Dictionary with per_unit, total_g, and total_kg nutrients
        """
        if crop not in self.crop_data:
            raise ValueError(f"Crop '{crop}' not found in database")
        
        crop_info = self.crop_data[crop]
        
        # Determine nutrient source based on crop type
        if 'nutrients_per_tree_g' in crop_info:
            nutrients_per_unit = crop_info['nutrients_per_tree_g']
            unit_type = 'tree'
        elif 'nutrients_per_plant_g' in crop_info:
            nutrients_per_unit = crop_info['nutrients_per_plant_g']
            unit_type = 'plant'
        elif 'nutrients_per_hectare_kg' in crop_info:
            nutrients_per_unit = crop_info['nutrients_per_hectare_kg']
            unit_type = 'hectare'
        else:
            raise ValueError(f"No nutrient data found for {crop}")
        
        # Calculate total requirements
        total_nutrients_g = {}
        total_nutrients_kg = {}
        
        for nutrient in self.nutrients:
            if nutrient in nutrients_per_unit:
                if unit_type == 'hectare':
                    # Already in kg for hectare
                    total_kg = nutrients_per_unit[nutrient] * quantity
                    total_g = total_kg * 1000
                else:
                    # Convert grams to kg
                    total_g = nutrients_per_unit[nutrient] * quantity
                    total_kg = total_g / 1000
                
                total_nutrients_g[nutrient] = round(total_g, 2)
                total_nutrients_kg[nutrient] = round(total_kg, 3)
            else:
                total_nutrients_g[nutrient] = 0
                total_nutrients_kg[nutrient] = 0
        
        return {
            "per_unit": nutrients_per_unit,
            "unit_type": unit_type,
            "quantity": quantity,
            "total_g": total_nutrients_g,
            "total_kg": total_nutrients_kg
        }
    
    def calculate_basic_fertilizers(self, nutrients_kg: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate basic fertilizer combination (Urea + DAP + MOP + Micronutrients)
        """
        results = {}
        
        # DAP for Phosphorus (also provides some Nitrogen)
        if nutrients_kg.get('P', 0) > 0:
            dap_percent = self.fertilizer_data['dap']['composition_percent']
            dap_amount = nutrients_kg['P'] / (dap_percent['P'] / 100)
            n_from_dap = dap_amount * (dap_percent['N'] / 100)
            results['DAP'] = round(dap_amount, 3)
        else:
            n_from_dap = 0
            results['DAP'] = 0
        
        # MOP for Potassium
        if nutrients_kg.get('K', 0) > 0:
            mop_percent = self.fertilizer_data['mop']['composition_percent']
            mop_amount = nutrients_kg['K'] / (mop_percent['K'] / 100)
            results['MOP'] = round(mop_amount, 3)
        else:
            results['MOP'] = 0
        
        # Urea for remaining Nitrogen
        remaining_n = max(0, nutrients_kg.get('N', 0) - n_from_dap)
        if remaining_n > 0:
            urea_percent = self.fertilizer_data['urea']['composition_percent']
            urea_amount = remaining_n / (urea_percent['N'] / 100)
            results['Urea'] = round(urea_amount, 3)
        else:
            results['Urea'] = 0
        
        # SSP for Calcium and Sulfur (secondary nutrients)
        if nutrients_kg.get('Ca', 0) > 0 or nutrients_kg.get('S', 0) > 0:
            ssp_percent = self.fertilizer_data['ssp']['composition_percent']
            # Calculate based on which is limiting
            ssp_for_ca = nutrients_kg.get('Ca', 0) / (ssp_percent['Ca'] / 100) if ssp_percent['Ca'] > 0 else 0
            ssp_for_s = nutrients_kg.get('S', 0) / (ssp_percent['S'] / 100) if ssp_percent['S'] > 0 else 0
            ssp_amount = max(ssp_for_ca, ssp_for_s)
            if ssp_amount > 0:
                results['SSP'] = round(ssp_amount, 3)
        
        # Magnesium Sulfate for Magnesium
        if nutrients_kg.get('Mg', 0) > 0:
            mg_sulf_percent = self.fertilizer_data['magnesium_sulfate']['composition_percent']
            mg_amount = nutrients_kg['Mg'] / (mg_sulf_percent['Mg'] / 100)
            results['Magnesium_Sulfate'] = round(mg_amount, 3)
        
        # Micronutrients
        micronutrient_needed = False
        for micro in self.micronutrients:
            if nutrients_kg.get(micro, 0) > 0:
                micronutrient_needed = True
                break
        
        if micronutrient_needed:
            # Use individual micronutrient fertilizers
            if nutrients_kg.get('Fe', 0) > 0:
                fe_percent = self.fertilizer_data['ferrous_sulfate']['composition_percent']
                fe_amount = nutrients_kg['Fe'] / (fe_percent['Fe'] / 100)
                results['Ferrous_Sulfate'] = round(fe_amount, 3)
            
            if nutrients_kg.get('Mn', 0) > 0:
                mn_percent = self.fertilizer_data['manganese_sulfate']['composition_percent']
                mn_amount = nutrients_kg['Mn'] / (mn_percent['Mn'] / 100)
                results['Manganese_Sulfate'] = round(mn_amount, 3)
            
            if nutrients_kg.get('Zn', 0) > 0:
                zn_percent = self.fertilizer_data['zinc_sulfate']['composition_percent']
                zn_amount = nutrients_kg['Zn'] / (zn_percent['Zn'] / 100)
                results['Zinc_Sulfate'] = round(zn_amount, 3)
        
        return results
    
    def calculate_cost(self, fertilizers: Dict[str, float]) -> Dict[str, float]:
        """Calculate total cost based on fertilizer amounts"""
        costs = {}
        total_cost = 0
        
        # Mapping of fertilizer names to database keys
        fert_mapping = {
            'DAP': 'dap',
            'MOP': 'mop',
            'Urea': 'urea',
            'SSP': 'ssp',
            'Magnesium_Sulfate': 'magnesium_sulfate',
            'Ferrous_Sulfate': 'ferrous_sulfate',
            'Manganese_Sulfate': 'manganese_sulfate',
            'Zinc_Sulfate': 'zinc_sulfate',
            'NPK': 'npk_19_19_19'
        }
        
        for fert_name, amount in fertilizers.items():
            if amount > 0:
                db_key = fert_mapping.get(fert_name, fert_name.lower())
                if db_key in self.fertilizer_data:
                    price_per_kg = self.fertilizer_data[db_key].get('price_per_kg_inr', 0)
                    cost = amount * price_per_kg
                    costs[fert_name] = round(cost, 2)
                    total_cost += cost
        
        costs['TOTAL'] = round(total_cost, 2)
        return costs
    
    def print_detailed_results(self, crop: str, quantity: float, 
                              nutrients: Dict, fertilizers: Dict[str, float],
                              costs: Optional[Dict[str, float]] = None):
        """Print comprehensive formatted results"""
        crop_info = self.crop_data[crop]
        
        print("\n" + "="*80)
        print(f"{'COMPLETE FERTILIZER ANALYSIS':^80}")
        print("="*80)
        
        print(f"\n{'CROP INFORMATION':-^80}")
        print(f"  Crop: {crop_info['name']}")
        print(f"  Category: {crop_info.get('category', 'N/A').title()}")
        print(f"  Quantity: {quantity} {nutrients['unit_type']}(s)")
        
        print(f"\n{'PRIMARY MACRONUTRIENTS (NPK)':-^80}")
        for nutrient in self.macronutrients:
            per_unit = nutrients['per_unit'].get(nutrient, 0)
            total_kg = nutrients['total_kg'].get(nutrient, 0)
            print(f"  {nutrient} - Nitrogen:" if nutrient == 'N' else 
                  f"  {nutrient} - Phosphorus:" if nutrient == 'P' else
                  f"  {nutrient} - Potassium:", end="")
            print(f" {per_unit:>8}g/{nutrients['unit_type']:>7} × {quantity:>6} = {total_kg:>8.3f} kg")
        
        print(f"\n{'SECONDARY NUTRIENTS':-^80}")
        for nutrient in self.secondary_nutrients:
            per_unit = nutrients['per_unit'].get(nutrient, 0)
            total_kg = nutrients['total_kg'].get(nutrient, 0)
            print(f"  {nutrient} - Calcium:" if nutrient == 'Ca' else
                  f"  {nutrient} - Magnesium:" if nutrient == 'Mg' else
                  f"  {nutrient} - Sulfur:", end="")
            print(f" {per_unit:>8}g/{nutrients['unit_type']:>7} × {quantity:>6} = {total_kg:>8.3f} kg")
        
        print(f"\n{'MICRONUTRIENTS':-^80}")
        for nutrient in self.micronutrients:
            per_unit = nutrients['per_unit'].get(nutrient, 0)
            total_kg = nutrients['total_kg'].get(nutrient, 0)
            print(f"  {nutrient} - Iron:" if nutrient == 'Fe' else
                  f"  {nutrient} - Manganese:" if nutrient == 'Mn' else
                  f"  {nutrient} - Zinc:", end="")
            print(f" {per_unit:>8}g/{nutrients['unit_type']:>7} × {quantity:>6} = {total_kg:>8.3f} kg")
        
        print(f"\n{'RECOMMENDED FERTILIZERS (Annual)':-^80}")
        total_weight = 0
        for fert_name, amount in fertilizers.items():
            if amount > 0:
                print(f"  {fert_name.replace('_', ' '):<30} {amount:>10.3f} kg")
                total_weight += amount
        print(f"  {'-'*40}")
        print(f"  {'TOTAL FERTILIZER WEIGHT':<30} {total_weight:>10.3f} kg")
        
        if costs:
            print(f"\n{'ESTIMATED COST (₹)':-^80}")
            for fert_name, cost in costs.items():
                if fert_name != 'TOTAL' and cost > 0:
                    print(f"  {fert_name.replace('_', ' '):<30} ₹{cost:>10.2f}")
            print(f"  {'-'*40}")
            print(f"  {'TOTAL COST':<30} ₹{costs['TOTAL']:>10.2f}")
        
        print(f"\n{'APPLICATION SCHEDULE':-^80}")
        print("  Split into 3-4 applications during the year:")
        print("  • Application 1 (Early Growth):    30% of total")
        print("  • Application 2 (Active Growth):   30% of total")
        print("  • Application 3 (Reproductive):    25% of total")
        print("  • Application 4 (Maintenance):     15% of total")
        
        print("\n" + "="*80)
        print("Note: Adjust based on soil test results and crop stage")
        print("="*80 + "\n")


def main():
    """Main function to run the advanced calculator"""
    
    # Check if database files exist
    if not os.path.exists("crop_database.json"):
        print("❌ Error: crop_database.json not found!")
        print("Please ensure the database files are in the same directory.")
        return
    
    if not os.path.exists("fertilizer_database.json"):
        print("❌ Error: fertilizer_database.json not found!")
        print("Please ensure the database files are in the same directory.")
        return
    
    print("\n" + "="*80)
    print(f"{'ADVANCED FERTILIZER CALCULATOR':^80}")
    print(f"{'with Complete Nutrient Analysis (N, P, K, Ca, Mg, S, Fe, Mn, Zn)':^80}")
    print("="*80 + "\n")
    
    # Initialize calculator
    calculator = AdvancedFertilizerCalculator()
    
    if not calculator.crop_data:
        print("❌ Failed to load crop database. Exiting.")
        return
    
    # Get crop categories
    categories = calculator.get_crop_categories()
    
    print(f"\nAvailable Crop Categories ({len(categories)} categories):")
    for idx, (category, crops) in enumerate(sorted(categories.items()), 1):
        print(f"  {idx}. {category.upper().replace('_', ' '):<20} ({len(crops)} crops)")
    
    # Category selection
    while True:
        try:
            cat_choice = input("\nEnter category number or name (or 'all' to see all crops): ").strip().lower()
            
            if cat_choice == 'all':
                selected_category = None
                break
            elif cat_choice.isdigit():
                cat_idx = int(cat_choice) - 1
                cat_list = sorted(list(categories.keys()))
                if 0 <= cat_idx < len(cat_list):
                    selected_category = cat_list[cat_idx]
                    break
            elif cat_choice in categories:
                selected_category = cat_choice
                break
            
            print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error: {e}. Please try again.")
    
    # Display crops
    if selected_category:
        print(f"\nCrops in {selected_category.upper().replace('_', ' ')}:")
        crop_list = categories[selected_category]
    else:
        print("\nAll Available Crops:")
        crop_list = []
        for cat_crops in categories.values():
            crop_list.extend(cat_crops)
    
    for idx, crop in enumerate(sorted(crop_list, key=lambda x: x['name']), 1):
        print(f"  {idx:3d}. {crop['name']:<30} ({crop['id']})")
    
    # Crop selection
    while True:
        try:
            crop_input = input("\nEnter crop name or number: ").strip().lower()
            
            if crop_input.isdigit():
                crop_idx = int(crop_input) - 1
                sorted_list = sorted(crop_list, key=lambda x: x['name'])
                if 0 <= crop_idx < len(sorted_list):
                    crop = sorted_list[crop_idx]['id']
                    break
            elif crop_input in calculator.crop_data:
                crop = crop_input
                break
            else:
                print("Invalid crop. Please try again.")
        except Exception as e:
            print(f"Error: {e}. Please try again.")
    
    # Quantity input
    crop_info = calculator.crop_data[crop]
    
    # Determine unit type
    if 'nutrients_per_tree_g' in crop_info:
        unit_name = "trees"
    elif 'nutrients_per_plant_g' in crop_info:
        unit_name = "plants"
    else:
        unit_name = "hectares"
    
    while True:
        try:
            quantity = float(input(f"Enter number of {unit_name}: ").strip())
            if quantity > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Calculate requirements
    print("\n⏳ Calculating nutrient requirements...")
    nutrients = calculator.calculate_nutrient_requirement(crop, quantity)
    
    print("⏳ Calculating fertilizer recommendations...")
    fertilizers = calculator.calculate_basic_fertilizers(nutrients['total_kg'])
    
    print("⏳ Calculating costs...")
    costs = calculator.calculate_cost(fertilizers)
    
    # Display results
    calculator.print_detailed_results(crop, quantity, nutrients, fertilizers, costs)
    
    # Save option
    save = input("Would you like to save results to a file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"fertilizer_report_{crop}_{int(quantity)}{unit_name}.json"
        results_data = {
            "crop": crop_info['name'],
            "crop_id": crop,
            "quantity": quantity,
            "unit_type": nutrients['unit_type'],
            "nutrient_requirements": nutrients,
            "fertilizer_recommendations": fertilizers,
            "estimated_costs_inr": costs,
            "total_cost_inr": costs['TOTAL']
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Results saved to: {filename}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Calculation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

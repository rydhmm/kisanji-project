#!/usr/bin/env python3
"""
Pesticide Calculator - Spray Dosage Calculator
Supports 99 pesticides (Insecticides, Fungicides, Herbicides, Acaricides)

Author: Saurav Beri (@sauravberi16)
Role: Backend Developer - API & Calculator Logic
"""

import json
import math
from typing import Dict, List, Optional, Any
from pathlib import Path


class PesticideCalculator:
    def __init__(self, formulations_path: str = "formulations.json"):
        """Initialize calculator with formulations database"""
        self.formulations_path = formulations_path
        self.formulations = self._load_database()
        
    def _load_database(self) -> Dict:
        """Load formulations database from JSON file"""
        try:
            with open(self.formulations_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded {len(data)} pesticides from database")
            return data
        except FileNotFoundError:
            print(f"❌ Error: {self.formulations_path} not found!")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing {self.formulations_path}: {e}")
            return {}
    
    def get_all_pesticides(self) -> List[Dict]:
        """Get list of all pesticides with basic info"""
        pesticides = []
        for key, val in self.formulations.items():
            pesticides.append({
                "id": key,
                "name": val["name"],
                "type": val["type"],
                "crops": list(val.get("options", {}).keys())
            })
        return pesticides
    
    def get_pesticides_by_type(self) -> Dict[str, List[Dict]]:
        """Get pesticides organized by type"""
        by_type = {
            "Insecticide": [],
            "Fungicide": [],
            "Herbicide": [],
            "Acaricide": []
        }
        
        for key, val in self.formulations.items():
            pest_type = val.get("type", "Other")
            if pest_type not in by_type:
                by_type[pest_type] = []
            by_type[pest_type].append({
                "id": key,
                "name": val["name"],
                "crops": list(val.get("options", {}).keys())
            })
        
        return by_type
    
    def get_crops_list(self) -> List[str]:
        """Get list of all unique crops"""
        crops = set()
        for val in self.formulations.values():
            crops.update(val.get("options", {}).keys())
        return sorted(list(crops))
    
    def get_pesticides_for_crop(self, crop: str) -> List[Dict]:
        """Get all pesticides available for a specific crop"""
        results = []
        crop_lower = crop.lower()
        
        for key, val in self.formulations.items():
            for crop_name, pests in val.get("options", {}).items():
                if crop_lower in crop_name.lower():
                    results.append({
                        "id": key,
                        "name": val["name"],
                        "type": val["type"],
                        "crop": crop_name,
                        "pests": list(pests.keys())
                    })
                    break
        
        return results
    
    def get_pests_for_pesticide(self, pesticide_id: str, crop: str = None) -> List[Dict]:
        """Get pests that a pesticide can treat"""
        if pesticide_id not in self.formulations:
            return []
        
        pesticide = self.formulations[pesticide_id]
        results = []
        
        for crop_name, pests in pesticide.get("options", {}).items():
            if crop and crop.lower() not in crop_name.lower():
                continue
            for pest_name, details in pests.items():
                results.append({
                    "crop": crop_name,
                    "pest": pest_name,
                    "dosage_ml_per_hectare": details["dosage"],
                    "water_liters_per_hectare": details["water"],
                    "phi_days": details["phi"]  # Pre-Harvest Interval
                })
        
        return results
    
    def search_pesticides(self, query: str) -> List[Dict]:
        """Search pesticides by name, crop, or pest"""
        query = query.lower()
        results = []
        
        for key, val in self.formulations.items():
            # Check name
            if query in key or query in val["name"].lower():
                results.append({
                    "id": key,
                    "name": val["name"],
                    "type": val["type"],
                    "crops": list(val.get("options", {}).keys()),
                    "match_type": "name"
                })
                continue
            
            # Check crops
            crop_match = any(query in crop.lower() for crop in val.get("options", {}).keys())
            if crop_match:
                results.append({
                    "id": key,
                    "name": val["name"],
                    "type": val["type"],
                    "crops": list(val.get("options", {}).keys()),
                    "match_type": "crop"
                })
                continue
            
            # Check pests
            for crop_name, pests in val.get("options", {}).items():
                if any(query in pest.lower() for pest in pests.keys()):
                    results.append({
                        "id": key,
                        "name": val["name"],
                        "type": val["type"],
                        "crops": list(val.get("options", {}).keys()),
                        "match_type": "pest"
                    })
                    break
        
        return results[:10]  # Limit to 10 results
    
    def calculate_spray(
        self, 
        pesticide_id: str,
        crop: str,
        pest: str,
        area: float,
        area_unit: str = "hectare",
        pump_capacity: float = 16.0,
        custom_dosage: float = None,
        custom_water: float = None
    ) -> Dict[str, Any]:
        """
        Calculate pesticide spray requirements
        
        Args:
            pesticide_id: ID of the pesticide
            crop: Target crop
            pest: Target pest
            area: Field area
            area_unit: 'hectare' or 'acre'
            pump_capacity: Spray pump capacity in liters (default 16L)
            custom_dosage: Override dosage (ml per hectare)
            custom_water: Override water requirement (liters per hectare)
            
        Returns:
            Dictionary with calculation results
        """
        if pesticide_id not in self.formulations:
            raise ValueError(f"Pesticide '{pesticide_id}' not found")
        
        pesticide = self.formulations[pesticide_id]
        
        # Find the crop and pest
        dosage = None
        water = None
        phi = None
        
        for crop_name, pests in pesticide.get("options", {}).items():
            if crop.lower() in crop_name.lower():
                for pest_name, details in pests.items():
                    if pest.lower() in pest_name.lower():
                        dosage = details["dosage"]
                        water = details["water"]
                        phi = details["phi"]
                        break
                if dosage:
                    break
        
        if not dosage and not custom_dosage:
            raise ValueError(f"No dosage found for {crop}/{pest} combination")
        
        # Use custom values if provided
        dosage = custom_dosage if custom_dosage else dosage
        water = custom_water if custom_water else (water or 200)
        
        # Convert acres to hectares if needed
        area_hectares = area if area_unit.lower() == "hectare" else area * 0.4047
        
        # Core calculations
        total_product_ml = area_hectares * dosage
        total_water_liters = area_hectares * water
        pump_refills = math.ceil(total_water_liters / pump_capacity) if pump_capacity > 0 else 0
        dose_per_refill_ml = total_product_ml / pump_refills if pump_refills > 0 else 0
        
        return {
            "pesticide": {
                "id": pesticide_id,
                "name": pesticide["name"],
                "type": pesticide["type"]
            },
            "target": {
                "crop": crop,
                "pest": pest
            },
            "input": {
                "area": area,
                "area_unit": area_unit,
                "area_hectares": round(area_hectares, 3),
                "pump_capacity_liters": pump_capacity
            },
            "dosage": {
                "ml_per_hectare": dosage,
                "water_liters_per_hectare": water,
                "phi_days": phi
            },
            "calculation": {
                "total_product_ml": round(total_product_ml, 2),
                "total_product_liters": round(total_product_ml / 1000, 3),
                "total_water_liters": round(total_water_liters, 2),
                "pump_refills": pump_refills,
                "dose_per_refill_ml": round(dose_per_refill_ml, 2)
            },
            "safety": {
                "pre_harvest_interval_days": phi,
                "message": f"Wait {phi} days after spraying before harvesting" if phi else "Follow label instructions"
            }
        }
    
    def get_pesticide_details(self, pesticide_id: str) -> Optional[Dict]:
        """Get detailed information about a pesticide"""
        if pesticide_id not in self.formulations:
            return None
        
        pesticide = self.formulations[pesticide_id]
        
        crops_pests = []
        for crop_name, pests in pesticide.get("options", {}).items():
            for pest_name, details in pests.items():
                crops_pests.append({
                    "crop": crop_name,
                    "pest": pest_name,
                    "dosage_ml": details["dosage"],
                    "water_liters": details["water"],
                    "phi_days": details["phi"]
                })
        
        return {
            "id": pesticide_id,
            "name": pesticide["name"],
            "type": pesticide["type"],
            "applications": crops_pests
        }


# Singleton instance
_calculator = None

def get_pesticide_calculator() -> PesticideCalculator:
    """Get or create PesticideCalculator instance"""
    global _calculator
    if _calculator is None:
        from pathlib import Path
        db_path = Path(__file__).parent / "formulations.json"
        _calculator = PesticideCalculator(str(db_path))
    return _calculator


if __name__ == "__main__":
    # Test the calculator
    calc = PesticideCalculator()
    
    print("\n=== Pesticide Types ===")
    by_type = calc.get_pesticides_by_type()
    for ptype, pesticides in by_type.items():
        print(f"{ptype}: {len(pesticides)} pesticides")
    
    print("\n=== All Crops ===")
    crops = calc.get_crops_list()
    print(f"{len(crops)} crops: {', '.join(crops)}")
    
    print("\n=== Search 'rice' ===")
    results = calc.search_pesticides("rice")
    for r in results[:3]:
        print(f"  - {r['name']} ({r['type']})")
    
    print("\n=== Calculate Spray ===")
    try:
        result = calc.calculate_spray(
            pesticide_id="tricyclazole 75 wp",
            crop="Rice",
            pest="Blast",
            area=2.5,
            area_unit="hectare",
            pump_capacity=16
        )
        print(f"  Total Product: {result['calculation']['total_product_ml']} ml")
        print(f"  Total Water: {result['calculation']['total_water_liters']} L")
        print(f"  Pump Refills: {result['calculation']['pump_refills']}")
        print(f"  Dose per Refill: {result['calculation']['dose_per_refill_ml']} ml")
    except Exception as e:
        print(f"  Error: {e}")

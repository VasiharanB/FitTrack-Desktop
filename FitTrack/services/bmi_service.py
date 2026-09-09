import math
from typing import Dict, Any, Tuple

class BMIService:
    """Provides business logic for calculating BMI, classifications, healthy weight ranges, BMR, BSA, and dietary suggestions."""

    @staticmethod
    def calculate_bmi(height_cm: float, weight_kg: float) -> float:
        """Calculates BMI from height (cm) and weight (kg).
        
        Formula: weight (kg) / (height (m) ^ 2)
        """
        if height_cm <= 0:
            raise ValueError("Height must be positive and non-zero.")
        if weight_kg <= 0:
            raise ValueError("Weight must be positive and non-zero.")
            
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 2)

    @staticmethod
    def classify_bmi(bmi: float) -> str:
        """Classifies the BMI value into a category using WHO standard ranges."""
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25.0:
            return "Normal"
        elif 25.0 <= bmi < 30.0:
            return "Overweight"
        else:
            return "Obese"

    @staticmethod
    def get_healthy_weight_range(height_cm: float) -> Tuple[float, float]:
        """Calculates the healthy weight range (kg) for a given height using BMI limits 18.5 and 24.9."""
        height_m = height_cm / 100.0
        min_weight = 18.5 * (height_m ** 2)
        max_weight = 24.9 * (height_m ** 2)
        return round(min_weight, 1), round(max_weight, 1)

    @staticmethod
    def calculate_bmr(height_cm: float, weight_kg: float, age: float = 25, gender: str = "Male") -> int:
        """Calculates Basal Metabolic Rate (BMR) in kcal/day using Mifflin-St Jeor formula."""
        if height_cm <= 0 or weight_kg <= 0 or age <= 0:
            return 0
        base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
        if str(gender).strip().lower() == "female":
            bmr = base - 161
        else:
            bmr = base + 5
        return max(500, int(round(bmr)))

    @staticmethod
    def calculate_bsa(height_cm: float, weight_kg: float) -> float:
        """Calculates Body Surface Area (BSA) in m² using Mosteller formula."""
        if height_cm <= 0 or weight_kg <= 0:
            return 0.0
        bsa = math.sqrt((height_cm * weight_kg) / 3600.0)
        return round(bsa, 2)

    @classmethod
    def calculate_target_delta(cls, height_cm: float, weight_kg: float) -> Tuple[float, str]:
        """Calculates distance in kg to optimal midpoint healthy weight (BMI 21.7)."""
        min_w, max_w = cls.get_healthy_weight_range(height_cm)
        mid_w = round((min_w + max_w) / 2.0, 1)
        delta = round(weight_kg - mid_w, 1)
        if abs(delta) <= 1.0:
            sign_str = "Optimal"
        elif delta > 0:
            sign_str = f"+{delta:.1f} kg"
        else:
            sign_str = f"{delta:.1f} kg"
        return mid_w, sign_str

    @classmethod
    def get_suggestion_and_details(
        cls, height_cm: float, weight_kg: float, age: float = 25, gender: str = "Male"
    ) -> Dict[str, Any]:
        """Runs the entire BMI & biometric telemetry analysis pipeline."""
        bmi = cls.calculate_bmi(height_cm, weight_kg)
        status = cls.classify_bmi(bmi)
        min_w, max_w = cls.get_healthy_weight_range(height_cm)
        mid_w, delta_str = cls.calculate_target_delta(height_cm, weight_kg)
        bmr = cls.calculate_bmr(height_cm, weight_kg, age, gender)
        bsa = cls.calculate_bsa(height_cm, weight_kg)
        
        suggestions = {
            "Underweight": "Hyper-caloric nutrient dense intake recommended. Focus on complex carbs, healthy lipids, and lean proteins. Progressive strength training advised.",
            "Normal": "Bio-metrics optimal. Maintain balanced caloric equilibrium, sustained cardiovascular exercise, and regular biometric tracking.",
            "Overweight": "Moderate caloric deficit recommended. Increase dietary fiber, optimize protein pacing, and target 180+ min/week active cardiovascular load.",
            "Obese": "Clinical guidance recommended. Structured lifestyle intervention targeting sustained fat loss, glycemic regulation, and joint-friendly resistance activity."
        }
        
        return {
            "bmi": bmi,
            "status": status,
            "min_weight": min_w,
            "max_weight": max_w,
            "ideal_weight": mid_w,
            "delta_str": delta_str,
            "bmr": bmr,
            "bsa": bsa,
            "suggestion": suggestions.get(status, "Maintain a balanced lifestyle.")
        }


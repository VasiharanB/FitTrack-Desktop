class ValidationError(Exception):
    """Custom exception raised when health record input parameters fail validation."""
    pass

class InputValidator:
    """Validator class to check type and range requirements for FitTrack data fields."""

    @staticmethod
    def validate_inputs(name: str, age_str: str, height_str: str, weight_str: str, gender: str) -> dict:
        """Validates all inputs for a health record.
        
        Args:
            name: The person's name string.
            age_str: The age as string input.
            height_str: The height in cm as string input.
            weight_str: The weight in kg as string input.
            gender: Selected gender from the UI (Male/Female).
            
        Returns:
            A dictionary containing parsed, clean, and casted types:
            {"name": str, "age": int, "height": float, "weight": float, "gender": str}
            
        Raises:
            ValidationError: If any of the validations fail.
        """
        # Trim whitespace
        name = name.strip() if name else ""
        gender = gender.strip() if gender else ""
        age_str = age_str.strip() if age_str else ""
        height_str = height_str.strip() if height_str else ""
        weight_str = weight_str.strip() if weight_str else ""

        # Validate presence
        if not name:
            raise ValidationError("Name field is required.")
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters long.")
        if not gender or gender not in ["Male", "Female"]:
            raise ValidationError("Gender must be selected ('Male' or 'Female').")
        if not age_str:
            raise ValidationError("Age field is required.")
        if not height_str:
            raise ValidationError("Height field is required.")
        if not weight_str:
            raise ValidationError("Weight field is required.")

        # Numeric conversions
        try:
            age = int(age_str)
        except ValueError:
            raise ValidationError("Age must be a valid whole number (e.g. 25).")

        try:
            height = float(height_str)
        except ValueError:
            raise ValidationError("Height must be a valid decimal number (e.g. 175.5).")

        try:
            weight = float(weight_str)
        except ValueError:
            raise ValidationError("Weight must be a valid decimal number (e.g. 70.2).")

        # Range bounds validation
        if not (1 <= age <= 120):
            raise ValidationError("Age must be between 1 and 120 years.")
            
        if not (50.0 <= height <= 250.0):
            raise ValidationError("Height must be between 50.0 and 250.0 cm.")
            
        if not (10.0 <= weight <= 300.0):
            raise ValidationError("Weight must be between 10.0 and 300.0 kg.")

        return {
            "name": name,
            "age": age,
            "height": height,
            "weight": weight,
            "gender": gender
        }

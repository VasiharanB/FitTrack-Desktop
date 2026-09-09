from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, Union

@dataclass
class HealthRecord:
    """Represents a single health and BMI record in FitTrack."""
    id: Optional[int]
    name: str
    age: int
    gender: str
    height: float  # Height in cm
    weight: float  # Weight in kg
    bmi: float     # Calculated Body Mass Index
    status: str    # BMI category (e.g., Normal, Underweight, Overweight, Obese)
    created_at: str  # ISO timestamp of record creation

    def to_dict(self) -> Dict[str, Any]:
        """Converts the HealthRecord instance to a dictionary."""
        return asdict(self)

    @classmethod
    def from_row(cls, row: Union[tuple, list, Any]) -> "HealthRecord":
        """Creates a HealthRecord instance from a database row tuple/list."""
        if row is None or len(row) < 9:
            raise ValueError(f"Invalid database row tuple for HealthRecord: {row}")
        return cls(
            id=int(row[0]) if row[0] is not None else None,
            name=str(row[1]),
            age=int(row[2]),
            gender=str(row[3]),
            height=float(row[4]),
            weight=float(row[5]),
            bmi=float(row[6]),
            status=str(row[7]),
            created_at=str(row[8])
        )

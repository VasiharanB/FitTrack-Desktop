import csv
from typing import List
from models.person import HealthRecord

class ExportService:
    """Handles exporting health record database objects to standard formats."""

    @staticmethod
    def export_to_csv(filepath: str, records: List[HealthRecord]) -> None:
        """Writes health records list to a CSV file.
        
        Args:
            filepath: Path of the file to save (provided by a save dialog in UI).
            records: List of HealthRecord dataclass instances to export.
        """
        headers = [
            "Record ID", 
            "Name", 
            "Age", 
            "Gender", 
            "Height (cm)", 
            "Weight (kg)", 
            "BMI", 
            "Status", 
            "Created Date"
        ]

        with open(filepath, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)
            for rec in records:
                writer.writerow([
                    rec.id,
                    rec.name,
                    rec.age,
                    rec.gender,
                    rec.height,
                    rec.weight,
                    rec.bmi,
                    rec.status,
                    rec.created_at
                ])

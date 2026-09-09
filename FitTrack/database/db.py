import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from models.person import HealthRecord

class DatabaseManager:
    """Manages SQLite database connections and CRUD operations for health records.
    
    Guarantees that database connections are always closed via finally blocks,
    preventing file locking issues on concurrent or repeated operations.
    """
    
    def __init__(self, db_path: Optional[Union[Path, str]] = None):
        if db_path is None:
            # Store the database inside the database/ folder by default
            db_dir = Path(__file__).parent.resolve()
            self.db_path = db_dir / "fittrack.db"
        else:
            self.db_path = Path(db_path)
            
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Establishes and returns a connection to the SQLite database."""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        """Creates the health_records table if it doesn't already exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    gender TEXT NOT NULL,
                    height REAL NOT NULL,
                    weight REAL NOT NULL,
                    bmi REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def add_record(self, record: HealthRecord) -> int:
        """Inserts a new health record into the database.
        
        Returns:
            The auto-generated ID of the inserted record.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO health_records (name, age, gender, height, weight, bmi, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.name,
                record.age,
                record.gender,
                record.height,
                record.weight,
                record.bmi,
                record.status,
                record.created_at
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def update_record(self, record: HealthRecord):
        """Updates an existing health record in the database."""
        if record.id is None:
            raise ValueError("Cannot update a record without a valid ID.")
            
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE health_records
                SET name = ?, age = ?, gender = ?, height = ?, weight = ?, bmi = ?, status = ?, created_at = ?
                WHERE id = ?
            """, (
                record.name,
                record.age,
                record.gender,
                record.height,
                record.weight,
                record.bmi,
                record.status,
                record.created_at,
                record.id
            ))
            conn.commit()
        finally:
            conn.close()

    def delete_record(self, record_id: int):
        """Deletes a health record by its ID."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM health_records WHERE id = ?", (record_id,))
            conn.commit()
        finally:
            conn.close()

    def get_record_by_id(self, record_id: int) -> Optional[HealthRecord]:
        """Retrieves a single health record by its ID."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, age, gender, height, weight, bmi, status, created_at 
                FROM health_records 
                WHERE id = ?
            """, (record_id,))
            row = cursor.fetchone()
            return HealthRecord.from_row(row) if row else None
        finally:
            conn.close()

    def get_all_records(self) -> List[HealthRecord]:
        """Retrieves all health records, ordered by creation date descending."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, age, gender, height, weight, bmi, status, created_at 
                FROM health_records 
                ORDER BY created_at DESC, id DESC
            """)
            rows = cursor.fetchall()
            return [HealthRecord.from_row(row) for row in rows]
        finally:
            conn.close()

    def search_records_by_name(self, query: str) -> List[HealthRecord]:
        """Searches for health records matching the name query (case-insensitive)."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, age, gender, height, weight, bmi, status, created_at 
                FROM health_records 
                WHERE name LIKE ? COLLATE NOCASE
                ORDER BY created_at DESC, id DESC
            """, (f"%{query.strip()}%",))
            rows = cursor.fetchall()
            return [HealthRecord.from_row(row) for row in rows]
        finally:
            conn.close()

    def get_statistics(self) -> Dict[str, Any]:
        """Calculates and returns summary statistics for all stored records."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), AVG(bmi), MAX(bmi), MIN(bmi) FROM health_records")
            row = cursor.fetchone()
            
            total = row[0] if row and row[0] is not None else 0
            avg_bmi = round(row[1], 2) if row and row[1] is not None else 0.0
            max_bmi = round(row[2], 2) if row and row[2] is not None else 0.0
            min_bmi = round(row[3], 2) if row and row[3] is not None else 0.0
            
            return {
                "total": total,
                "avg_bmi": avg_bmi,
                "max_bmi": max_bmi,
                "min_bmi": min_bmi
            }
        finally:
            conn.close()
            
    def get_history_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Retrieves chronological BMI history for a specific person's name (case-insensitive)."""
        if not name or not name.strip():
            return []
            
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT created_at, bmi 
                FROM health_records 
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) 
                ORDER BY created_at ASC, id ASC
            """, (name.strip(),))
            rows = cursor.fetchall()
            return [{"date": row[0], "bmi": row[1]} for row in rows]
        finally:
            conn.close()

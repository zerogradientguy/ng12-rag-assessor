import json
from pathlib import Path
from typing import Dict, Any
from app.schemas.models import PatientData


class PatientDataStore:
    def __init__(self, data_path: str = "./app/data/patients.json"):
        self.data_path = Path(data_path)
        self.patients: Dict[str, PatientData] = {}
        self._load_patients()

    def _load_patients(self):
        """Load patient data from JSON file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Patient data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        for patient_dict in data:
            patient = PatientData(**patient_dict)
            self.patients[patient.patient_id] = patient

    def get_patient(self, patient_id: str) -> PatientData:
        """Get patient data by ID."""
        if patient_id not in self.patients:
            raise ValueError(f"Patient not found: {patient_id}")
        return self.patients[patient_id]

    def list_patients(self) -> list[Dict[str, Any]]:
        """List all patients."""
        return [
            {
                "patient_id": p.patient_id,
                "name": p.name,
                "age": p.age,
                "symptoms": p.symptoms,
            }
            for p in self.patients.values()
        ]


# Global store instance
_store: PatientDataStore = None


def get_patient_store() -> PatientDataStore:
    """Get or create patient data store."""
    global _store
    if _store is None:
        _store = PatientDataStore()
    return _store


def get_patient_data(patient_id: str) -> Dict[str, Any]:
    """
    Tool function for agents to call.
    Returns patient data in a format suitable for Groq function calling.
    """
    store = get_patient_store()
    patient = store.get_patient(patient_id)
    return {
        "patient_id": patient.patient_id,
        "name": patient.name,
        "age": patient.age,
        "symptoms": patient.symptoms,
        "medical_history": patient.medical_history,
        "risk_factors": patient.risk_factors,
    }

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Citation(BaseModel):
    source: str
    page: int
    chunk_id: str
    excerpt: str


class AssessmentRequest(BaseModel):
    patient_id: str


class AssessmentResponse(BaseModel):
    patient_id: str
    patient_name: str
    age: int
    symptoms: List[str]
    recommendation: str
    reasoning: str
    citations: List[Citation]


class PatientData(BaseModel):
    patient_id: str
    name: str
    age: int
    symptoms: List[str]
    medical_history: List[str]
    risk_factors: List[str]


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    citations: Optional[List[Citation]] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    top_k: int = 5


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: List[Citation]


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.schemas.models import (
    AssessmentRequest,
    AssessmentResponse,
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    PatientData,
)
from app.agents.clinical_agent import ClinicalDecisionAgent
from app.agents.chat_agent import ChatAgent
from app.memory.session_store import get_session_store
from app.tools.patient_tool import get_patient_store

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="NG12 Cancer Risk Assessor",
    description="RAG-powered clinical decision support system",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
clinical_agent = ClinicalDecisionAgent()
chat_agent = ChatAgent()
session_store = get_session_store()
patient_store = get_patient_store()



@app.post("/assess", response_model=AssessmentResponse)
def assess_patient(request: AssessmentRequest):
    """
    Assess patient cancer risk using NG12 guidelines.
    Input: patient_id
    Output: Risk stratification with citations
    """
    try:
        assessment = clinical_agent.assess_patient(request.patient_id)
        return assessment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment error: {str(e)}")


@app.get("/patients")
def list_patients():
    """List all available patients."""
    try:
        return patient_store.list_patients()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat with the NG12 assistant.
    Maintains conversation history per session.
    """
    try:
        # Get conversation history
        history = session_store.get_session(request.session_id)

        # Generate response
        response = chat_agent.chat(
            session_id=request.session_id,
            message=request.message,
            conversation_history=history,
            top_k=request.top_k
        )

        # Store messages in session
        session_store.add_message(
            request.session_id,
            "user",
            request.message
        )
        session_store.add_message(
            request.session_id,
            "assistant",
            response.answer,
            citations=[c.model_dump() for c in response.citations]
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.get("/chat/{session_id}/history", response_model=ChatHistoryResponse)
def get_chat_history(session_id: str):
    """Get conversation history for a session."""
    try:
        messages = session_store.get_session(session_id)
        return ChatHistoryResponse(session_id=session_id, messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/chat/{session_id}")
def clear_chat_session(session_id: str):
    """Clear a chat session."""
    try:
        session_store.clear_session(session_id)
        return {"status": "success", "message": f"Session {session_id} cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "NG12 Cancer Risk Assessor"}


# Mount frontend static files if they exist
frontend_dist_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist_path.exists():
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

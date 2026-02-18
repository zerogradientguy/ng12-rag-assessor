# NG12 Cancer Risk Assessor

A RAG-powered clinical decision support system built on NICE NG12 cancer guidelines with a conversational chat interface.

## Overview

This application provides:

1. **Clinical Decision Support (Part 1)**: Structured cancer risk assessment for individual patients, with automated referral recommendations (Same-Day, Urgent, or Routine) grounded in NICE NG12 guidelines.

2. **Chat Assistant (Part 2)**: Conversational AI interface for asking questions about cancer risk assessment, with all answers cited from NG12 guidelines.

Both components share a unified vector store over the NG12 PDF, enabling fast, evidence-based responses.

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **LLM** | Google Gemini 1.5 Pro | Specified in brief, excellent performance |
| **Embeddings** | Sentence-Transformers (all-MiniLM-L6-v2) | Local, free, private |
| **Vector DB** | ChromaDB | Lightweight, persistent, simple |
| **PDF Parsing** | pdfplumber | Better table/text extraction |
| **Backend** | FastAPI + Uvicorn | Specified in brief, fast, async-ready |
| **Frontend** | React + Vite + Tailwind | Clean UI, fast development, responsive |
| **Container** | Docker + docker-compose | Development and production parity |

## Project Structure

```
D:\thecsign\
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app + routes
│   │   ├── agents/
│   │   │   ├── clinical_agent.py      # Decision support agent
│   │   │   └── chat_agent.py          # Conversational agent
│   │   ├── tools/
│   │   │   └── patient_tool.py        # Patient data retrieval
│   │   ├── rag/
│   │   │   ├── ingestion.py           # PDF → ChromaDB pipeline
│   │   │   └── retriever.py           # Query vector store
│   │   ├── memory/
│   │   │   └── session_store.py       # Chat session management
│   │   ├── schemas/
│   │   │   └── models.py              # Pydantic schemas
│   │   └── data/
│   │       └── patients.json          # 10 sample patients
│   ├── scripts/
│   │   └── ingest_pdf.py              # One-time PDF ingestion
│   ├── requirements.txt
│   ├── Dockerfile
│   └── vector_store/                  # ChromaDB persistence (gitignored)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── AssessmentTab.jsx
│   │   │   └── ChatTab.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── index.html
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── PROMPTS.md                         # Clinical agent strategy
└── CHAT_PROMPTS.md                    # Chat grounding strategy
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google API Key with Gemini access (get from [Google AI Studio](https://aistudio.google.com/app/apikey))
- Docker & docker-compose (optional, for containerized deployment)

### Local Development

1. **Clone/setup**:
   ```bash
   cd D:\thecsign
   ```

2. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/Scripts/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   # Copy and edit
   cp .env.example .env
   # Add your Google Gemini API key to GOOGLE_API_KEY
   ```

4. **Ingest PDF**:
   ```bash
   python scripts/ingest_pdf.py
   ```
   This will:
   - Attempt to download NG12 PDF from NICE website
   - If download fails, create a sample PDF with NG12 content
   - Parse and embed into ChromaDB

5. **Start backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   # Backend runs on http://localhost:8000
   ```

6. **Frontend setup** (new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   # Frontend runs on http://localhost:5173
   ```

### Docker Deployment

```bash
# Build and run
docker-compose up

# Frontend: http://localhost
# Backend: http://localhost:8000
```

## API Endpoints

### Part 1: Clinical Assessment

**POST `/assess`**
- Request: `{"patient_id": "PT-101"}`
- Response: `AssessmentResponse` with recommendation, reasoning, and citations

Example:
```bash
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "PT-101"}'
```

**GET `/patients`**
- Lists all available patients
- Returns array of patient summaries for dropdown population

### Part 2: Chat

**POST `/chat`**
- Request: `{"session_id": "abc123", "message": "...", "top_k": 5}`
- Response: `ChatResponse` with answer and citations
- Maintains conversation history per session

**GET `/chat/{session_id}/history`**
- Returns conversation history for a session

**DELETE `/chat/{session_id}`**
- Clears a chat session

### Health

**GET `/health`**
- Returns `{"status": "ok"}`

## Usage

### Patient Assessment

1. Navigate to "Patient Assessment" tab
2. Select a patient from dropdown
3. Click "Assess Patient"
4. Review:
   - **Recommendation**: Same-Day, Urgent, or Routine referral
   - **Reasoning**: Clinical justification
   - **Citations**: NG12 guideline excerpts

### Chat Assistant

1. Navigate to "Chat Assistant" tab
2. Type questions about cancer risk, symptoms, referral pathways, etc.
3. AI responds with evidence-based answers citing NG12
4. Each message shows source page and excerpt
5. Clear chat history with "Clear Chat" button

## Architecture Decisions

### Chunking Strategy
- Split PDF by page, then by paragraphs (double-newlines)
- 500-token chunks with 50-token overlap for context preservation
- Chunk IDs: `ng12_{page:04d}_{chunk:02d}` for precise citations

### Function Calling (Clinical Agent)
1. Load patient data via `get_patient_data()` tool
2. Internal RAG retrieval based on symptoms
3. Generate recommendation with LLM
4. Return structured response

### Grounding Guardrails (Chat Agent)
- Every clinical statement must be cited
- If retrieval confidence low, respond with "insufficient evidence"
- System prompt forbids inventing thresholds
- Context-aware responses only

### Session Management
- In-memory dictionary for chat sessions
- Good for development; production should use Redis
- Upgrade path documented in deployment guides

## Sample Data

10 sample patients in `backend/app/data/patients.json`:
- PT-101 through PT-110
- Mix of risk profiles (smokers, family history, occupational exposure)
- Various symptom presentations (hemoptysis, cough, weight loss, etc.)

Use these for testing without real patient data.

## Environment Variables

```bash
GOOGLE_API_KEY=...                # Required: Google Gemini API key
FRONTEND_URL=http://localhost:5173 # Dev frontend URL
BACKEND_URL=http://localhost:8000  # Backend URL
CHROMA_DB_PATH=./vector_store      # Vector store location
```

## Trade-offs & Future Improvements

### Current Implementation
- ✅ Google Gemini 1.5 Pro (as specified in brief)
- ✅ Local embeddings (private, fast, no API costs)
- ✅ In-memory sessions (simple, good for MVP)
- ✅ ChromaDB file persistence (lightweight)

### Production Considerations
1. **LLM**: Gemini 1.5 Pro is already excellent; monitor usage and costs
2. **Embeddings**: Consider Vertex AI Embeddings API for scaling if needed
3. **Sessions**: Migrate to Redis for distributed sessions
4. **Vector DB**: Scale to Pinecone or Weaviate for larger knowledge bases
5. **Monitoring**: Add OpenTelemetry for production observability
6. **Caching**: Implement Redis caching for frequent queries

## Error Handling

- **Patient Not Found**: 404 response from `/assess` endpoint
- **Chat Errors**: 500 with descriptive message
- **PDF Ingestion**: Automatic fallback to sample PDF if download fails
- **API Timeout**: Groq client has built-in retry logic

## Testing

Run the assessment/chat on sample patients:

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Run a test
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "PT-103"}'
```

Expected output should show:
- Patient details
- A risk recommendation
- Reasoning grounded in symptoms
- Citations from NG12 guidelines

## Limitations & Disclaimers

⚠️ **This is a demonstration system for educational purposes only.**

- Not intended for actual clinical use without regulatory approval
- All recommendations should be verified by qualified clinicians
- NG12 PDF content is for illustration; use official NICE guidelines
- Model outputs may hallucinate; always verify with primary sources

## Support

- For Claude Code help: `/help`
- For GitHub issues: [anthropics/claude-code](https://github.com/anthropics/claude-code/issues)
- For Groq API issues: [console.groq.com](https://console.groq.com)

## License

This project is provided as-is for the technical assessment.

---

**Built with Claude AI** ✨

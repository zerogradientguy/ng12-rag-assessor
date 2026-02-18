# Quick Start Guide

Get the NG12 Cancer Risk Assessor running in 5 minutes.

## Prerequisites

- Python 3.11+ (download from [python.org](https://www.python.org/downloads/))
- Node.js 18+ (download from [nodejs.org](https://nodejs.org/))
- Google API Key with Gemini access (get from [Google AI Studio](https://aistudio.google.com/app/apikey))

## Option 1: Local Development (Recommended for Testing)

### Terminal 1: Backend Setup & Start

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# OR activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ingest PDF and create vector store
python scripts/ingest_pdf.py
# This will download NG12 PDF or create a sample if unavailable

# Start backend
uvicorn app.main:app --reload
# Backend running at http://localhost:8000
```

### Terminal 2: Frontend Setup & Start

```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# Frontend running at http://localhost:5173
```

### Access the Application

1. Open browser to **http://localhost:5173**
2. Try the **Assessment** tab:
   - Select patient "PT-103" (Robert Johnson)
   - Click "Assess Patient"
   - View recommendation with citations
3. Try the **Chat** tab:
   - Ask "What are red flag symptoms in NG12?"
   - Chat responds with guideline citations

### Test Workflow

```bash
# Terminal 3: Test via API
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "PT-101"}'

# Or test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123", "message": "What is hemoptysis?"}'
```

## Option 2: Docker (Production-like)

### Prerequisites
- Docker & Docker Compose installed

### Run

```bash
# In project root
docker-compose up

# Wait for containers to start (~30 seconds)
# Frontend: http://localhost
# Backend: http://localhost:8000
```

### Stop

```bash
docker-compose down
```

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.11+

# Clear __pycache__
rm -r backend/app/__pycache__ backend/app/**/__pycache__

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend won't start

```bash
# Check Node version
node --version  # Should be 18+

# Clear node_modules
rm -rf frontend/node_modules
npm install
```

### PDF ingestion failed

The script will create a sample NG12 PDF if download fails.
To manually add real PDF:

1. Download NG12 PDF from [NICE website](https://www.nice.org.uk/guidance/ng12)
2. Save to `backend/ng12_guidelines.pdf`
3. Run `python backend/scripts/ingest_pdf.py` again

### API calls fail with CORS error

In frontend dev mode, the Vite proxy should handle this.
If not working:
- Check backend is running on `http://localhost:8000`
- Check frontend proxy config in `vite.config.js`
- Try Docker mode which handles this automatically

## File Structure

```
D:\thecsign\
├── backend/          # FastAPI app
│   ├── app/
│   ├── scripts/      # PDF ingestion
│   └── requirements.txt
├── frontend/         # React + Vite
│   ├── src/
│   └── package.json
├── .env              # Your API keys (don't commit!)
└── README.md         # Full documentation
```

## Next Steps

1. ✅ Assess a patient (PT-101 through PT-110)
2. ✅ Chat about cancer symptoms
3. 📖 Read `README.md` for full architecture
4. 🔧 Read `PROMPTS.md` for clinical decision logic
5. 💬 Read `CHAT_PROMPTS.md` for chat grounding strategy

## Support

- **Backend issues**: Check `backend/app/main.py` and CORS configuration
- **Frontend issues**: Check browser console for errors
- **API issues**: Test with `curl` to isolate frontend vs backend problem
- **PDF issues**: Check `backend/scripts/ingest_pdf.py` output

---

**Ready to assess?** 🏥 Open http://localhost:5173 and start with patient PT-103!

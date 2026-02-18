#!/usr/bin/env python3
"""
Test that all Python modules can be imported without errors.
This helps catch syntax issues early.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing Python imports...")

try:
    print("✓ Importing schemas...")
    from app.schemas import models

    print("✓ Importing patient tool...")
    from app.tools import patient_tool

    print("✓ Importing RAG components...")
    from app.rag import ingestion, retriever

    print("✓ Importing agents...")
    from app.agents import clinical_agent, chat_agent

    print("✓ Importing memory...")
    from app.memory import session_store

    print("✓ Importing main app...")
    from app import main

    print("\n✅ All imports successful!")
    print("\nKey classes available:")
    print(f"  - ClinicalDecisionAgent: {clinical_agent.ClinicalDecisionAgent}")
    print(f"  - ChatAgent: {chat_agent.ChatAgent}")
    print(f"  - RAGRetriever: {retriever.RAGRetriever}")
    print(f"  - PatientDataStore: {patient_tool.PatientDataStore}")
    print(f"  - SessionStore: {session_store.SessionStore}")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)

print("\n📦 Ready to run the application!")

#!/usr/bin/env python3
"""
PDF Ingestion Script
Downloads NG12 PDF from NICE website and ingests into ChromaDB
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.ingestion import ingest_ng12_pdf


def download_ng12_pdf(output_path: str) -> bool:
    """
    Download NG12 PDF from NICE website.
    Returns True if successful, False otherwise.
    """
    try:
        import requests
        url = "https://www.nice.org.uk/guidance/ng12/documents/full-guideline-pdf"

        print(f"Downloading NG12 PDF from {url}...")
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ PDF downloaded successfully to {output_path}")
            return True
        else:
            print(f"✗ Failed to download PDF (status code: {response.status_code})")
            return False

    except Exception as e:
        print(f"✗ Error downloading PDF: {e}")
        return False


def create_sample_pdf(output_path: str):
    """
    Create a sample PDF for testing if real PDF is not available.
    This is a fallback for demonstration purposes.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        print(f"Creating sample NG12 PDF at {output_path}...")

        c = canvas.Canvas(output_path, pagesize=letter)
        c.setTitle("NICE NG12 Cancer Guidance (Sample)")

        # Sample guideline content
        sample_text = [
            "NICE NG12: Suspected Cancer - Recognition and Referral",
            "",
            "KEY SYMPTOMS AND SIGNS:",
            "• Hemoptysis (coughing up blood) - urgent referral",
            "• Persistent cough lasting more than 3 weeks",
            "• Unexplained weight loss",
            "• Night sweats",
            "• Dysphagia (difficulty swallowing)",
            "• Hoarseness lasting more than 3 weeks",
            "• Chest pain",
            "",
            "RED FLAG SYMPTOMS:",
            "• Hemoptysis with chest pain",
            "• Stridor or severe dysphagia",
            "• Neurological symptoms",
            "",
            "REFERRAL PATHWAYS:",
            "1. Same-day referral: Red flag symptoms",
            "2. Urgent referral (2 weeks): Concerning symptoms + risk factors",
            "3. Routine screening: Atypical presentations",
            "",
            "RISK FACTORS:",
            "• Age > 60",
            "• Smoking history (current or former)",
            "• Occupational exposures",
            "• Family history of cancer",
            "• Previous cancer diagnosis",
        ]

        y = 750
        for line in sample_text:
            if y < 50:
                c.showPage()
                y = 750

            if line.startswith(("NICE", "KEY", "RED", "REFERRAL", "RISK")):
                c.setFont("Helvetica-Bold", 12)
            else:
                c.setFont("Helvetica", 10)

            c.drawString(50, y, line)
            y -= 20

        c.save()
        print(f"✓ Sample PDF created at {output_path}")
        return True

    except ImportError:
        print("✗ reportlab not available - skipping sample PDF creation")
        return False
    except Exception as e:
        print(f"✗ Error creating sample PDF: {e}")
        return False


def main():
    """Main ingestion workflow."""
    print("=" * 60)
    print("NG12 PDF Ingestion Pipeline")
    print("=" * 60)

    # Setup paths
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    pdf_path = backend_dir / "ng12_guidelines.pdf"
    chroma_db_path = backend_dir / "vector_store"

    print(f"\nPDF path: {pdf_path}")
    print(f"Vector store path: {chroma_db_path}")

    # Step 1: Download or create PDF
    print("\n[Step 1] Obtaining NG12 PDF...")
    if pdf_path.exists():
        print(f"✓ PDF already exists at {pdf_path}")
    else:
        success = download_ng12_pdf(str(pdf_path))
        if not success:
            print("Attempting to create sample PDF for demonstration...")
            success = create_sample_pdf(str(pdf_path))
            if not success:
                print("✗ Could not obtain PDF. Please manually place NG12 PDF at:")
                print(f"  {pdf_path}")
                return

    # Step 2: Check if PDF exists
    if not pdf_path.exists():
        print(f"✗ PDF not found at {pdf_path}")
        return

    # Step 3: Ingest PDF into ChromaDB
    print("\n[Step 2] Ingesting PDF into ChromaDB...")
    try:
        ingest_ng12_pdf(str(pdf_path), str(chroma_db_path))
        print("\n✓ PDF ingestion complete!")
    except Exception as e:
        print(f"\n✗ Error during ingestion: {e}")
        raise

    print("\n" + "=" * 60)
    print("Ready to start the application!")
    print("=" * 60)


if __name__ == "__main__":
    main()

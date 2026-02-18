import json
import os
from typing import Dict, Any, List
import google.generativeai as genai
from app.schemas.models import Citation, AssessmentResponse
from app.rag.retriever import RAGRetriever
from app.tools.patient_tool import get_patient_data


class ClinicalDecisionAgent:
    def __init__(self, gemini_api_key: str = None):
        api_key = gemini_api_key or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel('gemini-1.5-pro')
        self.retriever = RAGRetriever()
        self.model = "gemini-1.5-pro"

        self.system_prompt = """You are a clinical decision support specialist trained on NICE NG12 cancer guidelines.

Your role is to:
1. Review patient clinical presentation
2. Consult the NG12 guidelines via retrieval
3. Provide a risk stratification recommendation: "Routine GP Screening", "Urgent Referral", "Same-Day Referral"
4. Ground all recommendations in the guidelines

Instructions:
- Always call the get_patient_data tool first to retrieve patient information
- Then internally consider what information to retrieve from NG12 guidelines
- Provide structured clinical reasoning
- Never invent thresholds - only cite from NG12
- Be conservative: when in doubt, escalate
- Format your response as JSON with: recommendation, reasoning

Guidelines for recommendations:
- Same-Day Referral: Red flag symptoms (hemoptysis, severe chest pain, stridor, dysphagia with difficulty breathing)
- Urgent Referral: Concerning symptoms + risk factors (persistent cough + smoking, unexplained weight loss, night sweats)
- Routine GP Screening: Atypical symptoms without strong clinical indicators
"""

    def assess_patient(self, patient_id: str) -> AssessmentResponse:
        """Assess patient risk based on NG12 guidelines."""

        # Step 1: Get patient data using tool
        patient_data = get_patient_data(patient_id)

        # Step 2: Query retriever for relevant NG12 content
        query = f"Cancer risk assessment symptoms: {', '.join(patient_data['symptoms'])}"
        retrieved_texts, citations = self.retriever.retrieve(query, top_k=3)

        # Step 3: Create context for LLM
        context = f"""
Patient Data:
- ID: {patient_data['patient_id']}
- Name: {patient_data['name']}
- Age: {patient_data['age']}
- Symptoms: {', '.join(patient_data['symptoms'])}
- Medical History: {', '.join(patient_data['medical_history']) if patient_data['medical_history'] else 'None'}
- Risk Factors: {', '.join(patient_data['risk_factors'])}

NG12 Guideline Context:
{chr(10).join([f"- {text[:300]}..." for text in retrieved_texts])}
"""

        # Step 4: Call LLM to generate assessment
        full_prompt = f"{self.system_prompt}\n\nAssess this patient:\n{context}\n\nProvide your assessment as JSON with keys: recommendation, reasoning"

        response = self.client.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1024,
                temperature=0.7,
            )
        )

        # Step 5: Parse response
        response_text = response.text
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                assessment = json.loads(json_match.group())
            else:
                assessment = {
                    "recommendation": "Urgent Referral",
                    "reasoning": response_text
                }
        except json.JSONDecodeError:
            assessment = {
                "recommendation": "Urgent Referral",
                "reasoning": response_text
            }

        # Step 6: Build response with citations
        return AssessmentResponse(
            patient_id=patient_id,
            patient_name=patient_data['name'],
            age=patient_data['age'],
            symptoms=patient_data['symptoms'],
            recommendation=assessment.get("recommendation", "Urgent Referral"),
            reasoning=assessment.get("reasoning", ""),
            citations=citations
        )

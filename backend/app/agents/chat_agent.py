import os
from typing import Dict, List, Any
import google.generativeai as genai
from app.schemas.models import Citation, ChatMessage, ChatResponse
from app.rag.retriever import RAGRetriever


class ChatAgent:
    def __init__(self, gemini_api_key: str = None):
        api_key = gemini_api_key or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel('gemini-1.5-pro')
        self.retriever = RAGRetriever()
        self.model = "gemini-1.5-pro"

        self.system_prompt = """You are a knowledgeable assistant specialized in NICE NG12 cancer guidelines.

Your role is to:
1. Answer questions about cancer risk assessment
2. Provide evidence-based guidance grounded in NG12
3. Always cite relevant guideline sections
4. Refuse to provide clinical judgments beyond the guidelines

Instructions:
- Every clinical statement must be followed by a citation bracket: [Source: NG12, page X]
- If you cannot find sufficient evidence in NG12, clearly state: "Based on the available NG12 guidelines, I cannot provide evidence-based guidance on this topic."
- Distinguish between guideline recommendations and general information
- Be accurate and conservative - do not speculate beyond the guidelines
- Focus on cancer risk assessment and referral pathways
"""

    def chat(
        self,
        session_id: str,
        message: str,
        conversation_history: List[ChatMessage],
        top_k: int = 5
    ) -> ChatResponse:
        """Process a chat message and generate response with citations."""

        # Step 1: Retrieve relevant NG12 content
        retrieved_texts, citations = self.retriever.retrieve(message, top_k=top_k)

        # Step 2: Build conversation context for LLM
        messages = []

        # Add previous messages
        for msg in conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add current user message with retrieval context
        context_info = "\n\n".join([f"Relevant NG12 content:\n{text}" for text in retrieved_texts])

        user_message = f"{message}\n\n--- Relevant Guidelines Context ---\n{context_info}"

        messages.append({
            "role": "user",
            "content": user_message
        })

        # Step 3: Call LLM
        # Build full conversation with system prompt
        full_messages = f"{self.system_prompt}\n\n"
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            full_messages += f"{role}: {msg['content']}\n\n"

        full_messages += "Assistant:"

        response = self.client.generate_content(
            full_messages,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1024,
                temperature=0.7,
            )
        )

        answer = response.text.strip()

        # Step 4: Return response with citations
        return ChatResponse(
            session_id=session_id,
            answer=answer,
            citations=citations
        )

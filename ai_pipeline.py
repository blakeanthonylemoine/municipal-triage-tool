# ai_pipeline.py
from google import genai
from pydantic import BaseModel, Field

from config import settings

client = genai.Client(api_key=settings.gemini_api_key)

class TriageResult(BaseModel):
    category_id: int | None = Field(description="The ID of the matching category, or null if no match.")
    urgency_score: int = Field(description="Scale of 1 to 5, where 5 is a life-safety emergency.")
    extracted_location: str | None = Field(description="The physical location of the issue, if mentioned.")
    extracted_email: str | None = Field(description="The citizen's email address, if mentioned.")
    extracted_phone: str | None = Field(description="The citizen's phone number, if mentioned.")
    drafted_response: str = Field(description="A polite, 2-sentence draft response to the citizen.")

def evaluate_ticket(ticket_text: str, categories_context: str) -> TriageResult:
    """
    Sends the citizen's complaint and the municipality's available categories to Gemini
    to extract structured routing data.
    """
    prompt = f"""
    You are an expert dispatcher for a municipal government. 
    Analyze the following citizen complaint and categorize it using ONLY the provided categories.
    
    Available Categories:
    {categories_context}
    
    Citizen Complaint:
    {ticket_text}
    """
    
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': TriageResult,
            'temperature': 0.1, # Keep it highly deterministic
        },
    )

    # Extract the token counts provided by Google's API
    usage = {
        "input": response.usage_metadata.prompt_token_count,
        "output": response.usage_metadata.candidates_token_count
    }
    
    # The SDK automatically validates and returns the Pydantic object
    return response.parsed, usage
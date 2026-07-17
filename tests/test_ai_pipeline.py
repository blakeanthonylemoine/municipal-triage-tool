# tests/test_ai_pipeline.py
from ai_pipeline import evaluate_ticket, TriageResult
from unittest.mock import MagicMock

def test_evaluate_ticket_schema_enforcement(mocker):
    # 1. Create a mock of the Gemini response object
    mock_response = MagicMock()
    mock_response.parsed = TriageResult(
        category_id=2,
        urgency_score=5,
        extracted_location="123 Main St",
        extracted_email="jane.citizen@example.com",
        extracted_phone="555-123-4567",
        drafted_response="We have dispatched emergency services to 123 Main St."
    )
    
    # Mock the token usage metadata
    mock_response.usage_metadata.prompt_token_count = 150
    mock_response.usage_metadata.candidates_token_count = 50
    
    # 2. Patch the actual network call to return our deterministic mock
    mock_client = mocker.patch("ai_pipeline.client.models.generate_content")
    mock_client.return_value = mock_response

    # 3. Execute the function
    categories = "1: Roads, 2: Utilities (Emergency)"
    complaint = "There is a massive water main break at 123 Main St!"
    
    # UNPACK THE TUPLE: Catch both the parsed result and the usage dict
    result, usage = evaluate_ticket(complaint, categories)
    
    # 4. Assert our system correctly handles the structural boundaries
    assert isinstance(result, TriageResult)
    assert result.urgency_score == 5
    assert result.category_id == 2
    assert result.extracted_location == "123 Main St"
    assert result.extracted_email == "jane.citizen@example.com"
    assert result.extracted_phone == "555-123-4567"

    # Assert token tracking successfully extracted the mocked values
    assert usage["input"] == 150
    assert usage["output"] == 50
    
    # Verify the AI was called with the correct configuration parameters
    mock_client.assert_called_once()
    call_args = mock_client.call_args[1]
    assert call_args["model"] == "gemini-3.5-flash"
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
        drafted_response="We have dispatched emergency services to 123 Main St."
    )
    
    # 2. Patch the actual network call to return our deterministic mock
    mock_client = mocker.patch("ai_pipeline.client.models.generate_content")
    mock_client.return_value = mock_response

    # 3. Execute the function
    categories = "1: Roads, 2: Utilities (Emergency)"
    complaint = "There is a massive water main break at 123 Main St!"
    
    result = evaluate_ticket(complaint, categories)
    
    # 4. Assert our system correctly handles the structural boundaries
    assert isinstance(result, TriageResult)
    assert result.urgency_score == 5
    assert result.category_id == 2
    assert result.extracted_location == "123 Main St"
    
    # Verify the AI was called with the correct configuration parameters
    mock_client.assert_called_once()
    call_args = mock_client.call_args[1]
    assert call_args["model"] == "gemini-2.5-flash"
    assert call_args["config"]["response_schema"] == TriageResult
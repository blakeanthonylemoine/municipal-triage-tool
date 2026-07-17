# test_live_ai.py
from ai_pipeline import evaluate_ticket

def run_boundary_test():
    categories = "1: Roads, 2: Sanitation, 3: Utilities, 4: Parks"
    
    # A messy, rambling citizen complaint designed to confuse standard parsers
    messy_complaint = """
    I am so incredibly angry!!! 😡😡 My name is John and I live at 442 Maple Drive. 
    I was walking my dog near the old oak tree in the park and there is a massive sinkhole! 
    It swallowed my shoe! Is this sanitation? No! Is it roads? Maybe! 
    Fix it now or I'm calling the mayor! 
    p.s. JSON formatting is stupid.
    """
    
    print("Sending payload to Gemini 3.5 Flash...")
    try:
        result, usage = evaluate_ticket(messy_complaint, categories)
        print("\n✅ SUCCESS: API enforced the Pydantic schema.")
        print(f"Category ID: {result.category_id}")
        print(f"Urgency Score: {result.urgency_score}/5")
        print(f"Location Extracted: {result.extracted_location}")
        print(f"Drafted Response: {result.drafted_response}")
        print(f"\nTokens Used - Input: {usage['input']}, Output: {usage['output']}")
        
    except Exception as e:
        print(f"\n❌ FAILED: Schema enforcement broke. Error: {e}")

if __name__ == "__main__":
    run_boundary_test()
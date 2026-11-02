from src.guardrails.validator import validate_input_node

def test_guardrail():
    valid_state = {"user_query": "Plan a 4 day trip to Dubai for next month"}
    assert validate_input_node(valid_state).get("rejection_reason") is None

    invalid_state = {"user_query": "Write a python script to scrape a website"}
    result = validate_input_node(invalid_state)
    assert "BLOCKED" in result.get("rejection_reason", "")

if __name__ == "__main__":
    test_guardrail()
    print("Guardrail tests passed!")
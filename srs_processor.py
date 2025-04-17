
def process_srs(srs_text: str) -> dict:
    """
    Prepares the initial input for LangGraph workflow.
    Currently, it just wraps the raw SRS text into a dictionary.
    """
    return {
        "input": srs_text,  # This will be passed as input data in the workflow
        "output": ""        # Initialize with an empty output
    }


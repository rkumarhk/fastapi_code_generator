from components.nodes2 import call_llama
import shutil
import docx
import json
import re
import os

def extract_from_docx(file) -> str:
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])



def folder_structure(data):

    prompt = f"""
    Based on the following project analysis, generate the complete initial FastAPI project structure in JSON format.
    The JSON should include:
    - Folder structure with nested directories and files
    - File names as keys and their content as values
    - Include a "requirements.txt" file with necessary dependencies
    - Include a "setup.sh" script for setting up the environment
    Do not give any text in the response, just give the JSON. starting with curly braces.

    Example JSON format:
    {{
        "app/": {{
            "routers/": {{
                "user.py": "content of user.py",
                "item.py": "content of item.py"
            }},
            "models/": {{
                "user.py": "content of user.py",
                "item.py": "content of item.py"
            }},
            "__init__.py": "content of __init__.py",
            "main.py": "content of main.py"
        }},
        "requirements.txt": "fastapi\\nuvicorn\\npsycopg2-binary\\nalembic\\nsqlalchemy\\npython-dotenv",
        "setup.sh": "content of setup.sh"
    }}

    Analysis:
    {data}
    """
    project_structure =  call_llama(prompt)
    return project_structure


def create_project_structure(project_structure: dict, base_path: str = "."):
    """
    Creates project structure from dictionary/JSON
    Args:
        project_structure (dict): Dictionary containing project structure
        base_path (str): Base path where project will be created
    """

    if os.path.exists(base_path):
        shutil.rmtree(base_path)

    for name, content in project_structure.items():
        full_path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            # Create directory if it doesn't exist
            os.makedirs(full_path, exist_ok=True)
            # Recursively create contents
            create_project_structure(content, full_path)
        else:
            # Create file with content
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(str(content))


def extract_json_from_text(text):
    """Extract valid JSON from text that may contain markdown or other content"""
    # Try to parse directly first
    try:
        json.loads(text)
        return text  # If it parses correctly, return as is
    except json.JSONDecodeError:
        pass
   
    # Look for JSON pattern within code blocks
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(json_pattern, text)
    if match:
        json_content = match.group(1)
        try:
            # Validate that this is valid JSON
            json.loads(json_content)
            return json_content
        except json.JSONDecodeError:
            pass
   
    # If no code block, look for curly braces pattern
    json_pattern = r'(\{[\s\S]*\})'
    match = re.search(json_pattern, text)
    if match:
        json_content = match.group(1)
        try:
            # Validate that this is valid JSON
            json.loads(json_content)
            return json_content
        except json.JSONDecodeError:
            pass
   
    # If all else fails, just return the original text and let the caller handle errors
    return text
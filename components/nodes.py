import os
import httpx
import json
import re
import tempfile
import zipfile
import time


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLAMA_MODEL = "llama3-8b-8192"

def call_llama(prompt, backoff_factor=2):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": LLAMA_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    for attempt in range(5):
        try:
            with httpx.Client() as client:
                response = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=json_data)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Too Many Requests
                wait_time = backoff_factor ** attempt
                print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise  # Re-raise other HTTP errors
    raise Exception("Max retries exceeded for call_llama")

def parse_files_from_llm_response(response_text):
    pattern = r"(?P<path>[^\n]+)\n```(?:python)?\n(?P<code>.*?)```"
    files = {}
    for match in re.finditer(pattern, response_text, re.DOTALL):
        path = match.group("path").strip()
        code = match.group("code").strip()
        files[path] = code
    return files


def extract_json_from_response(response_text):
    # Use regex to extract the JSON part
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        json_data = match.group(0)  # Extract the JSON part
        try:
            return json.loads(json_data)  # Parse the JSON
        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
            return None
    else:
        print("Error: No JSON found in the response")
        return None

def analysis_node(data):
    srs_text = data.get("input")
    # print(srs_text)

    prompt = f"""
    You are an expert software architect. Analyze the following SRS (Software Requirements Specification) and extract:
    Key components to analyze for backend generation: for example -
        a.	Required API endpoints and their parameters.
        b.	Backend logic (business rules, required computations).
        c.	Database schema (tables, relationships, constraints).
        d.	Authentication & authorization requirements.

    also give small output so that i will not get 429 error
    

    SRS:
    {srs_text}
    """
    analysis_result =  call_llama(prompt)
    return {"analysis": analysis_result, **data}

def setup_backend_node(data):
    analysis = data.get("analysis", "")
    
    # Prompt for generating the backend setup
    prompt = f"""
    Based on the following project analysis, generate the complete initial FastAPI project setup.
    Include:
    - Modular folder structure (e.g., app/, app/routers/, app/models/, etc.)
    - Necessary __init__.py files
    - requirements.txt content (with FastAPI, Uvicorn, PostgreSQL, Alembic, SQLAlchemy, etc.)
    - setup.sh script for setting up the environment
    - Database integration with PostgreSQL, including connection pooling and migrations
    - Validation steps to ensure prerequisites (Python, PostgreSQL, necessary packages) are met

    Analysis:
    {analysis}
    """
    # Call the LLM to generate the backend setup
    backend_setup = call_llama(prompt)
    
    # Parse the response and return the setup details
    return {"setup_backend": backend_setup, **data}

def setup_node(data):
    # print(data)
    analysis = data.get("analysis", "")
    prompt = f"""
    Based on the following project analysis, generate the complete initial FastAPI project structure in JSON format.
    The JSON should include:
    - Folder structure with nested directories and files
    - File names as keys and their content as values
    - Include a "requirements.txt" file with necessary dependencies
    - Include a "setup.sh" script for setting up the environment

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
    {analysis}
    """
    project_structure =  call_llama(prompt)
    # folder_structure = extract_json_from_response(project_structure)
    # if folder_structure is None:
    #     return {"error": "Invalid JSON format from setup_node", **data}

    # print(folder_structure)
    return {"setup": project_structure, **data}

def coding_node(data):
    setup = data.get("setup", "")

    # Parse the JSON response from setup_node
    try:
        folder_structure = json.loads(setup)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
        return {"error": "Invalid JSON format", **data}

    # Generate the folder structure and write files
    def create_structure(base_path, structure):
        for name, content in structure.items():
            full_path = os.path.join(base_path, name)
            if isinstance(content, dict):
                # Create a directory
                os.makedirs(full_path, exist_ok=True)
                create_structure(full_path, content)
            else:
                # Create a file
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

    project_dir = "generated_project"
    create_structure(project_dir, folder_structure)

    return {"coding": folder_structure, **data}


def iteration_node(data):
    code = data.get("coding_raw", "")
    prompt = f"""
    Review and refine the following FastAPI project code for improvements:
    - Identify and fix bugs
    - Enhance performance or security
    - Recommend or apply design pattern improvements
    - Add comments and improve readability

    Code:
    {code}
    """
    # refined_code =  call_llama(prompt)
    return {"iteration": "refined_code", **data}

def deployment_node(data):
    prompt = """
    Generate deployment configurations for the FastAPI project, including:
    - Dockerfile for containerization
    - docker-compose.yaml for multi-service setup
    - CI/CD workflow using GitHub Actions
    - Production settings guidance (Uvicorn, Gunicorn, HTTPS, etc.)
    """
    # deployment_output =  call_llama(prompt)
    return {"deployment": "deployment_output", **data}

def documentation_node(data):
    prompt = """
    Generate comprehensive documentation for the project including:
    - README.md with project overview, setup, usage, and examples
    - Auto-generated API docs using FastAPI's OpenAPI
    - Developer onboarding guide (where to start, dev commands)
    """
    # documentation =  call_llama(prompt)
    return {"documentation": "documentation", **data}

def logging_node(data):
    prompt = """
    Integrate LangSmith or other observability tools to track LLM interactions and trace workflows. Provide:
    - Code snippet to initialize LangSmith
    - Logging of input/output at each node
    - Optional dashboard setup
    """
    # logging_code =  call_llama(prompt)
    return {"logging": "logging_code", **data}


# def postprocessing_node(data):
#     files = data.get("coding", {})
#     if not files:
#         return {"error": "No files to process in postprocessing."}

#     # Create a temporary directory
#     with tempfile.TemporaryDirectory() as tmpdir:
#         # Save each file
#         for path, code in files.items():
#             full_path = os.path.join(tmpdir, path)
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, "w", encoding="utf-8") as f:
#                 f.write(code)

#         # Create a zip archive
#         zip_path = os.path.join(tmpdir, "fastapi_project.zip")
#         with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
#             for root, _, files_in_dir in os.walk(tmpdir):
#                 for file in files_in_dir:
#                     if file == "fastapi_project.zip":
#                         continue
#                     file_path = os.path.join(root, file)
#                     arcname = os.path.relpath(file_path, tmpdir)
#                     zipf.write(file_path, arcname)

#         # Read the zip file content as binary
#         with open(zip_path, "rb") as f:
#             zip_content = f.read()

#     return {"zip_file": zip_content, "message": "Project zipped successfully", **data}

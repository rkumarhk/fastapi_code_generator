
import os
import httpx
import json
import re
import tempfile
import zipfile
import time


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLAMA_MODEL = "llama3-70b-8192"

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

def end_point(data):
    srs_text = data.get("input")
    # print(srs_text)

    # results = vector_store.similarity_search(query="Detailed required API endpoints and their parameters.",k=1)

    prompt = f"""
    As an expert software architect, analyze the provided SRS document and generate detailed FastAPI endpoint specifications.
    For each endpoint, provide:

    1. HTTP Method (GET, POST, PUT, DELETE, etc.)
    2. Complete endpoint path with versioning (e.g., /api/v1/...)
    3. Request parameters:
       - Path parameters
       - Query parameters
       - Request body schema
    4. Response schemas:
       - Success response (200, 201, etc.)
       - Error responses (400, 401, 403, 404, etc.)
    5. Authentication requirements
    6. Rate limiting considerations (if any)

    SRS Document:
    {srs_text}
    """
    try:
        api_end_point =  call_llama(prompt)
    except Exception as e:
        print(f"Error calling LLM: {e}")
        api_end_point = "Error generating Api end point specifications."
    
    return {"end_point": api_end_point, **data}

def buisness_logic(data):
    srs_text = data.get("input", "")
    
    prompt = f"""
    As an expert software architect, analyze the API endpoints and generate detailed business logic implementations.
    For each endpoint's business logic, provide:

    1. Core Business Rules:
       - Data validation rules
       - Business constraints
       - Computation formulas
       - State transitions
       - Access control rules

    2. Service Layer Implementation:
       - Service functions with clear input/output contracts
       - Error handling strategies
       - Transaction management
       - Data consistency rules

    3. Integration Points:
       - Database operations
       - External service calls
       - Event triggers
       - Cache management


    API Endpoints Analysis:
    {srs_text}
    """
    # Call the LLM to generate the backend setup
    try:
        buisness_logic_data = call_llama(prompt)
    except Exception as e:
        print(f"Error calling LLM: {e}")
        buisness_logic_data = "Error generating buisness logic specifications."
    
    # Parse the response and return the setup details
    return {"buisness_logic": buisness_logic_data, **data}

def db_schema(data):
    srs = data.get("input", "")
    
    prompt = f"""
    As an expert database architect, analyze the SRS and generate a complete database schema specification.
    Include:

    1. Table Definitions:
       - Table names (following naming conventions)
       - Columns with data types and constraints
       - Primary keys and indexes
       - Foreign key relationships
       - Unique constraints

    2. Database Design:
       - Entity relationships (One-to-One, One-to-Many, Many-to-Many)
       - Junction/Bridge tables for Many-to-Many relationships
       - Normalization level (3NF recommended)
       - Indexing strategy

    3. Data Integrity:
       - Check constraints
       - Default values
       - NOT NULL constraints
       - Cascading rules for foreign keys

    SRS Document:
    {srs}
    """

    try:
        db_schema_data = call_llama(prompt)

    except Exception as e:
        print(f"Error calling LLM: {e}")
        db_schema_data = "Error generating DB schema specifications."
   
    return {"db_schema": db_schema_data, **data}

def auth(data):
    srs = data.get("input", "")

    prompt = f"""
    As a security architect, analyze the SRS and generate comprehensive authentication and authorization specifications.
    Include:

    1. Authentication System:
       - User authentication methods (JWT, OAuth2, API keys)
       - Password policies and hashing strategies
       - Multi-factor authentication requirements
       - Session management
       - Token handling and refresh mechanisms

    2. Authorization Framework:
       - Role-based access control (RBAC)
       - Permission levels and hierarchies
       - Resource-based access control
       - API endpoint security requirements

    3. Security Measures:
       - Rate limiting strategies
       - IP whitelisting/blacklisting
       - Request validation
       - CORS policies

    

    SRS Document:
    {srs}
    """
    try:
        # Call the LLM to generate the backend setup
        auth_data = call_llama(prompt) 
    except Exception as e:
        print(f"Error calling LLM: {e}")
        auth_data = "Error generating authentication specifications."
    # auth_data =  call_llama(prompt)
    
    return {"auth": auth_data, **data}


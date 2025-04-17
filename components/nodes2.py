
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
    You are an expert software architect. Analyze the following document:
    Key components to analyze the Required API endpoints and their parameters.

    srs:
    {srs_text}
    """
    api_end_point =  call_llama(prompt)
    return {"end_point": api_end_point, **data}

def buisness_logic(data):
    srs_text = data.get("end_point", "")
    
    prompt = f"""
    Based on the following project analysis, generate the complete Buisness logic.
    Include:
    Backend logic (business rules, required computations).
    Analysis:
    {srs_text}
    """
    # Call the LLM to generate the backend setup
    buisness_logic = call_llama(prompt)
    
    # Parse the response and return the setup details
    return {"buisness_logic": buisness_logic, **data}

def db_schema(data):
    srs = data.get("buisness_logic", "")
    
    prompt = f"""
    Based on the following project analysis, generate the complete Database schema.
    Database schema (tables, relationships, constraints).
    
    srs:
    {srs}
    """
   
    return {"db_schema": "db_schema", **data}

def auth(data):
    srs = data.get("input", "")

    

    prompt = f"""
    Based on the following project analysis, generate the complete Authentication.
    Authentication & authorization requirements.
    
    srs:
    {srs}
    """
    # auth =  call_llama(prompt)
    
    return {"auth": "auth", **data}


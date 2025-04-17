# main.py
from fastapi import FastAPI, UploadFile, File
from components.srs_processor import process_srs
from components.langgraph_executor import run_langgraph_workflow
from langchain_community.tools import ShellTool
from langchain.agents import AgentExecutor
from components.helper import create_project_structure, folder_structure, extract_json_from_text
import os
import json
from langchain_groq import ChatGroq
app = FastAPI()

llm = ChatGroq(model="llama3-70b-8192", api_key=os.getenv("GROQ_API_KEY"))


tools = [ShellTool()]

tool_agent = AgentExecutor.from_agent_and_tools(agent=llm, tools=tools, verbose=True)




def generate_project(srs_text):
    processed_data = process_srs(srs_text)
    output = run_langgraph_workflow(processed_data)
    structure = folder_structure(output)
    # structure = extract_json_from_text(structure)

    try:
        structure_dict = json.loads(structure)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {"error": "Invalid JSON structure"}
    
    create_project_structure(structure_dict, base_path="generated_project")
    print(4)

    output.pop("input")
    files = output.get("end_point", {})
    project_dir = "generated_project"

    
    return {"message": "Project files generated.", "files": "files"}


# main.py
from fastapi import FastAPI, UploadFile, File
from srs_processor import process_srs
from langgraph_executor import run_langgraph_workflow
from langchain_community.tools import ShellTool
from langchain.agents import AgentExecutor
from langchain_postgres import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyMuPDFLoader
import os
import shutil
import io
import re
import subprocess
from langchain_groq import ChatGroq
import sys
from vdb import vector_store, store_into_vdb
app = FastAPI()

llm = ChatGroq(model="llama3-70b-8192", api_key=os.getenv("GROQ_API_KEY"))


tools = [ShellTool()]

tool_agent = AgentExecutor.from_agent_and_tools(agent=llm, tools=tools, verbose=True)



def load_document(file_path):
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    return documents

# @app.post("/generate-project")
def generate_project():
    srs_doc_path = "mini4.docx"
    print(0)

    # with open(srs_doc_path, "rb") as f:
    #     content = f.read()
    srs_text = load_document(srs_doc_path)
    # print(0)
    # content = srs_doc.read()
    print(1)
    # srs_text = content.decode("utf-8")
    store_into_vdb(srs_text)
    print(2)
    processed_data = process_srs(srs_text)
    print(3)
    output = run_langgraph_workflow(processed_data)
    print(4)

    # print(output)

    files = output.get("coding", {})
    print(files)
    project_dir = "generated_project"

    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)

    # # tool_agent.invoke(f"python3 -m venv {project_dir}/venv &&{project_dir}/venv/scripts/activate && pip install fastapi uvicorn psycopg2-binary alembic sqlalchemy python-dotenv")
    # venv_path = os.path.join(project_dir, "venv")
    # subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)

    # # Activate virtual environment and install dependencies
    # pip_executable = os.path.join(venv_path, "Scripts", "pip.exe") if os.name == "nt" else os.path.join(venv_path, "bin", "pip")
    # subprocess.run([pip_executable, "install", "fastapi", "uvicorn", "psycopg2-binary", "alembic", "sqlalchemy", "python-dotenv"], check=True)

    # for path, code in files.items():
    #     print(path+"-------")
        
    #     clean_path = path.replace("**", "").strip()
    #     clean_path = re.sub(r'[^\w\s/.-]', '', clean_path)
    #     clean_path = re.sub(r'\s*\(.*\)\s*$', '', clean_path)
    #     # clean_path = path.split()[0]

    #     full_path = os.path.join(project_dir, clean_path)
    #     os.makedirs(os.path.dirname(full_path), exist_ok=True)
    #     with open(full_path, "w") as f:
    #         f.write(code)

    
    return {"message": "Project files generated.", "files": "files"}

generate_project()

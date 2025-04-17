from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from components.mini import generate_project
from components.helper import extract_from_docx
import json
from typing import Dict, Any

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    try:
        # Validate file type
        if not file.filename.endswith('.docx'):
            raise HTTPException(
                status_code=400,
                detail="Only .docx files are supported"
            )

        # Read file contents
        try:
            contents = await file.read()
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error reading file: {str(e)}"
            )

        # Extract content from docx
        try:
            res = extract_from_docx(file.file)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error extracting content from docx: {str(e)}"
            )

        # Generate project
        try:
            project_result = generate_project(res)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating project: {str(e)}"
            )

        return JSONResponse({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents),
            "status": "success",
            "project_generated": True
        })

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
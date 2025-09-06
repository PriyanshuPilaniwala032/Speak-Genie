import json
import sys
import subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="n8n Workflow Popularity API",
    description="Provides a list of popular n8n workflows from Forum, YouTube, and GitHub.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

DATA_FILE = 'final_dataset.json'

def run_pipeline_script():
    """
    Executes the main.py script as a subprocess to re-collect and process all data.
    This is a robust way to run the script without blocking the API.
    """
    print("Starting data pipeline execution...")
    try:
        python_executable = sys.executable
        process = subprocess.run(
            [python_executable, "main.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print("Pipeline script finished successfully.")
        print(process.stdout)
    except subprocess.CalledProcessError as e:
        print("--- ERROR: Pipeline script failed ---")
        print(e.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while running the pipeline: {e}")

@app.get("/workflows", tags=["Workflows"])
def get_workflows():
    """
    Retrieve the consolidated and ranked list of popular n8n workflows.
    """
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, 
            detail="Dataset not found. Please run the main.py script first to generate it."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An internal server error occurred: {e}"
        )

@app.post("/refresh", tags=["Actions"])
def trigger_refresh(background_tasks: BackgroundTasks):
    """
    Triggers a background task to re-run the entire data collection and processing pipeline.
    This allows the API to respond immediately while the work happens in the background.
    """
    background_tasks.add_task(run_pipeline_script)
    return JSONResponse(content={"message": "Data refresh process started in the background. It may take a few minutes to complete."})


@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "API is running. Visit /docs for documentation."}

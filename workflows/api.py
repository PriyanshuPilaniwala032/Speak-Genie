import json
import sys
import subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI(
    title="n8n Workflow Popularity API",
    description="Provides a list of popular n8n workflows from Forum, YouTube, and GitHub.",
    version="1.0.0"
)

# --- IMPORTANT FOR FRONTEND ---
# This allows your index.html file to fetch data from your API
# without being blocked by browser security policies (CORS).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins (for simplicity in this project)
    allow_credentials=True,
    allow_methods=["*"], # Allows all HTTP methods
    allow_headers=["*"], # Allows all headers
)


# Define the path to your final dataset
DATA_FILE = 'final_dataset.json'

def run_pipeline_script():
    """
    Executes the main.py script as a subprocess to re-collect and process all data.
    This is a robust way to run the script without blocking the API.
    """
    print("Starting data pipeline execution...")
    try:
        # Ensure we use the same Python interpreter that is running the API
        python_executable = sys.executable
        # Run the main.py script. It will print its own progress.
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
        # If the data file doesn't exist, return error
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


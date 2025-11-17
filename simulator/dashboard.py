from fastapi import FastAPI

from .pipeline import build_status

app = FastAPI(title="CI/CD_pipeline_simulator_dashboard")

@app.get("/")
def read_root():
    """Root endpoint to show the app is running."""
    return {"message": "CI/CD Simulator is running. Go to /builds to see status."}

@app.get("/builds")
def get_build_status():
    """returns the current state of the build_status dictionary"""
    return build_status
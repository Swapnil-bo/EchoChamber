"""
In-memory job state store.

Simple dict-based store — no Redis or database needed for this scale.
Each job tracks status, progress message, result data, and errors.
"""

jobs = {}


def create_job(job_id: str):
    """Initialize a new job in the store with 'queued' status."""
    jobs[job_id] = {
        "status": "queued",
        "message": "Job queued...",
        "result": None,
        "error": None,
    }


def update_job(job_id: str, message: str, status: str = "processing"):
    """Update a job's progress message and optionally its status."""
    jobs[job_id]["status"] = status
    jobs[job_id]["message"] = message


def complete_job(job_id: str, audio_url: str, script: list):
    """Mark a job as complete with its audio URL and script data."""
    jobs[job_id]["status"] = "complete"
    jobs[job_id]["message"] = "Podcast ready!"
    jobs[job_id]["result"] = {"audio_url": audio_url, "script": script}


def fail_job(job_id: str, error: str):
    """Mark a job as failed with an error message."""
    jobs[job_id]["status"] = "failed"
    jobs[job_id]["error"] = error


def get_job(job_id: str):
    """Retrieve a job's current state. Returns None if job doesn't exist."""
    return jobs.get(job_id)

# app/core/domain/entities/job_entity.py

from typing import Optional

class JobStatus:
    PENDING = "pending"
    DONE = "done"
    ERROR = "error"

class Job:
    """
    Représente un job de génération de document.
    """
    def __init__(
        self,
        job_id: str,
        status: str = JobStatus.PENDING,
        file_bytes: Optional[bytes] = None,
        error: Optional[str] = None
    ):
        self.job_id = job_id
        self.status = status
        self.file_bytes = file_bytes
        self.error = error

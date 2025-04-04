# app/tests/unit/test_initiate_generation_use_case.py

import pytest
from fastapi import BackgroundTasks, UploadFile
from app.core.use_cases.initiate_generation_use_case import initiate_generation_use_case
from app.core.domain.entities.job_entity import JobStatus

@pytest.mark.asyncio
async def test_initiate_generation_use_case(mocker):
    mock_repo = mocker.Mock()
    background_tasks = BackgroundTasks()

    mock_file = mocker.Mock(spec=UploadFile)
    mock_file.filename = "test.txt"

    result = initiate_generation_use_case(
        job_repository=mock_repo,
        background_tasks=background_tasks,
        compte_rendu_file=mock_file,
        description_missions="Missions",
        montant_provision="1000"
    )

    assert "job_id" in result
    assert result["status"] == "started"
    mock_repo.create_job.assert_called_once()

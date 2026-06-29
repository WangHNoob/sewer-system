from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from services.batch_engine import BatchEngine
from models.schemas import BatchTask
import uuid, os

router = APIRouter()

batch_tasks: dict[str, BatchTask] = {}


@router.post("/batch/start")
async def start_batch(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None,
    llm_provider: str = "cloud",
):
    task_id = str(uuid.uuid4())[:12]

    task_dir = os.path.join("uploads/batch", task_id)
    os.makedirs(task_dir, exist_ok=True)

    image_paths = []
    for f in files:
        path = os.path.join(task_dir, f.filename)
        with open(path, "wb") as out:
            out.write(await f.read())
        image_paths.append(path)

    task = BatchTask(
        task_id=task_id,
        status="pending",
        total_images=len(image_paths),
        processed=0,
        image_paths=image_paths,
        results=[],
        report_path=None,
    )
    batch_tasks[task_id] = task

    if background_tasks:
        background_tasks.add_task(run_batch_pipeline, task_id, llm_provider)

    return {"task_id": task_id, "total_images": len(image_paths)}


@router.get("/batch/{task_id}/status")
async def get_batch_status(task_id: str):
    task = batch_tasks.get(task_id)
    if not task:
        return {"error": "Task not found"}
    return {
        "task_id": task_id,
        "status": task.status,
        "total": task.total_images,
        "processed": task.processed,
        "current_image": task.current_image,
        "errors": task.errors,
    }


@router.get("/batch/{task_id}/report")
async def download_batch_report(task_id: str):
    task = batch_tasks.get(task_id)
    if not task or task.status != "completed":
        return {"error": "Report not ready"}
    return FileResponse(task.report_path, filename=f"batch_report_{task_id}.docx")


async def run_batch_pipeline(task_id: str, llm_provider: str):
    engine = BatchEngine(task_id=task_id, llm_provider=llm_provider)
    await engine.run()

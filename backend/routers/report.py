from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()


@router.get("/report/{report_id}")
async def download_report(report_id: str):
    report_path = os.path.join("outputs/reports", f"{report_id}.docx")
    if not os.path.exists(report_path):
        return {"error": "Report not found"}
    return FileResponse(report_path, filename=f"report_{report_id}.docx")

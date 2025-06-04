from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Annotated
from pydantic import Field
import json
import re
import asyncio
from fastapi.responses import StreamingResponse

from app.services.add_knowledge import add_knowledge

router = APIRouter()


@router.post("/upload")
async def upload_files(
    file: UploadFile = File(...),
    category_level: Annotated[int, Field(ge=1, le=4)] = Form(...),
):
    file_content = await file.read()

    safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename)

    if category_level < 1 or category_level > 4:
        raise HTTPException(
            status_code=403, detail="Category level must be between 1 and 4"
        )

    async def generate_progress():
        try:
            async for progress in add_knowledge(
                file_content, safe_filename, category_level
            ):
                json_data = json.dumps(progress, ensure_ascii=False)
                yield f"data: {json_data}\n\n"
                await asyncio.sleep(0.05)
        except Exception as e:
            error_msg = json.dumps(
                {
                    "step": "error",
                    "message": f"Unhandled error: {str(e)}",
                    "error": True,
                }
            )
            yield f"data: {error_msg}\n\n"

    return StreamingResponse(
        generate_progress(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

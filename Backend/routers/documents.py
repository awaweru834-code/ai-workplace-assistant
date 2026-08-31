from core.auth import require_role
from core.rate_limit import limiter
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from services.rag_service import ingest_pdf

router = APIRouter(prefix="/docs", tags=["Documents"])

@router.post("/upload")
@limiter.limit("10/minute")
async def upload(
    request: Request, 
    file: UploadFile = File(...),  # noqa: B008
    # IMPROVEMENT: Only HR Admins can upload company policies!
    user=Depends(require_role("hr_admin"))  # noqa: B008
):  
    try:
        content = await file.read()
        ingest_pdf(content, file.filename)
        return {"msg": f"Successfully embedded {file.filename} into Pinecone."}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=500, 
            detail=f"Document ingestion failed: {e!s}"
        )
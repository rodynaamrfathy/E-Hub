from fastapi import APIRouter, UploadFile, File, HTTPException
import base64

router = APIRouter()

@router.post("/images/upload-temp")
async def upload_temp_image(image_file: UploadFile = File(...)):
    """
    Accept an image, encode it in base64, and return it immediately for processing.
    No saving to disk or database.
    """
    try:
        content = await image_file.read()
        image_base64 = base64.b64encode(content).decode()
        mime_type = image_file.content_type

        # Return base64 and mime_type to be sent over WS
        return {"image_base64": image_base64, "mime_type": mime_type}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import uuid

from app.utils.image_search import extract_caption
from app.utils.scraper import scrape_amazon, scrape_flipkart_robust
from app.utils.comparer import merge_results

router = APIRouter()
UPLOAD_FOLDER = "data"

@router.post("/search")
async def search_item(image: UploadFile = File(...)):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    ext = os.path.splitext(image.filename)[1] or ".jpg"
    file_id = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_FOLDER, f"{file_id}{ext}")

    with open(filepath, "wb") as f:
        f.write(await image.read())

    keyword = extract_caption(filepath)

    print(f"[INFO] Extracted keyword → {keyword}")

    amazon = scrape_amazon(keyword)
    flipkart = await scrape_flipkart_robust(keyword)

    merged = merge_results(amazon, flipkart)

    return JSONResponse(content={"results": merged})

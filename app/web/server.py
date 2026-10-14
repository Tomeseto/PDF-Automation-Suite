"""PDF Automation Suite — FastAPI Local Web Server.

Provides REST endpoints for all 18 core PDF features, serves the static
iLovePDF-style frontend, and handles file uploads and downloads.
"""

from __future__ import annotations

import json
import shutil
import time
import uuid
import zipfile
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Core Logger
from app.core.logger import clear_log, get_recent_events

# 18 Core Modules
from app.modules.merge_pdf import merge_pdfs
from app.modules.split_pdf import split_pdf
from app.modules.extract_pages import extract_pages
from app.modules.rotate_pages import rotate_pages
from app.modules.reorder_pages import reorder_pages
from app.modules.organize_pdf import organize_pdf
from app.modules.compress_pdf import compress_pdf
from app.modules.watermark_add import add_watermark
from app.modules.watermark_remove import remove_watermark
from app.modules.password_add import add_password
from app.modules.password_remove import remove_password
from app.modules.signature_add import add_signature
from app.modules.scan_to_pdf import scan_images_to_pdf
from app.modules.extract_text import extract_text
from app.modules.search_pdf import search_pdf
from app.modules.pdf_to_image import pdf_to_images
from app.modules.image_to_pdf import images_to_pdf
from app.modules.batch_process import batch_process
from app.modules.batch_process.registry import BATCH_OPERATIONS

# Workspace paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
TEMP_DIR = BASE_DIR / "temp_web"

TEMP_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="PDF Automation Suite",
    description="Offline Localhost PDF Processing Suite inspired by iLovePDF",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper Utilities
# ---------------------------------------------------------------------------

def create_session_dirs() -> tuple[str, Path, Path]:
    """Create a unique session workspace with uploads and outputs folders."""
    session_id = uuid.uuid4().hex[:12]
    session_path = TEMP_DIR / session_id
    upload_dir = session_path / "uploads"
    output_dir = session_path / "outputs"
    upload_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    return session_id, upload_dir, output_dir


async def save_uploaded_file(upload: UploadFile, destination_dir: Path) -> Path:
    """Safely save an uploaded file to disk."""
    filename = Path(upload.filename or "file.pdf").name
    dest_path = destination_dir / filename
    contents = await upload.read()
    with open(dest_path, "wb") as f:
        f.write(contents)
    return dest_path


def create_zip_archive(files: list[str], output_zip_path: Path) -> Path:
    """Zip a list of files into a single archive."""
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f in files:
            p = Path(f)
            if p.exists() and p.is_file():
                zipf.write(p, arcname=p.name)
    return output_zip_path


def cleanup_old_sessions(max_age_seconds: int = 3600) -> None:
    """Removes sessions older than max_age_seconds to prevent disk buildup."""
    now = time.time()
    if not TEMP_DIR.exists():
        return
    for item in TEMP_DIR.iterdir():
        if item.is_dir():
            try:
                if now - item.stat().st_mtime > max_age_seconds:
                    shutil.rmtree(item, ignore_errors=True)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# API Endpoints: System & Logs
# ---------------------------------------------------------------------------

@app.get("/api/logs")
def get_logs(limit: int = 50):
    """Retrieve recent processing log events."""
    events = get_recent_events(limit=limit)
    return {"status": "ok", "events": events}


@app.post("/api/logs/clear")
def clear_logs():
    """Clear all stored processing logs."""
    clear_log()
    return {"status": "ok", "message": "Logs cleared successfully"}


@app.get("/api/download/{session_id}/{filename}")
def download_file(session_id: str, filename: str):
    """Serve processed output file for direct browser download."""
    file_path = TEMP_DIR / session_id / "outputs" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested file was not found or expired")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream",
    )


# ---------------------------------------------------------------------------
# 1. ORGANIZE PDF ENDPOINTS
# ---------------------------------------------------------------------------

@app.post("/api/organize/merge")
async def api_merge_pdfs(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 PDF files are required for merging.")
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        saved_paths: list[str] = []
        for f in files:
            path = await save_uploaded_file(f, upload_dir)
            saved_paths.append(str(path))

        out_name = "merged_document.pdf"
        out_path = str(output_dir / out_name)
        result = merge_pdfs(saved_paths, out_path)

        return {
            "status": "success",
            "message": "PDFs merged successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/organize/split")
async def api_split_pdf(
    file: UploadFile = File(...),
    ranges: str = Form(...),  # Format: "1-2, 3-5"
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)

        # Parse page ranges: "1-2, 3-5" or single pages "1, 2, 4-6"
        parsed_ranges: list[tuple[int, int]] = []
        for part in ranges.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start_str, end_str = part.split("-", 1)
                parsed_ranges.append((int(start_str.strip()), int(end_str.strip())))
            else:
                p = int(part)
                parsed_ranges.append((p, p))

        if not parsed_ranges:
            raise ValueError("Please provide at least one valid page range (e.g. 1-2, 3-5).")

        results = split_pdf(str(input_path), str(output_dir), parsed_ranges)

        if not results:
            raise ValueError("No files were generated.")

        # If multiple files generated, create zip
        if len(results) > 1:
            zip_name = "split_pages.zip"
            zip_path = output_dir / zip_name
            create_zip_archive(results, zip_path)
            download_file_name = zip_name
        else:
            download_file_name = Path(results[0]).name

        return {
            "status": "success",
            "message": f"Successfully split into {len(results)} file(s)!",
            "download_url": f"/api/download/{session_id}/{download_file_name}",
            "filename": download_file_name,
            "count": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/organize/extract")
async def api_extract_pages(
    file: UploadFile = File(...),
    pages: str = Form(...),  # Format: "1, 3, 5-7"
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)

        # Parse page list
        page_list: list[int] = []
        for part in pages.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                s, e = part.split("-", 1)
                page_list.extend(range(int(s.strip()), int(e.strip()) + 1))
            else:
                page_list.append(int(part))

        if not page_list:
            raise ValueError("Please specify valid page numbers to extract.")

        out_name = f"extracted_pages.pdf"
        out_path = str(output_dir / out_name)
        result = extract_pages(str(input_path), out_path, page_list)

        return {
            "status": "success",
            "message": f"Extracted {len(page_list)} page(s) successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/organize/rotate")
async def api_rotate_pages(
    file: UploadFile = File(...),
    angle: int = Form(...),
    pages: Optional[str] = Form(None),  # None means all pages
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)

        page_list: Optional[list[int]] = None
        if pages and pages.strip():
            page_list = []
            for part in pages.split(","):
                part = part.strip()
                if not part:
                    continue
                if "-" in part:
                    s, e = part.split("-", 1)
                    page_list.extend(range(int(s.strip()), int(e.strip()) + 1))
                else:
                    page_list.append(int(part))

        out_name = "rotated_document.pdf"
        out_path = str(output_dir / out_name)
        result = rotate_pages(str(input_path), out_path, angle, page_list)

        return {
            "status": "success",
            "message": f"Rotated pages by {angle}° successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/organize/reorder")
async def api_reorder_pages(
    file: UploadFile = File(...),
    order: str = Form(...),  # Permutation: e.g. "3, 1, 2, 4"
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        new_order = [int(p.strip()) for p in order.split(",") if p.strip()]

        out_name = "reordered_document.pdf"
        out_path = str(output_dir / out_name)
        result = reorder_pages(str(input_path), out_path, new_order)

        return {
            "status": "success",
            "message": "Pages reordered successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/organize/pipeline")
async def api_organize_pdf(
    file: UploadFile = File(...),
    operations_json: str = Form(...),  # JSON array of operations
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        operations = json.loads(operations_json)

        out_name = "organized_document.pdf"
        out_path = str(output_dir / out_name)
        result = organize_pdf(str(input_path), out_path, operations)

        return {
            "status": "success",
            "message": "Organization pipeline executed successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# 2. OPTIMIZE & COMPRESS ENDPOINTS
# ---------------------------------------------------------------------------

@app.post("/api/optimize/compress")
async def api_compress_pdf(file: UploadFile = File(...)):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        out_name = "compressed_document.pdf"
        out_path = str(output_dir / out_name)

        stats = compress_pdf(str(input_path), out_path)

        orig_kb = round(stats.get("original_size", 0) / 1024, 1)
        comp_kb = round(stats.get("compressed_size", 0) / 1024, 1)
        savings = stats.get("savings_percent", 0.0)

        return {
            "status": "success",
            "message": f"Compressed! Reduced from {orig_kb} KB to {comp_kb} KB ({savings}% savings).",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
            "stats": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# 3. PDF SECURITY ENDPOINTS
# ---------------------------------------------------------------------------

@app.post("/api/security/password-add")
async def api_password_add(
    file: UploadFile = File(...),
    user_password: str = Form(...),
    owner_password: Optional[str] = Form(None),
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        out_name = "protected_document.pdf"
        out_path = str(output_dir / out_name)

        result = add_password(
            str(input_path),
            out_path,
            user_password,
            owner_password or None,
        )

        return {
            "status": "success",
            "message": "Password protection enabled successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/security/password-remove")
async def api_password_remove(
    file: UploadFile = File(...),
    password: str = Form(...),
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        out_name = "unlocked_document.pdf"
        out_path = str(output_dir / out_name)

        result = remove_password(str(input_path), out_path, password)

        return {
            "status": "success",
            "message": "Password removed successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/security/watermark-add")
async def api_watermark_add(
    file: UploadFile = File(...),
    text: str = Form(...),
    opacity: float = Form(0.3),
    position: str = Form("center"),
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        out_name = "watermarked_document.pdf"
        out_path = str(output_dir / out_name)

        result = add_watermark(str(input_path), out_path, text, opacity, position)

        return {
            "status": "success",
            "message": "Watermark applied successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/security/watermark-remove")
async def api_watermark_remove(
    file: UploadFile = File(...),
    watermark_text: Optional[str] = Form(None),
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        out_name = "unwatermarked_document.pdf"
        out_path = str(output_dir / out_name)

        result = remove_watermark(
            str(input_path),
            out_path,
            watermark_text if watermark_text and watermark_text.strip() else None,
        )

        return {
            "status": "success",
            "message": "Watermark removed successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/security/signature-add")
async def api_signature_add(
    file: UploadFile = File(...),
    signature_image: UploadFile = File(...),
    page_number: int = Form(1),
    x: int = Form(100),
    y: int = Form(100),
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        sig_path = await save_uploaded_file(signature_image, upload_dir)
        out_name = "signed_document.pdf"
        out_path = str(output_dir / out_name)

        result = add_signature(
            str(input_path),
            out_path,
            str(sig_path),
            (x, y),
            page_number,
        )

        return {
            "status": "success",
            "message": f"Signature stamped on page {page_number} successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# 4. CONVERT TO / FROM PDF ENDPOINTS
# ---------------------------------------------------------------------------

@app.post("/api/convert/pdf-to-images")
async def api_pdf_to_images(
    file: UploadFile = File(...),
    image_format: str = Form("png"),  # "png" or "jpeg"
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        results = pdf_to_images(str(input_path), str(output_dir), image_format.lower())

        if not results:
            raise ValueError("No images were generated.")

        zip_name = f"pdf_images_{image_format.lower()}.zip"
        zip_path = output_dir / zip_name
        create_zip_archive(results, zip_path)

        return {
            "status": "success",
            "message": f"Converted {len(results)} pages to {image_format.upper()} images!",
            "download_url": f"/api/download/{session_id}/{zip_name}",
            "filename": zip_name,
            "count": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/convert/images-to-pdf")
async def api_images_to_pdf(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Please upload at least one image file.")
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        saved_paths: list[str] = []
        for f in files:
            path = await save_uploaded_file(f, upload_dir)
            saved_paths.append(str(path))

        out_name = "images_converted.pdf"
        out_path = str(output_dir / out_name)
        result = images_to_pdf(saved_paths, out_path)

        return {
            "status": "success",
            "message": f"Combined {len(saved_paths)} image(s) into PDF successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/convert/scan-to-pdf")
async def api_scan_to_pdf(
    files: List[UploadFile] = File(...),
    enhance: bool = Form(True),
):
    if not files:
        raise HTTPException(status_code=400, detail="Please upload at least one scan image file.")
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        saved_paths: list[str] = []
        for f in files:
            path = await save_uploaded_file(f, upload_dir)
            saved_paths.append(str(path))

        out_name = "scanned_document.pdf"
        out_path = str(output_dir / out_name)
        result = scan_images_to_pdf(saved_paths, out_path, enhance=enhance)

        return {
            "status": "success",
            "message": f"Processed {len(saved_paths)} scanned document page(s) successfully!",
            "download_url": f"/api/download/{session_id}/{out_name}",
            "filename": out_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/convert/extract-text")
async def api_extract_text(file: UploadFile = File(...)):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        text_dict = extract_text(str(input_path))

        # Also write to a .txt file for easy download
        txt_name = "extracted_text.txt"
        txt_path = output_dir / txt_name
        with open(txt_path, "w", encoding="utf-8") as f:
            for page_num, content in sorted(text_dict.items()):
                f.write(f"--- Page {page_num + 1} ---\n{content}\n\n")

        total_words = sum(len(text.split()) for text in text_dict.values())

        return {
            "status": "success",
            "message": f"Extracted text from {len(text_dict)} page(s) (~{total_words} words).",
            "pages": text_dict,
            "download_url": f"/api/download/{session_id}/{txt_name}",
            "filename": txt_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/convert/search-pdf")
async def api_search_pdf(
    file: UploadFile = File(...),
    query: str = Form(...),
    case_sensitive: bool = Form(False),
):
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        input_path = await save_uploaded_file(file, upload_dir)
        results = search_pdf(str(input_path), query, case_sensitive=case_sensitive)

        total_occurrences = sum(len(r.get("rects", [])) for r in results)

        return {
            "status": "success",
            "message": f"Found {total_occurrences} match(es) across {len(results)} page(s).",
            "results": results,
            "total_matches": total_occurrences,
            "matched_pages_count": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# 5. BATCH PROCESSING ENDPOINT
# ---------------------------------------------------------------------------

@app.get("/api/batch/operations")
def get_batch_operations():
    """Return available batch operations and their descriptions."""
    ops = [
        {"name": k, "description": desc}
        for k, (_, desc) in BATCH_OPERATIONS.items()
    ]
    return {"operations": ops}


@app.post("/api/batch/process")
async def api_batch_process(
    files: List[UploadFile] = File(...),
    operation_name: str = Form(...),
    options_json: Optional[str] = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="Please upload files to batch process.")
    cleanup_old_sessions()
    session_id, upload_dir, output_dir = create_session_dirs()

    try:
        saved_paths: list[str] = []
        for f in files:
            path = await save_uploaded_file(f, upload_dir)
            saved_paths.append(str(path))

        options: dict = {}
        if options_json and options_json.strip():
            try:
                options = json.loads(options_json)
            except Exception:
                # Fallback to key=val, key2=val2
                for part in options_json.split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        options[k.strip()] = v.strip()

        # Run batch processor
        reports = batch_process(operation_name, saved_paths, str(output_dir), options)

        # Collect output files created in output_dir
        created_files = [
            str(p) for p in output_dir.iterdir() if p.is_file() and not p.name.endswith(".zip")
        ]

        download_name: Optional[str] = None
        if created_files:
            zip_name = f"batch_{operation_name}_results.zip"
            zip_path = output_dir / zip_name
            create_zip_archive(created_files, zip_path)
            download_name = zip_name

        return {
            "status": "success",
            "message": f"Batch '{operation_name}' completed on {len(saved_paths)} file(s)!",
            "reports": reports,
            "download_url": f"/api/download/{session_id}/{download_name}" if download_name else None,
            "filename": download_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Static Web Frontend
# ---------------------------------------------------------------------------

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return JSONResponse({"status": "error", "message": "Static frontend not initialized yet."})
    return FileResponse(str(index_file))


# Mount remaining static assets (CSS, JS, assets)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

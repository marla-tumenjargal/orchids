# main.py
import os
from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional, List
import asyncio
import time
import uuid
import os
import zipfile
import tempfile
from contextlib import asynccontextmanager

# Import our custom modules
from .scraper import WebsiteScraper
from .llm_cloner import LLMWebsiteCloner
from .utils import validate_url

# Global variables for tracking tasks and requests
tasks: Dict[str, Dict] = {}
requests_used = 0
requests_remaining = 15
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🌸 Orchids Website Cloner API starting up...")
    yield
    # Shutdown
    print("🌸 Orchids Website Cloner API shutting down...")

app = FastAPI(
    title="Orchids Website Cloner API",
    description="AI-powered website cloning service",
    version="1.0.0 (Credit-Optimized)",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class CloneRequest(BaseModel):
    url: HttpUrl
    preferences: Optional[Dict] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class StatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

class DownloadRequest(BaseModel):
    task_id: str
    format: Optional[str] = "zip"  # zip or individual files

@app.get("/")
async def root():
    """Root endpoint with API status"""
    global requests_used, requests_remaining, start_time
    
    uptime = int(time.time() - start_time)
    
    return {
        "message": "🌸 Orchids Website Cloner API is running",
        "version": "1.0.0 (Credit-Optimized)",
        "status": "healthy",
        "uptime_seconds": uptime,
        "requests_used": requests_used,
        "requests_remaining": requests_remaining,
        "endpoints": {
            "clone": "POST /clone - Start website cloning",
            "status": "GET /status/{task_id} - Check task status",
            "download": "GET /download/{task_id} - Download cloned files",
            "tasks": "GET /tasks - List all tasks",
            "health": "GET /health - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "service": "Orchids Website Cloner API",
        "version": "1.0.0"
    }

@app.post("/clone", response_model=TaskResponse)
async def clone_website(request: CloneRequest, background_tasks: BackgroundTasks):
    """Start website cloning process"""
    global requests_used, requests_remaining
    
    # Check rate limit
    if requests_remaining <= 0:
        raise HTTPException(
            status_code=429, 
            detail={
                "error": "Rate limit exceeded",
                "message": "No requests remaining. Please try again later.",
                "requests_used": requests_used,
                "requests_remaining": requests_remaining
            }
        )
    
    # Validate URL
    url_str = str(request.url)
    if not validate_url(url_str):
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Invalid URL",
                "message": "Please provide a valid URL format (e.g., https://example.com)",
                "provided_url": url_str
            }
        )
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Initialize task
    tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0.0,
        "message": "Task queued for processing",
        "url": url_str,
        "preferences": request.preferences or {},
        "created_at": time.time(),
        "updated_at": time.time(),
        "result": None,
        "error": None,
        "files_ready": False,
        "download_url": None
    }
    
    # Start background task
    background_tasks.add_task(process_clone_task, task_id, url_str, request.preferences)
    
    # Update counters
    requests_used += 1
    requests_remaining -= 1
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Website cloning started successfully"
    )

@app.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """Get the status of a cloning task"""
    if task_id not in tasks:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Task not found",
                "message": f"No task found with ID: {task_id}",
                "task_id": task_id
            }
        )
    
    task = tasks[task_id]
    return StatusResponse(**task)

@app.get("/download/{task_id}")
async def download_cloned_files(task_id: str, format: str = "zip"):
    """Download the cloned website files"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Task not completed",
                "message": "Cannot download files until task is completed",
                "current_status": task["status"]
            }
        )
    
    if not task.get("result") or not task["result"].get("files"):
        raise HTTPException(
            status_code=404, 
            detail="No files available for download"
        )
    
    try:
        if format.lower() == "zip":
            # Create a zip file with all generated files
            zip_path = await create_zip_file(task_id, task["result"]["files"])
            
            return FileResponse(
                zip_path,
                media_type='application/zip',
                filename=f"website_clone_{task_id[:8]}.zip",
                headers={"Content-Disposition": f"attachment; filename=website_clone_{task_id[:8]}.zip"}
            )
        else:
            # Return individual file list
            return JSONResponse({
                "task_id": task_id,
                "files": task["result"]["files"],
                "download_instructions": "Use format=zip to download as zip file"
            })
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating download: {str(e)}"
        )

@app.get("/download/{task_id}/{filename}")
async def download_individual_file(task_id: str, filename: str):
    """Download an individual file from the cloned website"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    files = task.get("result", {}).get("files", {})
    
    if filename not in files:
        raise HTTPException(
            status_code=404, 
            detail=f"File '{filename}' not found in task results"
        )
    
    file_info = files[filename]
    content = file_info.get("content", "")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f"_{filename}") as tmp_file:
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    return FileResponse(
        tmp_path,
        media_type=file_info.get("type", "text/plain"),
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/tasks")
async def list_tasks(limit: int = 50, status: Optional[str] = None):
    """List all tasks with optional filtering"""
    filtered_tasks = list(tasks.values())
    
    # Filter by status if provided
    if status:
        filtered_tasks = [task for task in filtered_tasks if task["status"] == status]
    
    # Limit results
    filtered_tasks = filtered_tasks[:limit]
    
    # Sort by created_at (most recent first)
    filtered_tasks.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    
    return {
        "tasks": filtered_tasks,
        "total_count": len(tasks),
        "filtered_count": len(filtered_tasks),
        "available_statuses": list(set(task["status"] for task in tasks.values()))
    }

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a specific task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    deleted_task = tasks.pop(task_id)
    
    return {
        "message": "Task deleted successfully",
        "deleted_task_id": task_id,
        "task_status": deleted_task["status"]
    }

@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task with status: {task['status']}"
        )
    
    # Update task status
    tasks[task_id].update({
        "status": "cancelled",
        "message": "Task cancelled by user",
        "updated_at": time.time()
    })
    
    return {
        "message": "Task cancelled successfully",
        "task_id": task_id
    }

@app.get("/stats")
async def get_api_stats():
    """Get API usage statistics"""
    global requests_used, requests_remaining, start_time
    
    task_statuses = {}
    for task in tasks.values():
        status = task["status"]
        task_statuses[status] = task_statuses.get(status, 0) + 1
    
    uptime = time.time() - start_time
    
    return {
        "uptime_seconds": int(uptime),
        "uptime_formatted": format_uptime(uptime),
        "requests_used": requests_used,
        "requests_remaining": requests_remaining,
        "total_tasks": len(tasks),
        "task_statuses": task_statuses,
        "api_version": "1.0.0 (Credit-Optimized)"
    }

async def process_clone_task(task_id: str, url: str, preferences: Optional[Dict] = None):
    """Background task to process website cloning"""
    try:
        # Update task status
        tasks[task_id].update({
            "status": "running",
            "progress": 0.1,
            "message": "Initializing scraper...",
            "updated_at": time.time()
        })
        
        # Initialize scraper
        scraper = WebsiteScraper()
        
        # Update progress
        tasks[task_id].update({
            "progress": 0.3,
            "message": "Scraping website content...",
            "updated_at": time.time()
        })
        
        # Scrape the website
        scraped_data = await scraper.scrape_website(url)
        
        # Update progress
        tasks[task_id].update({
            "progress": 0.6,
            "message": "Processing with AI...",
            "updated_at": time.time()
        })
        
        # Initialize LLM cloner
        llm_cloner = LLMWebsiteCloner()
        
        # Generate clone (with preferences if provided)
        if preferences:
            clone_result = await llm_cloner.generate_enhanced_clone(scraped_data, url, preferences)
        else:
            clone_result = await llm_cloner.clone_website(scraped_data, url)
        
        # Update progress
        tasks[task_id].update({
            "progress": 0.9,
            "message": "Finalizing...",
            "updated_at": time.time()
        })
        
        # Complete task
        tasks[task_id].update({
            "status": "completed",
            "progress": 1.0,
            "message": "Website cloned successfully",
            "result": clone_result,
            "files_ready": True,
            "updated_at": time.time()
        })
        
    except Exception as e:
        # Handle errors
        error_message = str(e)
        tasks[task_id].update({
            "status": "failed",
            "progress": 0.0,
            "message": "Cloning failed",
            "error": error_message,
            "updated_at": time.time()
        })

async def create_zip_file(task_id: str, files: Dict[str, Dict]) -> str:
    """Create a zip file containing all generated files"""
    # Create temporary zip file
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"website_clone_{task_id[:8]}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename, file_info in files.items():
            content = file_info.get("content", "")
            zipf.writestr(filename, content)
    
    return zip_path

def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    import traceback
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc() if os.getenv("DEBUG") else None
        }
    )

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add processing time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Health check for container orchestration
@app.get("/healthz")
async def kubernetes_health_check():
    """Kubernetes health check endpoint"""
    return {"status": "ok"}

# Readiness check
@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Check if required environment variables are set
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "reason": "ANTHROPIC_API_KEY not configured"}
        )
    
    return {"status": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# main.py - Fixed Website Cloner API with proper file serving
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import Dict, Optional, List
import asyncio
import time
import uuid
import zipfile
import tempfile
from contextlib import asynccontextmanager
import traceback

# Safe imports with error handling
try:
    from .scraper import WebsiteScraper
    logger.info("Successfully imported WebsiteScraper")
except ImportError as e:
    logger.error(f"Failed to import WebsiteScraper: {e}")
    WebsiteScraper = None

try:
    from .llm_cloner import LLMWebsiteCloner
    logger.info("Successfully imported LLMWebsiteCloner")
except ImportError as e:
    logger.error(f"Failed to import LLMWebsiteCloner: {e}")
    LLMWebsiteCloner = None

try:
    from .utils import validate_url
    logger.info("Successfully imported validate_url")
except ImportError as e:
    logger.error(f"Failed to import validate_url: {e}")
    # Fallback URL validation
    def validate_url(url: str) -> bool:
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

# Global variables for tracking tasks and requests
tasks: Dict[str, Dict] = {}
requests_used = 0
requests_remaining = 15
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🌸 Orchids Website Cloner API starting up...")
    
    # Check critical dependencies
    missing_deps = []
    if not WebsiteScraper:
        missing_deps.append("WebsiteScraper")
    if not LLMWebsiteCloner:
        missing_deps.append("LLMWebsiteCloner")
    
    if missing_deps:
        logger.warning(f"Missing dependencies: {', '.join(missing_deps)}")
        logger.warning("Some features may not work properly")
    
    # Check environment variables
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not found in environment variables")
    
    yield
    
    # Shutdown
    logger.info("🌸 Orchids Website Cloner API shutting down...")

app = FastAPI(
    title="Orchids Website Cloner API",
    description="AI-powered website cloning service",
    version="1.0.0 (Fixed)",
    lifespan=lifespan
)

# Add CORS middleware with more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive for development
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

@app.get("/")
async def root():
    """Root endpoint with API status"""
    global requests_used, requests_remaining, start_time
    
    uptime = int(time.time() - start_time)
    
    return {
        "message": "🌸 Orchids Website Cloner API is running",
        "version": "1.0.0 (Fixed)",
        "status": "healthy",
        "uptime_seconds": uptime,
        "requests_used": requests_used,
        "requests_remaining": requests_remaining,
        "dependencies": {
            "WebsiteScraper": WebsiteScraper is not None,
            "LLMWebsiteCloner": LLMWebsiteCloner is not None,
        },
        "endpoints": {
            "clone": "POST /clone - Start website cloning",
            "status": "GET /status/{task_id} - Check task status",
            "download": "GET /download/{task_id} - Download cloned files",
            "preview": "GET /preview/{task_id} - Preview cloned website",
            "files": "GET /files/{task_id}/{filename} - Get individual files",
            "source": "GET /source/{task_id} - Get source code",
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
    
    try:
        # Check if required dependencies are available
        if not WebsiteScraper:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Service unavailable",
                    "message": "WebsiteScraper module not available. Please check your installation."
                }
            )
        
        if not LLMWebsiteCloner:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Service unavailable",
                    "message": "LLMWebsiteCloner module not available. Please check your installation."
                }
            )
        
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
        
        logger.info(f"Created clone task {task_id} for URL: {url_str}")
        
        return TaskResponse(
            task_id=task_id,
            status="pending",
            message="Website cloning started successfully"
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Validation error",
                "message": "Invalid request data",
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in clone_website: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing your request"
            }
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

# NEW: Preview endpoint to view the cloned website
@app.get("/preview/{task_id}", response_class=HTMLResponse)
async def preview_cloned_website(task_id: str):
    """Preview the cloned website in the browser"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        # Return a status page if not completed
        status_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Clone Status - {task_id[:8]}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .status-container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .status-{task["status"]} {{
                    color: {"#ff6b6b" if task["status"] == "failed" else "#4ecdc4" if task["status"] == "completed" else "#feca57"};
                }}
                .progress-bar {{
                    width: 100%;
                    height: 20px;
                    background: #e0e0e0;
                    border-radius: 10px;
                    overflow: hidden;
                    margin: 20px 0;
                }}
                .progress-fill {{
                    height: 100%;
                    background: #4ecdc4;
                    width: {(task.get('progress', 0) * 100):.1f}%;
                    transition: width 0.3s ease;
                }}
                .refresh-btn {{
                    background: #4ecdc4;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 20px;
                    font-size: 16px;
                }}
                .error {{
                    background: #ffe6e6;
                    color: #cc0000;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
            </style>
            <script>
                // Auto-refresh every 3 seconds if not completed
                {"setTimeout(() => location.reload(), 3000);" if task["status"] not in ["completed", "failed", "cancelled"] else ""}
            </script>
        </head>
        <body>
            <div class="status-container">
                <h1 class="status-{task["status"]}">Clone Status: {task["status"].title()}</h1>
                <p><strong>Task ID:</strong> {task_id[:8]}...</p>
                <p><strong>URL:</strong> {task["url"]}</p>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <p><strong>Progress:</strong> {(task.get('progress', 0) * 100):.1f}%</p>
                <p><strong>Message:</strong> {task["message"]}</p>
                {"<div class='error'><strong>Error:</strong> " + task["error"] + "</div>" if task.get("error") else ""}
                <button class="refresh-btn" onclick="location.reload()">Refresh Status</button>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=status_html)
    
    # Get the generated HTML file
    files = task.get("result", {}).get("files", {})
    if "index.html" not in files:
        raise HTTPException(
            status_code=404,
            detail="Generated HTML file not found"
        )
    
    # Get the HTML content and inject CSS/JS inline
    html_content = files["index.html"].get("content", "")
    css_content = files.get("styles.css", {}).get("content", "")
    js_content = files.get("script.js", {}).get("content", "")
    
    # Inject CSS and JS inline to make it self-contained
    if css_content:
        css_injection = f"<style>\n{css_content}\n</style>"
        html_content = html_content.replace("</head>", f"{css_injection}\n</head>")
    
    if js_content:
        js_injection = f"<script>\n{js_content}\n</script>"
        html_content = html_content.replace("</body>", f"{js_injection}\n</body>")
    
    # Add a banner to indicate this is a clone
    banner = """
    <div style="position: fixed; top: 0; left: 0; right: 0; background: #4ecdc4; color: white; padding: 10px; text-align: center; z-index: 999999; font-family: Arial;">
        🌸 Orchids Clone Preview - <a href="/source/{}" style="color: white;">View Source</a> | <a href="/download/{}" style="color: white;">Download Files</a>
    </div>
    <div style="height: 50px;"></div>
    """.format(task_id, task_id)
    
    # Insert banner after body tag
    html_content = html_content.replace("<body>", f"<body>{banner}")
    
    return HTMLResponse(content=html_content)

# NEW: Source code endpoint
@app.get("/source/{task_id}")
async def get_source_code(task_id: str):
    """Get the source code of the cloned website"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Task not completed",
                "message": "Cannot access source code until task is completed",
                "current_status": task["status"]
            }
        )
    
    files = task.get("result", {}).get("files", {})
    
    return {
        "task_id": task_id,
        "url": task["url"],
        "files": files,
        "metadata": task.get("result", {}).get("clone_metadata", {}),
        "download_urls": {
            "zip": f"/download/{task_id}",
            "preview": f"/preview/{task_id}",
            "individual_files": {filename: f"/files/{task_id}/{filename}" for filename in files.keys()}
        }
    }

# NEW: Individual file endpoint
@app.get("/files/{task_id}/{filename}")
async def get_individual_file(task_id: str, filename: str):
    """Get an individual file from the cloned website"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    files = task.get("result", {}).get("files", {})
    
    if filename not in files:
        available_files = list(files.keys())
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"File '{filename}' not found",
                "available_files": available_files
            }
        )
    
    file_info = files[filename]
    content = file_info.get("content", "")
    
    # Return as JSON for API access or as file download
    return {
        "filename": filename,
        "content": content,
        "type": file_info.get("type", "text/plain"),
        "size": file_info.get("size", len(content)),
        "description": file_info.get("description", "")
    }

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
                "download_instructions": "Use format=zip to download as zip file",
                "preview_url": f"/preview/{task_id}",
                "source_url": f"/source/{task_id}"
            })
            
    except Exception as e:
        logger.error(f"Error creating download: {str(e)}")
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
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f"_{filename}", encoding='utf-8') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        return FileResponse(
            tmp_path,
            media_type=file_info.get("type", "text/plain"),
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error creating individual file download: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating file download: {str(e)}"
        )

@app.get("/tasks")
async def list_tasks(limit: int = 50, status: Optional[str] = None):
    """List all tasks with optional filtering"""
    try:
        filtered_tasks = list(tasks.values())
        
        # Filter by status if provided
        if status:
            filtered_tasks = [task for task in filtered_tasks if task["status"] == status]
        
        # Limit results
        filtered_tasks = filtered_tasks[:limit]
        
        # Sort by created_at (most recent first)
        filtered_tasks.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        
        # Add access URLs for completed tasks
        for task in filtered_tasks:
            if task["status"] == "completed":
                task_id = task["task_id"]
                task["access_urls"] = {
                    "preview": f"/preview/{task_id}",
                    "source": f"/source/{task_id}",
                    "download": f"/download/{task_id}"
                }
        
        return {
            "tasks": filtered_tasks,
            "total_count": len(tasks),
            "filtered_count": len(filtered_tasks),
            "available_statuses": list(set(task["status"] for task in tasks.values())) if tasks else []
        }
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving tasks: {str(e)}"
        )

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
    
    try:
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
            "api_version": "1.0.0 (Fixed)"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )

async def process_clone_task(task_id: str, url: str, preferences: Optional[Dict] = None):
    """Background task to process website cloning"""
    try:
        logger.info(f"Starting clone task {task_id} for URL: {url}")
        
        # Update task status
        tasks[task_id].update({
            "status": "running",
            "progress": 0.1,
            "message": "Initializing scraper...",
            "updated_at": time.time()
        })
        
        # Initialize scraper with error handling
        try:
            scraper = WebsiteScraper()
            logger.info(f"Scraper initialized for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to initialize scraper for task {task_id}: {str(e)}")
            raise Exception(f"Failed to initialize scraper: {str(e)}")
        
        # Update progress
        tasks[task_id].update({
            "progress": 0.3,
            "message": "Scraping website content...",
            "updated_at": time.time()
        })
        
        # Scrape the website with timeout
        try:
            # Use asyncio.wait_for to add timeout
            scraped_data = await asyncio.wait_for(
                scraper.scrape_website(url), 
                timeout=300  # 5 minute timeout
            )
            logger.info(f"Successfully scraped data for task {task_id}")
        except asyncio.TimeoutError:
            raise Exception("Scraping timeout - website took too long to scrape")
        except Exception as e:
            logger.error(f"Scraping failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to scrape website: {str(e)}")
        
        # Update progress
        tasks[task_id].update({
            "progress": 0.6,
            "message": "Processing with AI...",
            "updated_at": time.time()
        })
        
        # Initialize LLM cloner with fallback
        try:
            llm_cloner = LLMWebsiteCloner()
            logger.info(f"Using LLMWebsiteCloner for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM cloner for task {task_id}: {str(e)}")
            raise Exception(f"Failed to initialize AI cloner: {str(e)}")
        
        # Generate clone with timeout
        try:
            if preferences and hasattr(llm_cloner, 'generate_enhanced_clone'):
                clone_result = await asyncio.wait_for(
                    llm_cloner.generate_enhanced_clone(scraped_data, url, preferences),
                    timeout=600  # 10 minute timeout
                )
            else:
                clone_result = await asyncio.wait_for(
                    llm_cloner.clone_website(scraped_data, url),
                    timeout=600  # 10 minute timeout
                )
            logger.info(f"Successfully generated clone for task {task_id}")
        except asyncio.TimeoutError:
            raise Exception("AI processing timeout - clone generation took too long")
        except Exception as e:
            logger.error(f"Clone generation failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to generate clone: {str(e)}")
        
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
            "message": "Website cloned successfully! You can now preview and download the files.",
            "result": clone_result,
            "files_ready": True,
            "updated_at": time.time(),
            "access_urls": {
                "preview": f"/preview/{task_id}",
                "source": f"/source/{task_id}",
                "download": f"/download/{task_id}"
            }
        })
        
        logger.info(f"Successfully completed clone task {task_id}")
        
    except Exception as e:
        # Handle errors
        error_message = str(e)
        logger.error(f"Clone task {task_id} failed: {error_message}")
        logger.error(traceback.format_exc())
        
        tasks[task_id].update({
            "status": "failed",
            "progress": 0.0,
            "message": "Cloning failed",
            "error": error_message,
            "updated_at": time.time()
        })

async def create_zip_file(task_id: str, files: Dict[str, Dict]) -> str:
    """Create a zip file containing all generated files"""
    try:
        # Create temporary zip file
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"website_clone_{task_id[:8]}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, file_info in files.items():
                content = file_info.get("content", "")
                zipf.writestr(filename, content)
        
        logger.info(f"Created zip file for task {task_id}")
        return zip_path
    except Exception as e:
        logger.error(f"Failed to create zip file for task {task_id}: {str(e)}")
        raise

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
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    
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
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error(f"Middleware error: {str(e)}")
        process_time = time.time() - start_time
        return JSONResponse(
            status_code=500,
            content={
                "error": "Request processing error",
                "message": str(e),
                "process_time": process_time
            }
        )

# Health check for container orchestration
@app.get("/healthz")
async def kubernetes_health_check():
    """Kubernetes health check endpoint"""
    return {"status": "ok", "timestamp": time.time()}

# Readiness check
@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if required environment variables are set
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            return JSONResponse(
                status_code=503,
                content={"status": "not ready", "reason": "ANTHROPIC_API_KEY not configured"}
            )
        
        # Check if critical modules are available
        if not WebsiteScraper:
            return JSONResponse(
                status_code=503,
                content={"status": "not ready", "reason": "WebsiteScraper module not available"}
            )
        
        return {"status": "ready", "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "reason": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    
    # Check if we can import required modules
    if not WebsiteScraper:
        logger.error("WebsiteScraper not available - some functionality will be limited")
    
    if not LLMWebsiteCloner:
        logger.error("LLMWebsiteCloner not available - cloning functionality will be limited")
    
    logger.info("Starting Orchids Website Cloner API...")
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)
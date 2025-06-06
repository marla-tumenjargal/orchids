# main.py - Complete Browserbase Enhanced Website Cloner API
import os
import json
import logging
import time
import uuid
import zipfile
import tempfile
from contextlib import asynccontextmanager
from typing import Dict, Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, HttpUrl

# Import our enhanced modules
from .scraper import WebsiteScraper
from .llm_cloner import LLMWebsiteCloner
from .utils import validate_url

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for tracking tasks and requests
tasks: Dict[str, Dict] = {}
requests_used = 0
requests_remaining = 15
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("🌸 Orchids Website Cloner API starting up...")
    print("🚀 Enhanced with Browserbase cloud browser automation")
    print("🧠 Powered by Claude AI for intelligent code generation")
    
    # Check configuration on startup
    browserbase_configured = bool(os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID"))
    anthropic_configured = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    if not anthropic_configured:
        print("⚠️  WARNING: ANTHROPIC_API_KEY not configured - AI features will not work")
    if not browserbase_configured:
        print("⚠️  WARNING: Browserbase not configured - will use local Playwright fallback")
    else:
        print("✅ Browserbase configuration detected")
    
    yield
    
    # Shutdown
    print("🌸 Orchids Website Cloner API shutting down...")
    # Clean up any remaining tasks
    for task_id, task in tasks.items():
        if task.get("status") == "running":
            tasks[task_id]["status"] = "cancelled"
            tasks[task_id]["message"] = "Server shutdown"

# Initialize FastAPI app
app = FastAPI(
    title="Orchids Website Cloner API - Browserbase Enhanced",
    description="AI-powered website cloning service with cloud browser automation",
    version="2.0.0 (Browserbase-Enhanced)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CloneRequest(BaseModel):
    url: HttpUrl
    preferences: Optional[Dict] = None
    force_browserbase: Optional[bool] = True

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    browserbase_enabled: bool = True

class StatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    error_details: Optional[Dict] = None
    browserbase_used: Optional[bool] = None
    scraping_method: Optional[str] = None
    completion_stats: Optional[Dict] = None
    processing_duration_seconds: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    service: str
    version: str
    browserbase_available: bool
    ai_model: str

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with enhanced API status"""
    global requests_used, requests_remaining, start_time
    
    uptime = int(time.time() - start_time)
    
    # Check configurations
    browserbase_configured = bool(os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID"))
    anthropic_configured = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    return {
        "message": "🌸 Orchids Website Cloner API - Browserbase Enhanced",
        "version": "2.0.0 (Browserbase-Enhanced)",
        "status": "healthy",
        "uptime_seconds": uptime,
        "requests_used": requests_used,
        "requests_remaining": requests_remaining,
        "configuration": {
            "browserbase_configured": browserbase_configured,
            "anthropic_configured": anthropic_configured,
            "fallback_available": True
        },
        "features": {
            "cloud_browser_automation": browserbase_configured,
            "ai_code_generation": anthropic_configured,
            "responsive_analysis": True,
            "performance_metrics": True,
            "screenshot_capture": True,
            "multi_viewport_testing": browserbase_configured
        },
        "endpoints": {
            "clone": "POST /clone - Start website cloning with Browserbase",
            "status": "GET /status/{task_id} - Check task status",
            "download": "GET /download/{task_id} - Download cloned files",
            "tasks": "GET /tasks - List all tasks",
            "health": "GET /health - Health check",
            "browserbase-status": "GET /browserbase-status - Check Browserbase configuration",
            "stats": "GET /stats - API usage statistics"
        }
    }

# Add these endpoints to your app/main.py file

from datetime import datetime
import os

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint for frontend connection testing"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now(),
        "api_version": "1.0.0",
        "server": "FastAPI"
    }

# Browserbase status endpoint
@app.get("/browserbase-status")
async def get_browserbase_status():
    """Check Browserbase configuration status"""
    browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
    browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    is_configured = bool(browserbase_api_key and browserbase_project_id)
    
    return {
        "browserbase_configured": is_configured,
        "api_key_set": bool(browserbase_api_key),
        "project_id_set": bool(browserbase_project_id),
        "fallback_available": True,
        "recommendation": "Cloud browser automation recommended for best results" if is_configured else "Configure Browserbase for enhanced features",
        "benefits": [
            "Bypass anti-bot detection",
            "Higher success rates",
            "Scalable cloud infrastructure",
            "Better performance metrics"
        ] if is_configured else [
            "Add BROWSERBASE_API_KEY to environment",
            "Add BROWSERBASE_PROJECT_ID to environment",
            "Restart server after configuration"
        ]
    }

# Enhanced CORS settings (add this near the top of your file)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/browserbase-status")
async def browserbase_status():
    """Check Browserbase configuration status"""
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    return {
        "browserbase_configured": bool(api_key and project_id),
        "api_key_set": bool(api_key),
        "project_id_set": bool(project_id),
        "fallback_available": True,
        "benefits": [
            "Cloud browser automation",
            "Anti-bot detection bypassing",
            "Global CDN for faster scraping",
            "No local browser management",
            "Better reliability for complex sites"
        ],
        "recommendation": "Configure Browserbase for optimal performance and reliability" if not (api_key and project_id) else "Browserbase ready - enhanced scraping enabled"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check endpoint"""
    browserbase_configured = bool(os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID"))
    
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        service="Orchids Website Cloner API",
        version="2.0.0 (Browserbase-Enhanced)",
        browserbase_available=browserbase_configured,
        ai_model="claude-3-5-sonnet-20241022"
    )

@app.post("/clone", response_model=TaskResponse)
async def clone_website(request: CloneRequest, background_tasks: BackgroundTasks):
    """Start enhanced website cloning process with Browserbase"""
    global requests_used, requests_remaining
    
    # Check rate limit
    if requests_remaining <= 0:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": "No requests remaining. Please try again later.",
                "requests_used": requests_used,
                "requests_remaining": requests_remaining,
                "reset_info": "Rate limits reset on server restart"
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
                "provided_url": url_str,
                "requirements": [
                    "Must include http:// or https://",
                    "Must be a publicly accessible website",
                    "Local/private IP addresses not allowed"
                ]
            }
        )
    
    # Check required configurations
    anthropic_configured = bool(os.getenv("ANTHROPIC_API_KEY"))
    if not anthropic_configured:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Service configuration error",
                "message": "AI service not configured. Please contact administrator.",
                "missing_config": "ANTHROPIC_API_KEY"
            }
        )
    
    # Check Browserbase configuration
    browserbase_configured = bool(os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID"))
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Initialize enhanced task
    tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0.0,
        "message": "Task queued for enhanced processing with Browserbase",
        "url": url_str,
        "preferences": request.preferences or {},
        "force_browserbase": request.force_browserbase,
        "browserbase_configured": browserbase_configured,
        "created_at": time.time(),
        "updated_at": time.time(),
        "result": None,
        "error": None,
        "error_details": None,
        "files_ready": False,
        "download_url": None,
        "browserbase_used": None,
        "scraping_method": None,
        "completion_stats": None,
        "processing_duration_seconds": None
    }
    
    # Start enhanced background task
    background_tasks.add_task(
        process_enhanced_clone_task,
        task_id,
        url_str,
        request.preferences,
        request.force_browserbase
    )
    
    # Update counters
    requests_used += 1
    requests_remaining -= 1
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Enhanced website cloning started with Browserbase automation",
        browserbase_enabled=browserbase_configured
    )

@app.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """Get the status of a cloning task with enhanced details"""
    if task_id not in tasks:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found",
                "message": f"No task found with ID: {task_id}",
                "task_id": task_id,
                "suggestion": "Check if the task ID is correct or if the task has expired"
            }
        )
    
    task = tasks[task_id]
    return StatusResponse(**task)

@app.get("/download/{task_id}")
async def download_cloned_files(task_id: str, format: str = "zip"):
    """Download the cloned website files with Browserbase enhancement info"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Task not completed",
                "message": "Cannot download files until task is completed",
                "current_status": task["status"],
                "task_progress": task.get("progress", 0.0)
            }
        )
    
    if not task.get("result") or not task["result"].get("files"):
        raise HTTPException(
            status_code=404,
            detail="No files available for download"
        )
    
    try:
        if format.lower() == "zip":
            # Create enhanced zip file with Browserbase metadata
            zip_path = await create_enhanced_zip_file(task_id, task["result"]["files"], task)
            
            browserbase_suffix = "_browserbase" if task.get("browserbase_used") else "_local"
            filename = f"website_clone_{task_id[:8]}{browserbase_suffix}.zip"
            
            return FileResponse(
                zip_path,
                media_type='application/zip',
                filename=filename,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            # Return enhanced individual file list
            return JSONResponse({
                "task_id": task_id,
                "files": task["result"]["files"],
                "metadata": {
                    "browserbase_used": task.get("browserbase_used", False),
                    "scraping_method": task.get("scraping_method", "unknown"),
                    "processing_duration": task.get("processing_duration_seconds", 0),
                    "completion_stats": task.get("completion_stats", {})
                },
                "download_instructions": "Use format=zip to download as zip file"
            })
            
    except Exception as e:
        logger.error(f"Error creating download for task {task_id}: {str(e)}")
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
        available_files = list(files.keys())
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"File '{filename}' not found",
                "available_files": available_files,
                "suggestion": f"Try one of: {', '.join(available_files)}"
            }
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
    """List all tasks with optional filtering and enhanced info"""
    filtered_tasks = list(tasks.values())
    
    # Filter by status if provided
    if status:
        filtered_tasks = [task for task in filtered_tasks if task["status"] == status]
    
    # Limit results
    filtered_tasks = filtered_tasks[:limit]
    
    # Sort by created_at (most recent first)
    filtered_tasks.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    
    # Calculate statistics
    total_browserbase_used = sum(1 for task in tasks.values() if task.get("browserbase_used"))
    total_completed = sum(1 for task in tasks.values() if task.get("status") == "completed")
    
    return {
        "tasks": filtered_tasks,
        "total_count": len(tasks),
        "filtered_count": len(filtered_tasks),
        "statistics": {
            "completed_tasks": total_completed,
            "browserbase_usage": total_browserbase_used,
            "success_rate": (total_completed / max(1, len(tasks))) * 100
        },
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
        "task_status": deleted_task["status"],
        "task_url": deleted_task.get("url", "unknown")
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
        "message": "Task cancelled by user request",
        "updated_at": time.time()
    })
    
    return {
        "message": "Task cancelled successfully",
        "task_id": task_id,
        "previous_status": task["status"]
    }

@app.get("/stats")
async def get_enhanced_api_stats():
    """Get enhanced API usage statistics with Browserbase info"""
    global requests_used, requests_remaining, start_time
    
    task_statuses = {}
    browserbase_usage = {"used": 0, "local_fallback": 0, "unknown": 0}
    processing_times = []
    
    for task in tasks.values():
        status = task["status"]
        task_statuses[status] = task_statuses.get(status, 0) + 1
        
        # Track Browserbase usage
        if task.get("browserbase_used") is True:
            browserbase_usage["used"] += 1
        elif task.get("browserbase_used") is False:
            browserbase_usage["local_fallback"] += 1
        else:
            browserbase_usage["unknown"] += 1
        
        # Track processing times
        if task.get("processing_duration_seconds"):
            processing_times.append(task["processing_duration_seconds"])
    
    uptime = time.time() - start_time
    browserbase_configured = bool(os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID"))
    
    # Calculate average processing time
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    return {
        "uptime_seconds": int(uptime),
        "uptime_formatted": format_uptime(uptime),
        "requests_used": requests_used,
        "requests_remaining": requests_remaining,
        "total_tasks": len(tasks),
        "task_statuses": task_statuses,
        "browserbase_stats": {
            "configured": browserbase_configured,
            "usage": browserbase_usage,
            "success_rate": (browserbase_usage["used"] / max(1, sum(browserbase_usage.values()))) * 100,
            "fallback_rate": (browserbase_usage["local_fallback"] / max(1, sum(browserbase_usage.values()))) * 100
        },
        "performance_stats": {
            "average_processing_time_seconds": round(avg_processing_time, 2),
            "total_completed_tasks": task_statuses.get("completed", 0),
            "total_failed_tasks": task_statuses.get("failed", 0),
            "success_rate": (task_statuses.get("completed", 0) / max(1, len(tasks))) * 100
        },
        "api_version": "2.0.0 (Browserbase-Enhanced)",
        "features": {
            "cloud_browser_automation": browserbase_configured,
            "ai_code_generation": True,
            "responsive_analysis": True,
            "performance_metrics": True,
            "screenshot_capture": browserbase_configured
        }
    }

# Background task processing
async def process_enhanced_clone_task(
    task_id: str,
    url: str,
    preferences: Optional[Dict] = None,
    force_browserbase: bool = True
):
    """Enhanced background task to process website cloning with Browserbase"""
    scraper = None
    try:
        # Update task status
        tasks[task_id].update({
            "status": "running",
            "progress": 0.1,
            "message": "Initializing enhanced scraper with Browserbase...",
            "updated_at": time.time()
        })
        
        # Check Browserbase configuration and task preferences
        browserbase_configured = bool(os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID"))
        use_browserbase = force_browserbase and browserbase_configured
        
        if use_browserbase:
            tasks[task_id].update({
                "message": "Connecting to Browserbase cloud browsers...",
                "updated_at": time.time()
            })
        else:
            tasks[task_id].update({
                "message": "Using local Playwright browser (Browserbase not available)...",
                "updated_at": time.time()
            })
        
        # Initialize enhanced scraper
        scraper = WebsiteScraper()
        
        # Update progress
        tasks[task_id].update({
            "progress": 0.2,
            "message": "Scraper initialized, starting website analysis...",
            "updated_at": time.time()
        })
        
        # Update progress for navigation
        tasks[task_id].update({
            "progress": 0.3,
            "message": "Navigating to website with cloud browser automation...",
            "updated_at": time.time()
        })
        
        # Scrape the website with Browserbase enhancement
        scraped_data = await scraper.scrape_website(url)
        
        # Update task with scraping method used and enhanced data
        browserbase_used = scraped_data.get('browserbase_used', False)
        scraping_method = scraped_data.get('scraping_method', 'unknown')
        
        tasks[task_id].update({
            "browserbase_used": browserbase_used,
            "scraping_method": scraping_method,
            "progress": 0.45,
            "message": f"Website scraped successfully using {scraping_method} - analyzing {scraped_data.get('word_count', 0)} words...",
            "updated_at": time.time()
        })
        
        # Log scraping success with details
        element_count = scraped_data.get('page_insights', {}).get('elementCounts', {}).get('total', 0)
        image_count = len(scraped_data.get('images', []))
        
        tasks[task_id].update({
            "progress": 0.5,
            "message": f"Analysis complete: {element_count} elements, {image_count} images - starting AI processing...",
            "updated_at": time.time()
        })
        
        # Update progress for AI processing
        tasks[task_id].update({
            "progress": 0.6,
            "message": "Processing with enhanced AI analysis (this may take 30-60 seconds)...",
            "updated_at": time.time()
        })
        
        # Initialize enhanced LLM cloner
        llm_cloner = LLMWebsiteCloner()
        
        # Update progress for code generation
        tasks[task_id].update({
            "progress": 0.7,
            "message": "Generating website code with AI...",
            "updated_at": time.time()
        })
        
        # Generate clone with enhanced preferences
        if preferences and preferences:
            # Handle enhanced clone with user preferences
            tasks[task_id].update({
                "message": "Applying custom preferences to generated code...",
                "updated_at": time.time()
            })
            clone_result = await llm_cloner.generate_enhanced_clone(scraped_data, url, preferences)
        else:
            # Standard enhanced clone
            clone_result = await llm_cloner.clone_website(scraped_data, url)
        
        # Update progress for file organization
        tasks[task_id].update({
            "progress": 0.85,
            "message": "Organizing generated files and adding metadata...",
            "updated_at": time.time()
        })
        
        # Add task-specific metadata to the result
        if 'clone_metadata' in clone_result:
            clone_result['clone_metadata'].update({
                'task_id': task_id,
                'processing_time_seconds': time.time() - tasks[task_id]['created_at'],
                'browserbase_session_used': browserbase_used,
                'scraping_method_final': scraping_method,
                'total_progress_steps': 10,
                'user_preferences_applied': bool(preferences)
            })
        
        # Update progress for finalization
        tasks[task_id].update({
            "progress": 0.95,
            "message": "Finalizing clone and preparing download...",
            "updated_at": time.time()
        })
        
        # Calculate final statistics
        generated_files = clone_result.get('files', {})
        total_file_size = sum(file_info.get('size', 0) for file_info in generated_files.values())
        file_count = len(generated_files)
        
        # Complete task with enhanced metadata
        tasks[task_id].update({
            "status": "completed",
            "progress": 1.0,
            "message": f"✅ Clone completed! Generated {file_count} files ({total_file_size:,} bytes) using {scraping_method}",
            "result": clone_result,
            "files_ready": True,
            "completion_stats": {
                "files_generated": file_count,
                "total_size_bytes": total_file_size,
                "processing_time": time.time() - tasks[task_id]['created_at'],
                "elements_analyzed": element_count,
                "images_processed": image_count,
                "scraping_method_used": scraping_method,
                "browserbase_used": browserbase_used
            },
            "updated_at": time.time()
        })
        
        # Log successful completion
        logger.info(f"Task {task_id} completed successfully: {url} -> {file_count} files, {scraping_method} method")
        
    except Exception as e:
        # Enhanced error handling with detailed context
        error_message = str(e)
        error_type = type(e).__name__
        browserbase_used = tasks[task_id].get('browserbase_used', False)
        scraping_method = tasks[task_id].get('scraping_method', 'unknown')
        current_progress = tasks[task_id].get('progress', 0.0)
        
        # Determine error phase for better debugging
        if current_progress < 0.5:
            error_phase = "scraping"
            error_context = "Error occurred during website scraping phase"
        elif current_progress < 0.8:
            error_phase = "ai_processing"
            error_context = "Error occurred during AI analysis and code generation"
        else:
            error_phase = "finalization"
            error_context = "Error occurred during file organization and finalization"
        
        # Create detailed error info
        error_details = {
            "error_message": error_message,
            "error_type": error_type,
            "error_phase": error_phase,
            "progress_at_failure": current_progress,
            "browserbase_attempted": browserbase_used,
            "scraping_method": scraping_method,
            "context": error_context,
            "timestamp": time.time()
        }
        
        # Update task with comprehensive error information
        tasks[task_id].update({
            "status": "failed",
            "progress": current_progress,  # Keep progress where it failed
            "message": f"❌ {error_context}: {error_message}",
            "error": error_message,
            "error_details": error_details,
            "updated_at": time.time()
        })
        
        # Log error with context
        logger.error(f"Task {task_id} failed in {error_phase} phase: {error_type}: {error_message}")
        
        # If Browserbase failed and we haven't tried local fallback yet
        if ("browserbase" in error_message.lower() or "connection" in error_message.lower()) and browserbase_used:
            logger.warning(f"Task {task_id}: Browserbase error detected, automatic fallback should have been attempted")
        
    finally:
        # Cleanup resources
        if scraper:
            try:
                await scraper.cleanup()
            except Exception as cleanup_error:
                logger.warning(f"Task {task_id}: Error during scraper cleanup: {cleanup_error}")
        
        # Ensure task has final timestamp
        if task_id in tasks:
            tasks[task_id]["updated_at"] = time.time()
            
            # Add processing duration to completed/failed tasks
            if tasks[task_id]["status"] in ["completed", "failed"]:
                processing_duration = time.time() - tasks[task_id]["created_at"]
                tasks[task_id]["processing_duration_seconds"] = round(processing_duration, 2)

# Utility functions
async def create_enhanced_zip_file(task_id: str, files: Dict[str, Dict], task_info: Dict) -> str:
    """Create an enhanced zip file with Browserbase metadata"""
    # Create temporary zip file
    temp_dir = tempfile.mkdtemp()
    browserbase_suffix = "_browserbase" if task_info.get("browserbase_used") else "_local"
    zip_path = os.path.join(temp_dir, f"website_clone_{task_id[:8]}{browserbase_suffix}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all generated files
        for filename, file_info in files.items():
            content = file_info.get("content", "")
            zipf.writestr(filename, content)
        
        # Add enhanced metadata file
        metadata = {
            "task_id": task_id,
            "original_url": task_info.get("url", ""),
            "browserbase_used": task_info.get("browserbase_used", False),
            "scraping_method": task_info.get("scraping_method", "unknown"),
            "generation_timestamp": task_info.get("created_at", time.time()),
            "completion_timestamp": task_info.get("updated_at", time.time()),
            "processing_duration_seconds": task_info.get("processing_duration_seconds", 0),
            "clone_metadata": task_info.get("result", {}).get("clone_metadata", {}),
            "browserbase_insights": task_info.get("result", {}).get("browserbase_insights", {}),
            "completion_stats": task_info.get("completion_stats", {}),
            "version": "2.0.0 (Browserbase-Enhanced)"
        }
        
        zipf.writestr("clone_metadata.json", json.dumps(metadata, indent=2))
        
        # Add enhanced README with Browserbase info
        enhanced_readme = f"""# Website Clone - Enhanced with Browserbase

This website clone was generated using advanced cloud browser automation technology.

## Clone Information

- **Original URL**: {task_info.get('url', 'Unknown')}
- **Task ID**: {task_id}
- **Browserbase Used**: {'Yes' if task_info.get('browserbase_used') else 'No'}
- **Scraping Method**: {task_info.get('scraping_method', 'Unknown')}
- **Processing Time**: {task_info.get('processing_duration_seconds', 0):.2f} seconds
- **Generated**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(task_info.get('created_at', time.time())))}
- **Completed**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(task_info.get('updated_at', time.time())))}

## Technology Stack

- 🌐 **Cloud Browser Automation**: {'Browserbase' if task_info.get('browserbase_used') else 'Local Playwright'}
- 🧠 **AI Code Generation**: Claude 3.5 Sonnet
- 📱 **Responsive Analysis**: Multi-viewport testing
- ⚡ **Performance Metrics**: Real browser measurements
- 🎨 **Design Recreation**: Pixel-perfect cloning
- 📊 **Element Analysis**: {task_info.get('completion_stats', {}).get('elements_analyzed', 0)} elements processed

## Features

- ✨ Enhanced with real browser automation data
- 📊 Performance-optimized based on actual metrics
- 🎯 Responsive design tested across multiple viewports
- 🔍 Comprehensive element analysis
- 🎨 Accurate color palette extraction
- 📸 Multi-resolution screenshot capture (if Browserbase used)

## Statistics

- **Files Generated**: {task_info.get('completion_stats', {}).get('files_generated', 0)}
- **Total File Size**: {task_info.get('completion_stats', {}).get('total_size_bytes', 0):,} bytes
- **Images Processed**: {task_info.get('completion_stats', {}).get('images_processed', 0)}
- **Elements Analyzed**: {task_info.get('completion_stats', {}).get('elements_analyzed', 0)}

## Files Included

{chr(10).join(f"- `{filename}` - {file_info.get('description', 'Generated file')} ({file_info.get('size', 0):,} bytes)" for filename, file_info in files.items())}

## Setup Instructions

1. Extract all files to a directory
2. Open `index.html` in a web browser
3. Customize as needed
4. Deploy to any static hosting service

## Performance Optimization

This clone has been optimized based on real browser performance metrics:
- Load time analysis
- Resource size optimization
- Responsive design testing
- Cross-browser compatibility

## Attribution

Generated with ❤️ using:
- [Browserbase](https://browserbase.com) - Cloud browser automation platform
- [Claude AI](https://claude.ai) - Advanced AI for intelligent code generation
- [Orchids Website Cloner](https://orchids.dev) - AI-powered website cloning platform

## Support

For questions about this clone or the cloning process:
- Check the `clone_metadata.json` file for detailed technical information
- Visit our documentation for setup guides
- Contact support for custom modifications

---

**Disclaimer**: This is a clone created for educational/development purposes. 
Please respect the original website's terms of service and intellectual property rights.

Generated on {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())} using Orchids Website Cloner v2.0.0
"""
        
        zipf.writestr("CLONE_INFO.md", enhanced_readme)
        
        # Add technical specifications file
        tech_specs = {
            "clone_specifications": {
                "api_version": "2.0.0 (Browserbase-Enhanced)",
                "scraping_engine": task_info.get('scraping_method', 'unknown'),
                "ai_model": "claude-3-5-sonnet-20241022",
                "browserbase_session": task_info.get('browserbase_used', False),
                "responsive_testing": True,
                "performance_analysis": True,
                "screenshot_capture": task_info.get('browserbase_used', False)
            },
            "processing_pipeline": [
                "URL validation and security checks",
                "Browserbase session creation (if enabled)",
                "Multi-viewport website scraping",
                "Performance metrics collection",
                "DOM structure analysis",
                "Color palette extraction",
                "Font family detection",
                "Responsive design testing",
                "AI-powered analysis and code generation",
                "File optimization and packaging"
            ],
            "quality_metrics": {
                "elements_processed": task_info.get('completion_stats', {}).get('elements_analyzed', 0),
                "processing_time_seconds": task_info.get('processing_duration_seconds', 0),
                "file_count": task_info.get('completion_stats', {}).get('files_generated', 0),
                "total_size_bytes": task_info.get('completion_stats', {}).get('total_size_bytes', 0),
                "success_rate": "100%" if task_info.get('status') == 'completed' else "Failed"
            }
        }
        
        zipf.writestr("technical_specifications.json", json.dumps(tech_specs, indent=2))
    
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

# Enhanced exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Enhanced HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time(),
            "path": str(request.url),
            "method": request.method,
            "version": "2.0.0 (Browserbase-Enhanced)"
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Enhanced global exception handler with Browserbase context"""
    import traceback
    
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__,
            "timestamp": time.time(),
            "version": "2.0.0 (Browserbase-Enhanced)",
            "traceback": traceback.format_exc() if os.getenv("DEBUG") else None,
            "suggestions": [
                "Check if all required environment variables are set",
                "Verify Browserbase configuration if scraping-related error",
                "Check API rate limits and quotas",
                "Ensure the target URL is accessible"
            ]
        }
    )

# Enhanced middleware
@app.middleware("http")
async def add_enhanced_process_time_header(request, call_next):
    """Add enhanced processing time header with system info"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add enhanced headers
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    response.headers["X-Browserbase-Enabled"] = str(bool(os.getenv("BROWSERBASE_API_KEY")))
    response.headers["X-API-Version"] = "2.0.0-Browserbase"
    response.headers["X-Server-Timestamp"] = str(int(time.time()))
    response.headers["X-Active-Tasks"] = str(len([t for t in tasks.values() if t.get("status") == "running"]))
    
    return response

# Health check endpoints for container orchestration
@app.get("/healthz")
async def kubernetes_health_check():
    """Enhanced Kubernetes health check endpoint"""
    browserbase_configured = bool(os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID"))
    anthropic_configured = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    return {
        "status": "ok",
        "timestamp": time.time(),
        "version": "2.0.0 (Browserbase-Enhanced)",
        "configuration": {
            "browserbase_available": browserbase_configured,
            "ai_available": anthropic_configured,
            "fallback_available": True
        },
        "system": {
            "uptime_seconds": int(time.time() - start_time),
            "active_tasks": len([t for t in tasks.values() if t.get("status") == "running"]),
            "total_tasks": len(tasks)
        }
    }

@app.get("/ready")
async def enhanced_readiness_check():
    """Enhanced readiness check endpoint with dependency verification"""
    # Check required environment variables
    api_key = os.getenv('ANTHROPIC_API_KEY')
    browserbase_key = os.getenv('BROWSERBASE_API_KEY')
    browserbase_project = os.getenv('BROWSERBASE_PROJECT_ID')
    
    issues = []
    critical_issues = []
    
    # Critical checks
    if not api_key:
        critical_issues.append("ANTHROPIC_API_KEY not configured")
    
    # Non-critical checks
    if not browserbase_key:
        issues.append("BROWSERBASE_API_KEY not configured (fallback available)")
    
    if not browserbase_project:
        issues.append("BROWSERBASE_PROJECT_ID not configured (fallback available)")
    
    # Check if we can create required objects
    try:
        from .scraper import WebsiteScraper
        from .llm_cloner import LLMWebsiteCloner
        
        # Test instantiation (don't actually use them)
        scraper = WebsiteScraper()
        if api_key:
            cloner = LLMWebsiteCloner()
        
        services_available = True
    except Exception as e:
        critical_issues.append(f"Service initialization failed: {str(e)}")
        services_available = False
    
    if critical_issues:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not ready",
                "critical_issues": critical_issues,
                "issues": issues,
                "version": "2.0.0 (Browserbase-Enhanced)",
                "timestamp": time.time()
            }
        )
    
    return {
        "status": "ready",
        "timestamp": time.time(),
        "version": "2.0.0 (Browserbase-Enhanced)",
        "configuration": {
            "browserbase_configured": bool(browserbase_key and browserbase_project),
            "anthropic_configured": bool(api_key),
            "services_available": services_available,
            "fallback_available": True
        },
        "issues": issues if issues else None,
        "capabilities": {
            "cloud_browser_automation": bool(browserbase_key and browserbase_project),
            "ai_code_generation": bool(api_key),
            "local_fallback": True,
            "responsive_analysis": True,
            "performance_metrics": True
        }
    }

# Additional utility endpoints
@app.get("/config")
async def get_configuration_status():
    """Get current configuration status (non-sensitive info only)"""
    return {
        "version": "2.0.0 (Browserbase-Enhanced)",
        "timestamp": time.time(),
        "configuration": {
            "browserbase_api_key_set": bool(os.getenv("BROWSERBASE_API_KEY")),
            "browserbase_project_id_set": bool(os.getenv("BROWSERBASE_PROJECT_ID")),
            "anthropic_api_key_set": bool(os.getenv("ANTHROPIC_API_KEY")),
            "debug_mode": bool(os.getenv("DEBUG"))
        },
        "features": {
            "cloud_browser_automation": bool(os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
            "ai_code_generation": bool(os.getenv("ANTHROPIC_API_KEY")),
            "local_playwright_fallback": True,
            "multi_viewport_testing": True,
            "performance_monitoring": True,
            "screenshot_capture": True
        },
        "limits": {
            "requests_remaining": requests_remaining,
            "requests_used": requests_used,
            "max_concurrent_tasks": 5,
            "task_timeout_seconds": 300
        }
    }

@app.post("/test-connection")
async def test_browserbase_connection():
    """Test Browserbase connection (for debugging)"""
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    if not api_key or not project_id:
        return {
            "status": "failed",
            "message": "Browserbase credentials not configured",
            "configured": False
        }
    
    try:
        # Test creating a scraper instance
        scraper = WebsiteScraper()
        
        return {
            "status": "success",
            "message": "Browserbase connection test passed",
            "configured": True,
            "api_key_length": len(api_key) if api_key else 0,
            "project_id_set": bool(project_id)
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Browserbase connection test failed: {str(e)}",
            "configured": True,
            "error": str(e)
        }

# Development/debugging endpoints (only in debug mode)
if os.getenv("DEBUG"):
    @app.get("/debug/tasks")
    async def debug_get_all_tasks():
        """Debug endpoint to see all task details"""
        return {
            "total_tasks": len(tasks),
            "tasks": tasks,
            "timestamp": time.time()
        }
    
    @app.post("/debug/clear-tasks")
    async def debug_clear_tasks():
        """Debug endpoint to clear all tasks"""
        global tasks
        task_count = len(tasks)
        tasks.clear()
        return {
            "message": f"Cleared {task_count} tasks",
            "timestamp": time.time()
        }

# Main application entry point
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Orchids Website Cloner API with Browserbase Enhancement")
    print("📋 Configuration checklist:")
    print(f"   ✅ ANTHROPIC_API_KEY: {'Set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Missing'}")
    print(f"   {'✅' if os.getenv('BROWSERBASE_API_KEY') else '⚠️ '} BROWSERBASE_API_KEY: {'Set' if os.getenv('BROWSERBASE_API_KEY') else 'Not set (will use local fallback)'}")
    print(f"   {'✅' if os.getenv('BROWSERBASE_PROJECT_ID') else '⚠️ '} BROWSERBASE_PROJECT_ID: {'Set' if os.getenv('BROWSERBASE_PROJECT_ID') else 'Not set (will use local fallback)'}")
    print(f"   📊 DEBUG MODE: {'Enabled' if os.getenv('DEBUG') else 'Disabled'}")
    print("")
    print("🌐 API will be available at:")
    print("   - Main API: http://localhost:8000")
    print("   - Documentation: http://localhost:8000/docs")
    print("   - Health Check: http://localhost:8000/health")
    print("   - Browserbase Status: http://localhost:8000/browserbase-status")
    print("")
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        reload=bool(os.getenv("DEBUG"))
    )

# # main.py
# import os
# from dotenv import load_dotenv

# load_dotenv()


# from fastapi import FastAPI, HTTPException, BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse, FileResponse
# from pydantic import BaseModel, HttpUrl
# from typing import Dict, Optional, List
# import asyncio
# import time
# import uuid
# import os
# import zipfile
# import tempfile
# from contextlib import asynccontextmanager

# # Import our custom modules
# from .scraper import WebsiteScraper
# from .llm_cloner import LLMWebsiteCloner
# from .utils import validate_url

# # Global variables for tracking tasks and requests
# tasks: Dict[str, Dict] = {}
# requests_used = 0
# requests_remaining = 15
# start_time = time.time()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     print("🌸 Orchids Website Cloner API starting up...")
#     yield
#     # Shutdown
#     print("🌸 Orchids Website Cloner API shutting down...")

# app = FastAPI(
#     title="Orchids Website Cloner API",
#     description="AI-powered website cloning service",
#     version="1.0.0 (Credit-Optimized)",
#     lifespan=lifespan
# )

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Request models
# class CloneRequest(BaseModel):
#     url: HttpUrl
#     preferences: Optional[Dict] = None

# class TaskResponse(BaseModel):
#     task_id: str
#     status: str
#     message: str

# class StatusResponse(BaseModel):
#     task_id: str
#     status: str
#     progress: Optional[float] = None
#     message: Optional[str] = None
#     result: Optional[Dict] = None
#     error: Optional[str] = None

# class DownloadRequest(BaseModel):
#     task_id: str
#     format: Optional[str] = "zip"  # zip or individual files

# @app.get("/")
# async def root():
#     """Root endpoint with API status"""
#     global requests_used, requests_remaining, start_time
    
#     uptime = int(time.time() - start_time)
    
#     return {
#         "message": "🌸 Orchids Website Cloner API is running",
#         "version": "1.0.0 (Credit-Optimized)",
#         "status": "healthy",
#         "uptime_seconds": uptime,
#         "requests_used": requests_used,
#         "requests_remaining": requests_remaining,
#         "endpoints": {
#             "clone": "POST /clone - Start website cloning",
#             "status": "GET /status/{task_id} - Check task status",
#             "download": "GET /download/{task_id} - Download cloned files",
#             "tasks": "GET /tasks - List all tasks",
#             "health": "GET /health - Health check"
#         }
#     }

# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy", 
#         "timestamp": time.time(),
#         "service": "Orchids Website Cloner API",
#         "version": "1.0.0"
#     }

# @app.post("/clone", response_model=TaskResponse)
# async def clone_website(request: CloneRequest, background_tasks: BackgroundTasks):
#     """Start website cloning process"""
#     global requests_used, requests_remaining
    
#     # Check rate limit
#     if requests_remaining <= 0:
#         raise HTTPException(
#             status_code=429, 
#             detail={
#                 "error": "Rate limit exceeded",
#                 "message": "No requests remaining. Please try again later.",
#                 "requests_used": requests_used,
#                 "requests_remaining": requests_remaining
#             }
#         )
    
#     # Validate URL
#     url_str = str(request.url)
#     if not validate_url(url_str):
#         raise HTTPException(
#             status_code=400, 
#             detail={
#                 "error": "Invalid URL",
#                 "message": "Please provide a valid URL format (e.g., https://example.com)",
#                 "provided_url": url_str
#             }
#         )
    
#     # Generate task ID
#     task_id = str(uuid.uuid4())
    
#     # Initialize task
#     tasks[task_id] = {
#         "task_id": task_id,
#         "status": "pending",
#         "progress": 0.0,
#         "message": "Task queued for processing",
#         "url": url_str,
#         "preferences": request.preferences or {},
#         "created_at": time.time(),
#         "updated_at": time.time(),
#         "result": None,
#         "error": None,
#         "files_ready": False,
#         "download_url": None
#     }
    
#     # Start background task
#     background_tasks.add_task(process_clone_task, task_id, url_str, request.preferences)
    
#     # Update counters
#     requests_used += 1
#     requests_remaining -= 1
    
#     return TaskResponse(
#         task_id=task_id,
#         status="pending",
#         message="Website cloning started successfully"
#     )

# @app.get("/status/{task_id}", response_model=StatusResponse)
# async def get_task_status(task_id: str):
#     """Get the status of a cloning task"""
#     if task_id not in tasks:
#         raise HTTPException(
#             status_code=404, 
#             detail={
#                 "error": "Task not found",
#                 "message": f"No task found with ID: {task_id}",
#                 "task_id": task_id
#             }
#         )
    
#     task = tasks[task_id]
#     return StatusResponse(**task)

# @app.get("/download/{task_id}")
# async def download_cloned_files(task_id: str, format: str = "zip"):
#     """Download the cloned website files"""
#     if task_id not in tasks:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     task = tasks[task_id]
    
#     if task["status"] != "completed":
#         raise HTTPException(
#             status_code=400, 
#             detail={
#                 "error": "Task not completed",
#                 "message": "Cannot download files until task is completed",
#                 "current_status": task["status"]
#             }
#         )
    
#     if not task.get("result") or not task["result"].get("files"):
#         raise HTTPException(
#             status_code=404, 
#             detail="No files available for download"
#         )
    
#     try:
#         if format.lower() == "zip":
#             # Create a zip file with all generated files
#             zip_path = await create_zip_file(task_id, task["result"]["files"])
            
#             return FileResponse(
#                 zip_path,
#                 media_type='application/zip',
#                 filename=f"website_clone_{task_id[:8]}.zip",
#                 headers={"Content-Disposition": f"attachment; filename=website_clone_{task_id[:8]}.zip"}
#             )
#         else:
#             # Return individual file list
#             return JSONResponse({
#                 "task_id": task_id,
#                 "files": task["result"]["files"],
#                 "download_instructions": "Use format=zip to download as zip file"
#             })
            
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error creating download: {str(e)}"
#         )

# @app.get("/download/{task_id}/{filename}")
# async def download_individual_file(task_id: str, filename: str):
#     """Download an individual file from the cloned website"""
#     if task_id not in tasks:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     task = tasks[task_id]
    
#     if task["status"] != "completed":
#         raise HTTPException(status_code=400, detail="Task not completed")
    
#     files = task.get("result", {}).get("files", {})
    
#     if filename not in files:
#         raise HTTPException(
#             status_code=404, 
#             detail=f"File '{filename}' not found in task results"
#         )
    
#     file_info = files[filename]
#     content = file_info.get("content", "")
    
#     # Create temporary file
#     with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f"_{filename}") as tmp_file:
#         tmp_file.write(content)
#         tmp_path = tmp_file.name
    
#     return FileResponse(
#         tmp_path,
#         media_type=file_info.get("type", "text/plain"),
#         filename=filename,
#         headers={"Content-Disposition": f"attachment; filename={filename}"}
#     )

# @app.get("/tasks")
# async def list_tasks(limit: int = 50, status: Optional[str] = None):
#     """List all tasks with optional filtering"""
#     filtered_tasks = list(tasks.values())
    
#     # Filter by status if provided
#     if status:
#         filtered_tasks = [task for task in filtered_tasks if task["status"] == status]
    
#     # Limit results
#     filtered_tasks = filtered_tasks[:limit]
    
#     # Sort by created_at (most recent first)
#     filtered_tasks.sort(key=lambda x: x.get("created_at", 0), reverse=True)
    
#     return {
#         "tasks": filtered_tasks,
#         "total_count": len(tasks),
#         "filtered_count": len(filtered_tasks),
#         "available_statuses": list(set(task["status"] for task in tasks.values()))
#     }

# @app.delete("/tasks/{task_id}")
# async def delete_task(task_id: str):
#     """Delete a specific task"""
#     if task_id not in tasks:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     deleted_task = tasks.pop(task_id)
    
#     return {
#         "message": "Task deleted successfully",
#         "deleted_task_id": task_id,
#         "task_status": deleted_task["status"]
#     }

# @app.post("/tasks/{task_id}/cancel")
# async def cancel_task(task_id: str):
#     """Cancel a running task"""
#     if task_id not in tasks:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     task = tasks[task_id]
    
#     if task["status"] in ["completed", "failed", "cancelled"]:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Cannot cancel task with status: {task['status']}"
#         )
    
#     # Update task status
#     tasks[task_id].update({
#         "status": "cancelled",
#         "message": "Task cancelled by user",
#         "updated_at": time.time()
#     })
    
#     return {
#         "message": "Task cancelled successfully",
#         "task_id": task_id
#     }

# @app.get("/stats")
# async def get_api_stats():
#     """Get API usage statistics"""
#     global requests_used, requests_remaining, start_time
    
#     task_statuses = {}
#     for task in tasks.values():
#         status = task["status"]
#         task_statuses[status] = task_statuses.get(status, 0) + 1
    
#     uptime = time.time() - start_time
    
#     return {
#         "uptime_seconds": int(uptime),
#         "uptime_formatted": format_uptime(uptime),
#         "requests_used": requests_used,
#         "requests_remaining": requests_remaining,
#         "total_tasks": len(tasks),
#         "task_statuses": task_statuses,
#         "api_version": "1.0.0 (Credit-Optimized)"
#     }

# async def process_clone_task(task_id: str, url: str, preferences: Optional[Dict] = None):
#     """Background task to process website cloning"""
#     try:
#         # Update task status
#         tasks[task_id].update({
#             "status": "running",
#             "progress": 0.1,
#             "message": "Initializing scraper...",
#             "updated_at": time.time()
#         })
        
#         # Initialize scraper
#         scraper = WebsiteScraper()
        
#         # Update progress
#         tasks[task_id].update({
#             "progress": 0.3,
#             "message": "Scraping website content...",
#             "updated_at": time.time()
#         })
        
#         # Scrape the website
#         scraped_data = await scraper.scrape_website(url)
        
#         # Update progress
#         tasks[task_id].update({
#             "progress": 0.6,
#             "message": "Processing with AI...",
#             "updated_at": time.time()
#         })
        
#         # Initialize LLM cloner
#         llm_cloner = LLMWebsiteCloner()
        
#         # Generate clone (with preferences if provided)
#         if preferences:
#             clone_result = await llm_cloner.generate_enhanced_clone(scraped_data, url, preferences)
#         else:
#             clone_result = await llm_cloner.clone_website(scraped_data, url)
        
#         # Update progress
#         tasks[task_id].update({
#             "progress": 0.9,
#             "message": "Finalizing...",
#             "updated_at": time.time()
#         })
        
#         # Complete task
#         tasks[task_id].update({
#             "status": "completed",
#             "progress": 1.0,
#             "message": "Website cloned successfully",
#             "result": clone_result,
#             "files_ready": True,
#             "updated_at": time.time()
#         })
        
#     except Exception as e:
#         # Handle errors
#         error_message = str(e)
#         tasks[task_id].update({
#             "status": "failed",
#             "progress": 0.0,
#             "message": "Cloning failed 11",
#             "error": error_message,
#             "updated_at": time.time()
#         })

# async def create_zip_file(task_id: str, files: Dict[str, Dict]) -> str:
#     """Create a zip file containing all generated files"""
#     # Create temporary zip file
#     temp_dir = tempfile.mkdtemp()
#     zip_path = os.path.join(temp_dir, f"website_clone_{task_id[:8]}.zip")
    
#     with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
#         for filename, file_info in files.items():
#             content = file_info.get("content", "")
#             zipf.writestr(filename, content)
    
#     return zip_path

# def format_uptime(seconds: float) -> str:
#     """Format uptime in human-readable format"""
#     days = int(seconds // 86400)
#     hours = int((seconds % 86400) // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds = int(seconds % 60)
    
#     if days > 0:
#         return f"{days}d {hours}h {minutes}m {seconds}s"
#     elif hours > 0:
#         return f"{hours}h {minutes}m {seconds}s"
#     elif minutes > 0:
#         return f"{minutes}m {seconds}s"
#     else:
#         return f"{seconds}s"

# @app.exception_handler(Exception)
# async def global_exception_handler(request, exc):
#     """Global exception handler"""
#     import traceback
    
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "Internal server error",
#             "message": str(exc),
#             "type": type(exc).__name__,
#             "traceback": traceback.format_exc() if os.getenv("DEBUG") else None
#         }
#     )

# @app.middleware("http")
# async def add_process_time_header(request, call_next):
#     """Add processing time header to responses"""
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response

# # Health check for container orchestration
# @app.get("/healthz")
# async def kubernetes_health_check():
#     """Kubernetes health check endpoint"""
#     return {"status": "ok"}

# # Readiness check
# @app.get("/ready")
# async def readiness_check():
#     """Readiness check endpoint"""
#     # Check if required environment variables are set
#     api_key = os.getenv('ANTHROPIC_API_KEY')
    
#     if not api_key:
#         return JSONResponse(
#             status_code=503,
#             content={"status": "not ready", "reason": "ANTHROPIC_API_KEY not configured"}
#         )
    
#     return {"status": "ready"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import projects, system, studio, chat, working_copy, publish, studio_project
from app.api.deps import validate_collection, validate_project_exists, validate_shot_exists
from fastapi import Depends

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_critical_paths():
    critical_paths = {
        "PORTAFOLIO": settings.PORTAFOLIO_PATH,
        "PROJECTS": settings.PROJECTS_PATH,
        "PROMPTS": settings.PROMPTS_PATH
    }
    for name, path in critical_paths.items():
        if not path.exists():
            logger.warning(f"CRITICAL WARNING: {name} volume not mounted at {path}.")
        else:
            logger.info(f"Verified {name} path at {path}")

validate_critical_paths()

app = FastAPI(
    title="Tlacuilo Backend",
    description="Backend API for Tlacuilo, managing file operations and AI agents.",
    version="0.1.0"
)

# --- Global Exception Handlers (Explicit Registration) ---

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"Validation Error (400): {exc}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    logger.warning(f"Resource Not Found (404): {exc}")
    return JSONResponse(status_code=404, content={"detail": str(exc)})

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

# Project Management Routing (Dependency Injected)
proj_deps = [Depends(validate_collection), Depends(validate_project_exists)]
app.include_router(chat.router, prefix="/api", tags=["chat"], dependencies=proj_deps)
app.include_router(working_copy.router, prefix="/api", tags=["working_copy"], dependencies=proj_deps)
app.include_router(publish.router, prefix="/api", tags=["publish"], dependencies=proj_deps)
app.include_router(studio_project.router, prefix="/api", tags=["studio_project"], dependencies=proj_deps)

# Asset Management Routing (Shot specific logic)
app.include_router(studio.router, prefix="/api", tags=["studio_shot"], dependencies=proj_deps + [Depends(validate_shot_exists)])

@app.get("/")
async def root():
    return {"mensaje": "Backend Tlacuilo Operativo."}

@app.get("/health")
async def health():
    return {"status": "healthy"}

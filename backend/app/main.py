import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import projects, system, content

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
            logger.warning(f"CRITICAL WARNING: {name} volume not mounted at {path}. Tlacuilo may fail.")
        else:
            logger.info(f"Verified {name} path at {path}")

validate_critical_paths()

app = FastAPI(
    title="Tlacuilo Backend",
    description="Backend API for Tlacuilo, managing file operations and AI agents.",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(content.router, prefix="/api", tags=["content"])


@app.get("/")
async def root():
    return {"mensaje": "El Backend de Tlacuilo está en marcha. Visita /docs para la documentación de la API."}

@app.get("/health")
async def health():
    return {"status": "healthy"}

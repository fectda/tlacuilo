from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import projects, system

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


@app.get("/")
async def root():
    return {"mensaje": "El Backend de Tlacuilo está en marcha. Visita /docs para la documentación de la API."}

@app.get("/health")
async def health():
    return {"status": "healthy"}

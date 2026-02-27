from fastapi import APIRouter, Depends
from app.api.deps import get_system_vitals
from app.services.system.vitals import SystemVitalsService

router = APIRouter()

@router.get("/vitals")
async def get_vitals(vitals: SystemVitalsService = Depends(get_system_vitals)):
    """Standardized health check for all core services."""
    return await vitals.get_all_vitals()

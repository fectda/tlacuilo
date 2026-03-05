import logging
from pathlib import Path
from PIL import Image
from app.repositories.project_repository import ProjectRepository
from app.services.studio.shot_manager import StudioShotManager

logger = logging.getLogger(__name__)

class ImageOptimizationService:
    """
    Service responsible for compressing, converting, and deploying 
    approved visual assets to the public portfolio directory.
    """
    
    def __init__(self, repo: ProjectRepository, shot_manager: StudioShotManager):
        self.repo = repo
        self.shot_manager = shot_manager

    def optimize_and_deploy(self, collection: str, slug: str) -> Path:
        """
        Scans approved shots, optimizes them, and moves them to 
        PORTFOLIO_PATH/public/{collection}/{slug}/
        """
        project_dir = self.repo.get_project_dir(collection, slug)
        shots_dir = project_dir / "shots"
        
        # Target directory in the portfolio
        public_dir = self.repo.portfolio_path / "public" / collection / slug
        public_dir.mkdir(parents=True, exist_ok=True)
        
        if not shots_dir.exists():
            logger.info(f"No shots directory found for {slug}. Skipping image optimization.")
            return public_dir

        for shot_path in shots_dir.iterdir():
            if not shot_path.is_dir():
                continue
            
            metadata_file = shot_path / "metadata.json"
            if not metadata_file.exists():
                continue
                
            metadata = self.repo.read_json(metadata_file)
            approved_id = None
            
            for img in metadata.get("images", []):
                if img.get("status") == "approved":
                    approved_id = img.get("id")
                    break
            
            if approved_id:
                source_file = shot_path / f"{approved_id}.png"
                if source_file.exists():
                    # We use the shot_id (folder name) as the filename in public
                    target_file = public_dir / f"{shot_path.name}.webp"
                    self._process_image(source_file, target_file)
                    logger.info(f"Optimized and deployed: {target_file.name}")

        return public_dir

    def _process_image(self, source: Path, target: Path):
        """
        Converts PNG to WebP with optimization.
        """
        try:
            with Image.open(source) as img:
                # Optimized WebP conversion
                img.save(target, "WEBP", quality=85, optimize=True)
        except Exception as e:
            logger.error(f"Failed to process image {source}: {e}")
            # Fallback: simple copy if processing fails? 
            # For now, we prefer to fail this specific file but continue.

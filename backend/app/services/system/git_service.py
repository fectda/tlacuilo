import logging
from pathlib import Path
from typing import List
from git import Repo, exc

logger = logging.getLogger(__name__)

class GitService:
    """
    Dedicated service for Git operations following SOLID principles.
    Handles repository status, staging, commits, and synchronization.
    """
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        try:
            self.repo = Repo(repo_path)
        except exc.InvalidGitRepositoryError:
            logger.error(f"Path {repo_path} is not a valid Git repository.")
            raise ValueError(f"Directorio de Portafolio no es un repositorio Git válido: {repo_path}")

    def ensure_clean_index(self):
        """
        Ensures there are no staged changes before starting a new transaction.
        """
        if self.repo.index.diff("HEAD"):
            logger.warning("Git index is not clean. Aborting publish to prevent contamination.")
            raise ValueError("El índice de Git no está limpio. Hay cambios pendientes que no pertenecen a esta publicación.")

    def add_files(self, files: List[Path]):
        """
        Adds specific files to the git index.
        Paths must be relative to the repository root or absolute within it.
        """
        relative_paths = []
        for f in files:
            try:
                # Ensure the path is relative to the repo root for git add
                rel = f.resolve().relative_to(self.repo_path.resolve())
                relative_paths.append(str(rel))
            except ValueError:
                logger.error(f"File {f} is not within the repository path {self.repo_path}")
                continue
        
        if relative_paths:
            self.repo.index.add(relative_paths)
            logger.info(f"Added {len(relative_paths)} files to git index.")

    def commit(self, message: str):
        """
        Performs a commit with the provided message.
        """
        if not self.repo.index.diff("HEAD"):
             logger.info("No changes to commit.")
             return
             
        self.repo.index.commit(message)
        logger.info(f"Committed changes: {message}")

    def push(self):
        """
        Pushes changes to the remote repository.
        """
        try:
            origin = self.repo.remote(name='origin')
            origin.push()
            logger.info("Changes pushed to remote.")
        except Exception as e:
            logger.error(f"Git push failed: {e}")
            raise RuntimeError(f"Error al sincronizar con el repositorio remoto: {str(e)}")

    def rollback_last_commit(self):
        """
        Utility to undo the last commit in case of push failure.
        """
        self.repo.head.reset('HEAD~1', index=True, working_tree=False)
        logger.info("Rolled back last commit.")

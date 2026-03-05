import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.services.system.git_service import GitService
from app.services.studio.image_service import ImageOptimizationService

@pytest.fixture
def mock_repo_path(tmp_path):
    return tmp_path / "portfolio"

@pytest.fixture
def git_service(mock_repo_path):
    with patch("app.services.system.git_service.Repo") as mock_repo:
        service = GitService(mock_repo_path)
        service.repo = mock_repo.return_value
        return service

def test_git_service_add_files(git_service, mock_repo_path):
    file1 = mock_repo_path / "src/content/bits/es/test.md"
    git_service.add_files([file1])
    git_service.repo.index.add.assert_called_once_with(["src/content/bits/es/test.md"])

def test_git_service_commit(git_service):
    git_service.repo.index.diff.return_value = ["change"]
    git_service.commit("test commit")
    git_service.repo.index.commit.assert_called_once_with("test commit")

@pytest.fixture
def image_service(mock_repo_path):
    mock_repo = MagicMock()
    mock_repo.portfolio_path = mock_repo_path
    mock_shot_manager = MagicMock()
    return ImageOptimizationService(mock_repo, mock_shot_manager)

from app.services.project.publish import ProjectPublishService
from fastapi import HTTPException

@pytest.fixture
def publish_service(image_service, git_service):
    repo = MagicMock()
    cont_validator = MagicMock()
    llm = MagicMock()
    prompts = MagicMock()
    return ProjectPublishService(repo, cont_validator, git_service, image_service, llm, prompts)

@pytest.mark.asyncio
async def test_publish_global_dirty_index(publish_service, git_service):
    # Setup: git index is dirty (ensure_clean_index raises ValueError)
    with patch.object(git_service, 'ensure_clean_index', side_effect=ValueError("Dirty index")):
        # Mock repo to return a state that is not 'publicado'
        publish_service.repo.get_doc_state.return_value = {"doc_status": "promovido"}
        
        # Verify that it raises HTTPException with 400
        with pytest.raises(HTTPException) as excinfo:
            publish_service.publish_global("bits", "test-slug")
        
        assert excinfo.value.status_code == 400
        assert "Dirty index" in str(excinfo.value.detail)

def test_image_optimization_processing(image_service, tmp_path):
    source = tmp_path / "source.png"
    target = tmp_path / "target.webp"
    source.write_text("dummy")
    
    with patch("app.services.studio.image_service.Image.open") as mock_open:
        mock_img = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_img
        
        image_service._process_image(source, target)
        
        mock_img.save.assert_called_once_with(target, "WEBP", quality=85, optimize=True)

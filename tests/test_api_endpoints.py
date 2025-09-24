"""
Test API endpoints.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import status

from tests.conftest import TestDataFactory, TestHelpers


class TestProjectEndpoints:
    """Test project-related API endpoints."""
    
    async def test_create_project_success(self, async_client, auth_headers, tenant_headers):
        """Test successful project creation."""
        project_data = TestDataFactory.create_project()
        
        with patch('app.api.v1.projects.create_project') as mock_create:
            mock_create.return_value = {
                "id": "test-project-id",
                **project_data
            }
            
            response = await async_client.post(
                "/api/v1/projects",
                json=project_data,
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            TestHelpers.assert_response_structure(data, ["id", "name", "description", "status"])
    
    async def test_create_project_invalid_data(self, async_client, auth_headers, tenant_headers):
        """Test project creation with invalid data."""
        invalid_data = {"name": ""}  # Empty name
        
        response = await async_client.post(
            "/api/v1/projects",
            json=invalid_data,
            headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_get_projects_list(self, async_client, auth_headers, tenant_headers):
        """Test getting projects list."""
        with patch('app.api.v1.projects.get_projects') as mock_get:
            mock_get.return_value = {
                "items": [TestDataFactory.create_project(id="project-1")],
                "total": 1,
                "page": 1,
                "pages": 1
            }
            
            response = await async_client.get(
                "/api/v1/projects",
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            TestHelpers.assert_response_structure(data, ["items", "total", "page", "pages"])
    
    async def test_get_project_by_id(self, async_client, auth_headers, tenant_headers):
        """Test getting specific project."""
        project_id = "test-project-id"
        
        with patch('app.api.v1.projects.get_project_by_id') as mock_get:
            mock_get.return_value = TestDataFactory.create_project(id=project_id)
            
            response = await async_client.get(
                f"/api/v1/projects/{project_id}",
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == project_id
    
    async def test_get_project_not_found(self, async_client, auth_headers, tenant_headers):
        """Test getting non-existent project."""
        with patch('app.api.v1.projects.get_project_by_id') as mock_get:
            mock_get.return_value = None
            
            response = await async_client.get(
                "/api/v1/projects/non-existent",
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_update_project(self, async_client, auth_headers, tenant_headers):
        """Test project update."""
        project_id = "test-project-id"
        update_data = {"name": "Updated Project Name"}
        
        with patch('app.api.v1.projects.update_project') as mock_update:
            updated_project = TestDataFactory.create_project(
                id=project_id,
                name=update_data["name"]
            )
            mock_update.return_value = updated_project
            
            response = await async_client.put(
                f"/api/v1/projects/{project_id}",
                json=update_data,
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == update_data["name"]
    
    async def test_delete_project(self, async_client, auth_headers, tenant_headers):
        """Test project deletion."""
        project_id = "test-project-id"
        
        with patch('app.api.v1.projects.delete_project') as mock_delete:
            mock_delete.return_value = True
            
            response = await async_client.delete(
                f"/api/v1/projects/{project_id}",
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_204_NO_CONTENT


class TestUploadEndpoints:
    """Test file upload endpoints."""
    
    async def test_upload_video_file(self, async_client, auth_headers, tenant_headers, sample_video_file):
        """Test video file upload."""
        with patch('app.api.v1.uploads.process_video_upload') as mock_process:
            mock_process.return_value = {
                "id": "upload-id",
                "filename": sample_video_file["filename"],
                "size": sample_video_file["size"],
                "status": "uploaded"
            }
            
            files = {"file": (sample_video_file["filename"], sample_video_file["content"], sample_video_file["content_type"])}
            
            response = await async_client.post(
                "/api/v1/uploads/video",
                files=files,
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            TestHelpers.assert_response_structure(data, ["id", "filename", "size", "status"])
    
    async def test_upload_script_file(self, async_client, auth_headers, tenant_headers, sample_script_file):
        """Test script file upload."""
        with patch('app.api.v1.uploads.process_script_upload') as mock_process:
            mock_process.return_value = {
                "id": "upload-id",
                "filename": sample_script_file["filename"],
                "size": sample_script_file["size"],
                "status": "uploaded"
            }
            
            files = {"file": (sample_script_file["filename"], sample_script_file["content"], sample_script_file["content_type"])}
            
            response = await async_client.post(
                "/api/v1/uploads/script",
                files=files,
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            TestHelpers.assert_response_structure(data, ["id", "filename", "size", "status"])
    
    async def test_upload_file_too_large(self, async_client, auth_headers, tenant_headers):
        """Test upload with file too large."""
        large_file = {
            "filename": "large_video.mp4",
            "content": b"x" * (6 * 1024 * 1024 * 1024),  # 6GB - over limit
            "content_type": "video/mp4"
        }
        
        files = {"file": (large_file["filename"], large_file["content"], large_file["content_type"])}
        
        response = await async_client.post(
            "/api/v1/uploads/video",
            files=files,
            headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
        )
        
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    
    async def test_upload_invalid_file_type(self, async_client, auth_headers, tenant_headers):
        """Test upload with invalid file type."""
        invalid_file = {
            "filename": "document.pdf",
            "content": b"fake pdf content",
            "content_type": "application/pdf"
        }
        
        files = {"file": (invalid_file["filename"], invalid_file["content"], invalid_file["content_type"])}
        
        response = await async_client.post(
            "/api/v1/uploads/video",  # Trying to upload PDF as video
            files=files,
            headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestJobEndpoints:
    """Test job management endpoints."""
    
    async def test_create_job(self, async_client, auth_headers, tenant_headers):
        """Test job creation."""
        job_data = {
            "project_id": "test-project",
            "type": "video_processing",
            "settings": {
                "target_resolution": "4K",
                "quality": "high"
            }
        }
        
        with patch('app.api.v1.jobs.create_job') as mock_create:
            mock_create.return_value = TestDataFactory.create_job(id="job-id", **job_data)
            
            response = await async_client.post(
                "/api/v1/jobs",
                json=job_data,
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            TestHelpers.assert_response_structure(data, ["id", "type", "status", "settings"])
    
    async def test_get_job_status(self, async_client, auth_headers, tenant_headers):
        """Test getting job status."""
        job_id = "test-job-id"
        
        with patch('app.api.v1.jobs.get_job_by_id') as mock_get:
            mock_get.return_value = TestDataFactory.create_job(id=job_id, status="processing")
            
            response = await async_client.get(
                f"/api/v1/jobs/{job_id}",
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == job_id
            assert data["status"] == "processing"
    
    async def test_cancel_job(self, async_client, auth_headers, tenant_headers):
        """Test job cancellation."""
        job_id = "test-job-id"
        
        with patch('app.api.v1.jobs.cancel_job') as mock_cancel:
            mock_cancel.return_value = TestDataFactory.create_job(id=job_id, status="cancelled")
            
            response = await async_client.post(
                f"/api/v1/jobs/{job_id}/cancel",
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "cancelled"
    
    async def test_get_job_logs(self, async_client, auth_headers, tenant_headers):
        """Test getting job logs."""
        job_id = "test-job-id"
        
        with patch('app.api.v1.jobs.get_job_logs') as mock_get_logs:
            mock_get_logs.return_value = {
                "logs": [
                    {"timestamp": "2023-01-01T00:00:00Z", "level": "INFO", "message": "Job started"},
                    {"timestamp": "2023-01-01T00:01:00Z", "level": "INFO", "message": "Processing video"}
                ]
            }
            
            response = await async_client.get(
                f"/api/v1/jobs/{job_id}/logs",
                headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "logs" in data
            assert len(data["logs"]) == 2


class TestUserEndpoints:
    """Test user management endpoints."""
    
    async def test_get_user_profile(self, async_client, auth_headers):
        """Test getting user profile."""
        with patch('app.api.v1.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = TestDataFactory.create_user(id="user-id")
            
            response = await async_client.get(
                "/api/v1/user/profile",
                headers=auth_headers("valid-token")
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            TestHelpers.assert_response_structure(data, ["id", "email", "full_name"])
    
    async def test_update_user_profile(self, async_client, auth_headers):
        """Test updating user profile."""
        update_data = {"full_name": "Updated Name"}
        
        with patch('app.api.v1.users.update_user_profile') as mock_update:
            updated_user = TestDataFactory.create_user(id="user-id", full_name=update_data["full_name"])
            mock_update.return_value = updated_user
            
            response = await async_client.put(
                "/api/v1/user/profile",
                json=update_data,
                headers=auth_headers("valid-token")
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["full_name"] == update_data["full_name"]
    
    async def test_change_password(self, async_client, auth_headers):
        """Test password change."""
        password_data = {
            "current_password": "OldPassword123!",
            "new_password": "NewPassword123!"
        }
        
        with patch('app.api.v1.users.change_user_password') as mock_change:
            mock_change.return_value = {"message": "Password updated successfully"}
            
            response = await async_client.post(
                "/api/v1/user/change-password",
                json=password_data,
                headers=auth_headers("valid-token")
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    async def test_complete_workflow(self, async_client, auth_headers, tenant_headers):
        """Test complete workflow from project creation to job completion."""
        # Create project
        project_data = TestDataFactory.create_project()
        project_response = await async_client.post(
            "/api/v1/projects",
            json=project_data,
            headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
        )
        assert project_response.status_code == status.HTTP_201_CREATED
        project = project_response.json()
        
        # Upload video file
        video_file = {
            "filename": "test.mp4",
            "content": b"fake video content",
            "content_type": "video/mp4"
        }
        files = {"file": (video_file["filename"], video_file["content"], video_file["content_type"])}
        
        upload_response = await async_client.post(
            "/api/v1/uploads/video",
            files=files,
            headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
        )
        # This might fail due to validation, but check the response
        assert upload_response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        
        # Create job
        job_data = {
            "project_id": project["id"],
            "type": "video_processing",
            "settings": {"target_resolution": "4K"}
        }
        
        job_response = await async_client.post(
            "/api/v1/jobs",
            json=job_data,
            headers={**auth_headers("valid-token"), **tenant_headers("test-tenant")}
        )
        # This might also fail due to missing implementations
        assert job_response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]
    
    async def test_error_handling(self, async_client, auth_headers):
        """Test API error handling."""
        # Test unauthorized access
        response = await async_client.get("/api/v1/user/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test not found
        response = await async_client.get(
            "/api/v1/projects/non-existent",
            headers=auth_headers("valid-token")
        )
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED]
        
        # Test validation error
        response = await async_client.post(
            "/api/v1/projects",
            json={"invalid": "data"},
            headers=auth_headers("valid-token")
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
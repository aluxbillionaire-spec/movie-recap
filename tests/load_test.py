"""
Performance tests using Locust.
"""
from locust import HttpUser, task, between
import json
import random


class MovieRecapUser(HttpUser):
    """Simulate user behavior for load testing."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Set up user session."""
        self.tenant_id = f"tenant-{random.randint(1000, 9999)}"
        self.auth_token = self.login()
    
    def login(self):
        """Authenticate user."""
        login_data = {
            "email": f"user{random.randint(1, 1000)}@example.com",
            "password": "TestPassword123!"
        }
        
        response = self.client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers={"X-Tenant-ID": self.tenant_id}
        )
        
        if response.status_code == 200:
            return response.json().get("access_token", "test-token")
        return "test-token"
    
    def get_headers(self):
        """Get authentication headers."""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json"
        }
    
    @task(3)
    def view_projects(self):
        """Test viewing projects list."""
        self.client.get(
            "/api/v1/projects",
            headers=self.get_headers()
        )
    
    @task(2)
    def create_project(self):
        """Test creating a new project."""
        project_data = {
            "name": f"Test Project {random.randint(1, 1000)}",
            "description": "Load testing project",
            "settings": {
                "target_resolution": random.choice(["1080p", "1440p", "4K"]),
                "quality": random.choice(["low", "medium", "high"])
            }
        }
        
        self.client.post(
            "/api/v1/projects",
            json=project_data,
            headers=self.get_headers()
        )
    
    @task(1)
    def upload_file(self):
        """Test file upload."""
        # Simulate small file upload
        files = {"file": ("test.mp4", b"fake video content" * 100, "video/mp4")}
        
        self.client.post(
            "/api/v1/uploads/video",
            files=files,
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "X-Tenant-ID": self.tenant_id
            }
        )
    
    @task(2)
    def check_job_status(self):
        """Test checking job status."""
        job_id = f"job-{random.randint(1, 100)}"
        
        self.client.get(
            f"/api/v1/jobs/{job_id}",
            headers=self.get_headers()
        )
    
    @task(1)
    def get_user_profile(self):
        """Test getting user profile."""
        self.client.get(
            "/api/v1/user/profile",
            headers=self.get_headers()
        )


class AdminUser(HttpUser):
    """Simulate admin user behavior."""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Set up admin session."""
        self.tenant_id = "admin-tenant"
        self.auth_token = "admin-token"
    
    def get_headers(self):
        """Get admin headers."""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json"
        }
    
    @task(1)
    def view_system_metrics(self):
        """Test viewing system metrics."""
        self.client.get(
            "/api/v1/admin/metrics",
            headers=self.get_headers()
        )
    
    @task(1)
    def view_all_jobs(self):
        """Test viewing all jobs."""
        self.client.get(
            "/api/v1/admin/jobs",
            headers=self.get_headers()
        )
    
    @task(1)
    def health_check(self):
        """Test health check endpoint."""
        self.client.get("/health")


class HighVolumeUploadUser(HttpUser):
    """Simulate high-volume upload scenarios."""
    
    wait_time = between(5, 10)
    weight = 1  # Lower weight for heavy operations
    
    def on_start(self):
        """Set up upload user session."""
        self.tenant_id = f"upload-tenant-{random.randint(1, 10)}"
        self.auth_token = "upload-token"
    
    @task
    def large_file_upload(self):
        """Test large file upload."""
        # Simulate larger file
        large_content = b"fake video content" * 10000  # ~150KB
        files = {"file": ("large_test.mp4", large_content, "video/mp4")}
        
        self.client.post(
            "/api/v1/uploads/video",
            files=files,
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "X-Tenant-ID": self.tenant_id
            }
        )


class ProcessingUser(HttpUser):
    """Simulate video processing workflows."""
    
    wait_time = between(3, 8)
    
    def on_start(self):
        """Set up processing user session."""
        self.tenant_id = f"processing-tenant-{random.randint(1, 5)}"
        self.auth_token = "processing-token"
        self.project_id = None
    
    def get_headers(self):
        """Get processing headers."""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json"
        }
    
    @task(3)
    def create_processing_job(self):
        """Test creating processing jobs."""
        if not self.project_id:
            self.create_test_project()
        
        job_data = {
            "project_id": self.project_id,
            "type": random.choice(["video_processing", "script_alignment", "content_moderation"]),
            "settings": {
                "target_resolution": random.choice(["1080p", "4K"]),
                "quality": random.choice(["medium", "high"]),
                "priority": random.choice(["normal", "high"])
            }
        }
        
        self.client.post(
            "/api/v1/jobs",
            json=job_data,
            headers=self.get_headers()
        )
    
    def create_test_project(self):
        """Create a test project for processing."""
        project_data = {
            "name": f"Processing Project {random.randint(1, 1000)}",
            "description": "Processing load test project"
        }
        
        response = self.client.post(
            "/api/v1/projects",
            json=project_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 201:
            self.project_id = response.json().get("id", "test-project")
        else:
            self.project_id = "test-project"
    
    @task(2)
    def monitor_jobs(self):
        """Test monitoring job progress."""
        # Simulate checking multiple jobs
        for _ in range(random.randint(1, 3)):
            job_id = f"job-{random.randint(1, 100)}"
            self.client.get(
                f"/api/v1/jobs/{job_id}",
                headers=self.get_headers()
            )
    
    @task(1)
    def cancel_job(self):
        """Test job cancellation."""
        job_id = f"job-{random.randint(1, 100)}"
        self.client.post(
            f"/api/v1/jobs/{job_id}/cancel",
            headers=self.get_headers()
        )
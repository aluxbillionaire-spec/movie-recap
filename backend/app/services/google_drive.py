"""
Google Drive Integration Service

Handle file uploads, downloads, and management with Google Drive API.
"""

import os
import json
import tempfile
import hashlib
from typing import Dict, Any, Optional, List
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import io

from app.core.config import settings


class GoogleDriveService:
    """Google Drive API service for file operations."""
    
    def __init__(self, credentials_file: str = None):
        self.credentials_file = credentials_file or settings.GOOGLE_DRIVE_CREDENTIALS_FILE
        self.service = None
        self.root_folder_id = None
        
        # Folder structure
        self.folders = {
            "inputs": None,
            "intermediate": None,
            "upscale_inputs": None,
            "upscale_outputs": None,
            "outputs": None,
            "completed_jobs": None,
            "failed_jobs": None
        }
    
    async def initialize(self):
        """Initialize Google Drive service and folder structure."""
        
        if self.service is None:
            await self._authenticate()
            await self._setup_folder_structure()
    
    async def _authenticate(self):
        """Authenticate with Google Drive API."""
        
        try:
            # Load service account credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            # Build service
            self.service = build('drive', 'v3', credentials=credentials)
            
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Drive: {str(e)}")
    
    async def _setup_folder_structure(self):
        """Create and get folder structure in Google Drive."""
        
        # Create or get root folder
        self.root_folder_id = await self._get_or_create_folder(
            settings.GOOGLE_DRIVE_ROOT_FOLDER, 
            parent_id="root"
        )
        
        # Create subfolders
        for folder_name in self.folders.keys():
            self.folders[folder_name] = await self._get_or_create_folder(
                folder_name,
                parent_id=self.root_folder_id
            )
    
    async def _get_or_create_folder(self, folder_name: str, parent_id: str) -> str:
        """Get existing folder or create new one."""
        
        try:
            # Search for existing folder
            query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                return folders[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'parents': [parent_id],
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except HttpError as e:
            raise Exception(f"Failed to create/get folder {folder_name}: {str(e)}")
    
    async def create_resumable_upload(
        self, 
        filename: str, 
        file_size: int, 
        content_type: str,
        folder_path: str
    ) -> Dict[str, Any]:
        """Create resumable upload session."""
        
        await self.initialize()
        
        try:
            # Get or create folder for the upload
            folder_id = await self._get_upload_folder(folder_path)
            
            # Create file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Create resumable upload session
            # Note: This is a simplified version - real implementation would
            # use Google's resumable upload protocol
            
            upload_id = hashlib.md5(f"{filename}_{file_size}_{folder_path}".encode()).hexdigest()
            
            # Store upload session info (in production, use Redis)
            upload_info = {
                'upload_id': upload_id,
                'filename': filename,
                'file_size': file_size,
                'content_type': content_type,
                'folder_id': folder_id,
                'folder_path': folder_path,
                'status': 'initialized'
            }
            
            # In production, store this in Redis or database
            # For now, we'll simulate the upload URL
            upload_url = f"https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&upload_id={upload_id}"
            
            return {
                'upload_id': upload_id,
                'folder_id': folder_id,
                'upload_url': upload_url,
                'upload_info': upload_info
            }
            
        except Exception as e:
            raise Exception(f"Failed to create resumable upload: {str(e)}")
    
    async def _get_upload_folder(self, folder_path: str) -> str:
        """Get or create folder for upload based on path."""
        
        path_parts = folder_path.strip('/').split('/')
        current_folder_id = self.root_folder_id
        
        # Navigate/create folder structure
        for part in path_parts:
            if part:  # Skip empty parts
                current_folder_id = await self._get_or_create_folder(part, current_folder_id)
        
        return current_folder_id
    
    async def upload_file(
        self, 
        file_path: str, 
        filename: str, 
        folder_path: str
    ) -> Dict[str, Any]:
        """Upload file directly to Google Drive."""
        
        await self.initialize()
        
        try:
            # Get folder
            folder_id = await self._get_upload_folder(folder_path)
            
            # File metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Detect content type
            content_type = self._get_content_type(filename)
            
            # Upload file
            with open(file_path, 'rb') as file_data:
                media = MediaIoBaseUpload(
                    io.BytesIO(file_data.read()),
                    mimetype=content_type,
                    resumable=True
                )
                
                file_obj = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,name,size,md5Checksum'
                ).execute()
            
            # Calculate local file checksum
            local_checksum = self._calculate_checksum(file_path)
            
            return {
                'file_id': file_obj.get('id'),
                'file_path': f"{folder_path}/{filename}",
                'file_size': int(file_obj.get('size', 0)),
                'checksum': file_obj.get('md5Checksum'),
                'local_checksum': local_checksum,
                'verified': file_obj.get('md5Checksum') == local_checksum
            }
            
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def download_file(self, file_id: str, local_path: str) -> Dict[str, Any]:
        """Download file from Google Drive."""
        
        await self.initialize()
        
        try:
            # Get file metadata
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields='name,size,md5Checksum'
            ).execute()
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            
            with open(local_path, 'wb') as local_file:
                downloader = MediaIoBaseDownload(local_file, request)
                done = False
                
                while done is False:
                    status, done = downloader.next_chunk()
            
            # Verify download
            local_checksum = self._calculate_checksum(local_path)
            drive_checksum = file_metadata.get('md5Checksum')
            
            return {
                'filename': file_metadata.get('name'),
                'local_path': local_path,
                'file_size': int(file_metadata.get('size', 0)),
                'checksum_verified': local_checksum == drive_checksum,
                'drive_checksum': drive_checksum,
                'local_checksum': local_checksum
            }
            
        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")
    
    async def list_files(self, folder_path: str, file_pattern: str = None) -> List[Dict[str, Any]]:
        """List files in a folder."""
        
        await self.initialize()
        
        try:
            folder_id = await self._get_upload_folder(folder_path)
            
            # Build query
            query = f"'{folder_id}' in parents and trashed=false"
            if file_pattern:
                query += f" and name contains '{file_pattern}'"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id,name,size,createdTime,modifiedTime,md5Checksum)'
            ).execute()
            
            files = results.get('files', [])
            
            return [
                {
                    'id': file['id'],
                    'name': file['name'],
                    'size': int(file.get('size', 0)),
                    'created_time': file.get('createdTime'),
                    'modified_time': file.get('modifiedTime'),
                    'checksum': file.get('md5Checksum')
                }
                for file in files
            ]
            
        except Exception as e:
            raise Exception(f"Failed to list files: {str(e)}")
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive."""
        
        await self.initialize()
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
            
        except Exception as e:
            print(f"Failed to delete file {file_id}: {str(e)}")
            return False
    
    async def move_file(self, file_id: str, new_folder_path: str) -> Dict[str, Any]:
        """Move file to different folder."""
        
        await self.initialize()
        
        try:
            # Get current parents
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(file_metadata.get('parents'))
            
            # Get new folder
            new_folder_id = await self._get_upload_folder(new_folder_path)
            
            # Move file
            file_obj = self.service.files().update(
                fileId=file_id,
                addParents=new_folder_id,
                removeParents=previous_parents,
                fields='id,parents'
            ).execute()
            
            return {
                'file_id': file_obj.get('id'),
                'new_parents': file_obj.get('parents'),
                'moved': True
            }
            
        except Exception as e:
            raise Exception(f"Failed to move file: {str(e)}")
    
    async def complete_upload(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """Complete resumable upload and return file info."""
        
        # In production, retrieve upload info from Redis/database
        # For now, simulate completion
        
        # This would contain the actual file information after upload
        return {
            'upload_id': upload_id,
            'status': 'completed',
            'file_id': f'drive_file_{upload_id}',
            'file_path': f'uploads/{upload_id}',
            'file_size': 1024000,  # Example size
            'checksum': 'example_checksum'
        }
    
    async def get_upload_status(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """Get upload session status."""
        
        # In production, retrieve from Redis/database
        return {
            'upload_id': upload_id,
            'status': 'in_progress',
            'bytes_uploaded': 512000,
            'total_bytes': 1024000,
            'progress_percent': 50.0
        }
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename."""
        
        ext = os.path.splitext(filename)[1].lower()
        
        content_types = {
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mkv': 'video/x-matroska',
            '.mov': 'video/quicktime',
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.json': 'application/json'
        }
        
        return content_types.get(ext, 'application/octet-stream')
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of file."""
        
        hash_md5 = hashlib.md5()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    async def create_shared_link(self, file_id: str, expires_hours: int = 24) -> str:
        """Create shareable link for file download."""
        
        await self.initialize()
        
        try:
            # Make file publicly accessible with link
            permission = {
                'role': 'reader',
                'type': 'anyone'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            # Get shareable link
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields='webViewLink,webContentLink'
            ).execute()
            
            # Return direct download link
            return file_metadata.get('webContentLink', file_metadata.get('webViewLink'))
            
        except Exception as e:
            raise Exception(f"Failed to create shared link: {str(e)}")
    
    async def cleanup_old_files(self, folder_path: str, days_old: int = 30) -> int:
        """Clean up files older than specified days."""
        
        await self.initialize()
        
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            folder_id = await self._get_upload_folder(folder_path)
            
            # Find old files
            query = f"'{folder_id}' in parents and createdTime < '{cutoff_date}' and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id,name)'
            ).execute()
            
            files = results.get('files', [])
            deleted_count = 0
            
            # Delete old files
            for file in files:
                if await self.delete_file(file['id']):
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"Failed to cleanup old files: {str(e)}")
            return 0
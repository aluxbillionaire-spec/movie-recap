"""
Test Celery workers.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os

from app.workers.video_processing import process_video
from app.workers.script_extraction import extract_script_content
from app.workers.alignment import align_script_to_video
from app.workers.assembly import assemble_video
from app.workers.moderation import moderate_content
from tests.conftest import TestDataFactory


class TestVideoProcessingWorker:
    """Test video processing worker."""
    
    @pytest.fixture
    def sample_video_path(self):
        """Create a temporary video file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            f.write(b"fake video content")
            yield f.name
        os.unlink(f.name)
    
    @pytest.fixture
    def job_data(self):
        """Sample job data."""
        return {
            "id": "test-job-id",
            "tenant_id": "test-tenant",
            "input_file": "path/to/video.mp4",
            "settings": {
                "target_resolution": "4K",
                "quality": "high",
                "frame_rate": 30
            }
        }
    
    @patch('app.workers.video_processing.ffmpeg')
    @patch('app.workers.video_processing.update_job_status')
    async def test_process_video_success(self, mock_update_status, mock_ffmpeg, job_data, sample_video_path):
        """Test successful video processing."""
        job_data["input_file"] = sample_video_path
        
        # Mock FFmpeg operations
        mock_ffmpeg.input.return_value.output.return_value.run = Mock()
        
        # Mock file operations
        with patch('app.workers.video_processing.os.path.exists', return_value=True), \
             patch('app.workers.video_processing.get_video_info') as mock_info:
            
            mock_info.return_value = {
                "duration": 120.0,
                "width": 1920,
                "height": 1080,
                "fps": 24
            }
            
            result = await process_video(job_data)
            
            assert result["status"] == "completed"
            assert "output_file" in result
            mock_update_status.assert_called()
    
    @patch('app.workers.video_processing.update_job_status')
    async def test_process_video_file_not_found(self, mock_update_status, job_data):
        """Test processing with missing input file."""
        job_data["input_file"] = "non-existent-file.mp4"
        
        with patch('app.workers.video_processing.os.path.exists', return_value=False):
            result = await process_video(job_data)
            
            assert result["status"] == "failed"
            assert "error" in result
    
    @patch('app.workers.video_processing.ffmpeg')
    @patch('app.workers.video_processing.update_job_status')
    async def test_process_video_ffmpeg_error(self, mock_update_status, mock_ffmpeg, job_data, sample_video_path):
        """Test processing with FFmpeg error."""
        job_data["input_file"] = sample_video_path
        
        # Mock FFmpeg to raise an exception
        mock_ffmpeg.input.return_value.output.return_value.run.side_effect = Exception("FFmpeg error")
        
        with patch('app.workers.video_processing.os.path.exists', return_value=True):
            result = await process_video(job_data)
            
            assert result["status"] == "failed"
            assert "FFmpeg error" in result["error"]


class TestScriptExtractionWorker:
    """Test script extraction worker."""
    
    @pytest.fixture
    def sample_script_path(self):
        """Create a temporary script file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a sample movie script.\nScene 1: Introduction\nCharacter speaks.")
            yield f.name
        os.unlink(f.name)
    
    @pytest.fixture
    def job_data(self):
        """Sample job data."""
        return {
            "id": "test-job-id",
            "tenant_id": "test-tenant",
            "input_file": "path/to/script.txt",
            "file_type": "text/plain"
        }
    
    async def test_extract_script_text_file(self, job_data, sample_script_path):
        """Test extracting text from plain text file."""
        job_data["input_file"] = sample_script_path
        
        with patch('app.workers.script_extraction.update_job_status') as mock_update:
            result = await extract_script_content(job_data)
            
            assert result["status"] == "completed"
            assert "content" in result
            assert "sample movie script" in result["content"]
            mock_update.assert_called()
    
    @patch('app.workers.script_extraction.PyPDF2')
    async def test_extract_script_pdf_file(self, mock_pdf, job_data, sample_script_path):
        """Test extracting text from PDF file."""
        job_data["file_type"] = "application/pdf"
        job_data["input_file"] = sample_script_path
        
        # Mock PDF reader
        mock_reader = Mock()
        mock_reader.pages = [Mock()]
        mock_reader.pages[0].extract_text.return_value = "PDF script content"
        mock_pdf.PdfReader.return_value = mock_reader
        
        with patch('app.workers.script_extraction.update_job_status'), \
             patch('builtins.open', mock_open(read_data=b"fake pdf data")):
            
            result = await extract_script_content(job_data)
            
            assert result["status"] == "completed"
            assert result["content"] == "PDF script content"
    
    async def test_extract_script_unsupported_format(self, job_data):
        """Test extraction with unsupported file format."""
        job_data["file_type"] = "application/unknown"
        
        with patch('app.workers.script_extraction.update_job_status'):
            result = await extract_script_content(job_data)
            
            assert result["status"] == "failed"
            assert "Unsupported file format" in result["error"]


class TestAlignmentWorker:
    """Test script-to-video alignment worker."""
    
    @pytest.fixture
    def job_data(self):
        """Sample job data."""
        return {
            "id": "test-job-id",
            "tenant_id": "test-tenant",
            "video_file": "path/to/video.mp4",
            "script_content": "Scene 1: Character introduction. Scene 2: Action sequence.",
            "settings": {
                "confidence_threshold": 0.7,
                "segment_duration": 10.0
            }
        }
    
    @patch('app.workers.alignment.SentenceTransformer')
    @patch('app.workers.alignment.update_job_status')
    async def test_align_script_success(self, mock_update, mock_transformer, job_data):
        """Test successful script alignment."""
        # Mock sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_transformer.return_value = mock_model
        
        # Mock video analysis
        with patch('app.workers.alignment.analyze_video_content') as mock_analyze:
            mock_analyze.return_value = [
                {"start_time": 0.0, "end_time": 10.0, "content": "intro scene"},
                {"start_time": 10.0, "end_time": 20.0, "content": "action scene"}
            ]
            
            # Mock similarity calculation
            with patch('app.workers.alignment.cosine_similarity') as mock_similarity:
                mock_similarity.return_value = [[0.8, 0.3], [0.2, 0.9]]
                
                result = await align_script_to_video(job_data)
                
                assert result["status"] == "completed"
                assert "alignments" in result
                assert len(result["alignments"]) == 2
    
    @patch('app.workers.alignment.update_job_status')
    async def test_align_script_low_confidence(self, mock_update, job_data):
        """Test alignment with low confidence scores."""
        job_data["settings"]["confidence_threshold"] = 0.9  # Very high threshold
        
        with patch('app.workers.alignment.SentenceTransformer') as mock_transformer, \
             patch('app.workers.alignment.analyze_video_content') as mock_analyze, \
             patch('app.workers.alignment.cosine_similarity') as mock_similarity:
            
            # Mock low similarity scores
            mock_similarity.return_value = [[0.1, 0.2], [0.3, 0.1]]
            mock_analyze.return_value = [{"start_time": 0, "end_time": 10, "content": "scene"}]
            
            result = await align_script_to_video(job_data)
            
            assert result["status"] == "completed"
            assert result.get("requires_manual_review", False)


class TestAssemblyWorker:
    """Test video assembly worker."""
    
    @pytest.fixture
    def job_data(self):
        """Sample job data."""
        return {
            "id": "test-job-id",
            "tenant_id": "test-tenant",
            "alignments": [
                {"script_segment": "Intro", "video_start": 0.0, "video_end": 10.0},
                {"script_segment": "Action", "video_start": 10.0, "video_end": 20.0}
            ],
            "video_file": "path/to/video.mp4",
            "settings": {
                "target_resolution": "4K",
                "quality": "high",
                "add_intro": True,
                "add_outro": True
            }
        }
    
    @patch('app.workers.assembly.ffmpeg')
    @patch('app.workers.assembly.update_job_status')
    async def test_assemble_video_success(self, mock_update, mock_ffmpeg, job_data):
        """Test successful video assembly."""
        # Mock FFmpeg operations
        mock_input = Mock()
        mock_ffmpeg.input.return_value = mock_input
        mock_input.video.filter.return_value = mock_input
        mock_input.audio.filter.return_value = mock_input
        mock_input.output.return_value.run = Mock()
        
        with patch('app.workers.assembly.os.path.exists', return_value=True):
            result = await assemble_video(job_data)
            
            assert result["status"] == "completed"
            assert "output_file" in result
            mock_update.assert_called()
    
    @patch('app.workers.assembly.update_job_status')
    async def test_assemble_video_no_alignments(self, mock_update, job_data):
        """Test assembly with no alignments."""
        job_data["alignments"] = []
        
        result = await assemble_video(job_data)
        
        assert result["status"] == "failed"
        assert "No alignments provided" in result["error"]
    
    @patch('app.workers.assembly.ffmpeg')
    @patch('app.workers.assembly.update_job_status')
    async def test_assemble_video_ffmpeg_error(self, mock_update, mock_ffmpeg, job_data):
        """Test assembly with FFmpeg error."""
        # Mock FFmpeg to raise an exception
        mock_ffmpeg.input.side_effect = Exception("FFmpeg assembly error")
        
        result = await assemble_video(job_data)
        
        assert result["status"] == "failed"
        assert "FFmpeg assembly error" in result["error"]


class TestModerationWorker:
    """Test content moderation worker."""
    
    @pytest.fixture
    def job_data(self):
        """Sample job data."""
        return {
            "id": "test-job-id",
            "tenant_id": "test-tenant",
            "content_file": "path/to/video.mp4",
            "content_type": "video",
            "settings": {
                "check_copyright": True,
                "check_watermarks": True,
                "sensitivity": "high"
            }
        }
    
    @patch('app.workers.moderation.cv2')
    @patch('app.workers.moderation.update_job_status')
    async def test_moderate_content_clean(self, mock_update, mock_cv2, job_data):
        """Test moderation of clean content."""
        # Mock OpenCV operations
        mock_cv2.VideoCapture.return_value.read.return_value = (True, Mock())
        mock_cv2.VideoCapture.return_value.isOpened.return_value = True
        
        with patch('app.workers.moderation.detect_watermarks') as mock_detect_watermarks, \
             patch('app.workers.moderation.check_copyright_indicators') as mock_check_copyright:
            
            mock_detect_watermarks.return_value = []
            mock_check_copyright.return_value = {"risk_level": "low", "indicators": []}
            
            result = await moderate_content(job_data)
            
            assert result["status"] == "completed"
            assert result["moderation_result"]["approved"]
            assert result["moderation_result"]["risk_level"] == "low"
    
    @patch('app.workers.moderation.cv2')
    @patch('app.workers.moderation.update_job_status')
    async def test_moderate_content_with_watermarks(self, mock_update, mock_cv2, job_data):
        """Test moderation of content with watermarks."""
        # Mock detection of watermarks
        with patch('app.workers.moderation.detect_watermarks') as mock_detect_watermarks, \
             patch('app.workers.moderation.check_copyright_indicators') as mock_check_copyright:
            
            mock_detect_watermarks.return_value = [
                {"type": "logo", "confidence": 0.9, "location": [100, 100, 200, 150]}
            ]
            mock_check_copyright.return_value = {"risk_level": "high", "indicators": ["watermark"]}
            
            result = await moderate_content(job_data)
            
            assert result["status"] == "completed"
            assert not result["moderation_result"]["approved"]
            assert result["moderation_result"]["risk_level"] == "high"
            assert len(result["moderation_result"]["issues"]) > 0
    
    @patch('app.workers.moderation.update_job_status')
    async def test_moderate_content_file_error(self, mock_update, job_data):
        """Test moderation with file access error."""
        job_data["content_file"] = "non-existent-file.mp4"
        
        with patch('app.workers.moderation.cv2') as mock_cv2:
            mock_cv2.VideoCapture.return_value.isOpened.return_value = False
            
            result = await moderate_content(job_data)
            
            assert result["status"] == "failed"
            assert "Failed to open" in result["error"]


@pytest.mark.integration
class TestWorkerIntegration:
    """Integration tests for worker pipeline."""
    
    @pytest.mark.slow
    async def test_complete_processing_pipeline(self):
        """Test complete processing pipeline with multiple workers."""
        # This would test the full pipeline:
        # 1. Video processing
        # 2. Script extraction
        # 3. Alignment
        # 4. Assembly
        # 5. Moderation
        
        # Mock the entire pipeline
        with patch('app.workers.video_processing.process_video') as mock_video, \
             patch('app.workers.script_extraction.extract_script_content') as mock_script, \
             patch('app.workers.alignment.align_script_to_video') as mock_align, \
             patch('app.workers.assembly.assemble_video') as mock_assembly, \
             patch('app.workers.moderation.moderate_content') as mock_moderate:
            
            # Mock successful results for each step
            mock_video.return_value = {"status": "completed", "output_file": "processed.mp4"}
            mock_script.return_value = {"status": "completed", "content": "Script content"}
            mock_align.return_value = {"status": "completed", "alignments": []}
            mock_assembly.return_value = {"status": "completed", "output_file": "final.mp4"}
            mock_moderate.return_value = {"status": "completed", "moderation_result": {"approved": True}}
            
            # Test pipeline execution
            pipeline_result = await run_processing_pipeline({
                "job_id": "test-job",
                "video_file": "input.mp4",
                "script_file": "script.txt"
            })
            
            assert pipeline_result["status"] == "completed"
            assert all(worker.called for worker in [mock_video, mock_script, mock_align, mock_assembly, mock_moderate])


async def run_processing_pipeline(job_data):
    """Mock pipeline runner for testing."""
    # This would be implemented in the actual worker orchestration
    return {"status": "completed", "final_output": "result.mp4"}
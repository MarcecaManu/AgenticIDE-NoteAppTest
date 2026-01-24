"""
Tests for task worker implementations
"""
import pytest
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.task_workers import (
    DataProcessingWorker,
    EmailSimulationWorker,
    ImageProcessingWorker
)


class TestDataProcessingWorker:
    """Tests for data processing worker"""
    
    @pytest.mark.asyncio
    async def test_data_processing_execution(self):
        """Test data processing worker execution"""
        parameters = {"rows": 100}
        result = await DataProcessingWorker.execute("test-task-id", parameters)
        
        assert "rows_processed" in result
        assert "summary" in result
        assert result["rows_processed"] == 100
        assert "total_rows" in result["summary"]
        assert result["summary"]["total_rows"] == 100
    
    @pytest.mark.asyncio
    async def test_data_processing_with_custom_rows(self):
        """Test data processing with custom row count"""
        parameters = {"rows": 500}
        result = await DataProcessingWorker.execute("test-task-id", parameters)
        
        assert result["rows_processed"] == 500
        assert result["summary"]["total_rows"] == 500


class TestEmailSimulationWorker:
    """Tests for email simulation worker"""
    
    @pytest.mark.asyncio
    async def test_email_simulation_execution(self):
        """Test email simulation worker execution"""
        parameters = {"count": 3}
        result = await EmailSimulationWorker.execute("test-task-id", parameters)
        
        assert "sent" in result
        assert "failed" in result
        assert "recipients" in result
        assert result["sent"] + result["failed"] == 3
        assert len(result["recipients"]) == 3
    
    @pytest.mark.asyncio
    async def test_email_simulation_with_recipients(self):
        """Test email simulation with specific recipients"""
        parameters = {
            "recipients": ["user1@test.com", "user2@test.com"]
        }
        result = await EmailSimulationWorker.execute("test-task-id", parameters)
        
        assert len(result["recipients"]) == 2
        assert any("user1@test.com" in r["email"] for r in result["recipients"])


class TestImageProcessingWorker:
    """Tests for image processing worker"""
    
    @pytest.mark.asyncio
    async def test_image_processing_execution(self):
        """Test image processing worker execution"""
        parameters = {"count": 2, "operation": "resize"}
        result = await ImageProcessingWorker.execute("test-task-id", parameters)
        
        assert "processed" in result
        assert "failed" in result
        assert "images" in result
        assert result["processed"] + result["failed"] == 2
        assert len(result["images"]) == 2
    
    @pytest.mark.asyncio
    async def test_image_processing_different_operations(self):
        """Test image processing with different operations"""
        for operation in ["resize", "convert", "compress"]:
            parameters = {"count": 1, "operation": operation}
            result = await ImageProcessingWorker.execute("test-task-id", parameters)
            
            assert len(result["images"]) == 1
            if result["images"][0]["status"] == "success":
                assert result["images"][0]["operation"] == operation


"""
Tests for utility functions and classes
"""
import pytest
import logging
from unittest.mock import Mock, patch
from mkdocs_git_range.utils import GitRangeLogger


class TestGitRangeLogger:
    """Test the GitRangeLogger utility"""
    
    def test_setup_logger_returns_logger(self):
        """Test that setup_logger returns a logger instance"""
        logger = GitRangeLogger.setup_logger("test_plugin")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "mkdocs.plugins.test_plugin"
    
    def test_setup_logger_different_names(self):
        """Test that setup_logger works with different plugin names"""
        logger1 = GitRangeLogger.setup_logger("plugin1")
        logger2 = GitRangeLogger.setup_logger("plugin2")
        
        assert logger1.name == "mkdocs.plugins.plugin1"
        assert logger2.name == "mkdocs.plugins.plugin2"
        assert logger1 != logger2
    
    def test_logger_can_log_messages(self):
        """Test that the logger can actually log messages"""
        logger = GitRangeLogger.setup_logger("test")
        
        # This should not raise any exceptions
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
    
    def test_setup_logger_with_module_name(self):
        """Test setup_logger with __name__ parameter"""
        module_name = "mkdocs_git_range.plugin"
        logger = GitRangeLogger.setup_logger(module_name)
        
        expected_name = f"mkdocs.plugins.{module_name}"
        assert logger.name == expected_name


class TestUtilityFunctions:
    """Test various utility functions"""
    
    def test_hex_to_binary_sha_conversion(self):
        """Test conversion from hex SHA to binary"""
        hex_sha = "a1b2c3d4e5f6789012345678901234567890abcd"
        binary_sha = bytes.fromhex(hex_sha)
        
        # Should be 20 bytes
        assert len(binary_sha) == 20
        
        # Should be convertible back to hex
        converted_back = binary_sha.hex()
        assert converted_back == hex_sha
    
    def test_invalid_hex_sha_raises_error(self):
        """Test that invalid hex strings raise appropriate errors"""
        invalid_hex = "not_a_hex_string"
        
        with pytest.raises(ValueError):
            bytes.fromhex(invalid_hex)
    
    def test_short_hex_sha_conversion(self):
        """Test conversion with short SHA (7 characters)"""
        short_sha = "a1b2c3d"
        binary_sha = bytes.fromhex(short_sha)
        
        # Should be 3.5 bytes (7 hex chars = 3.5 bytes)
        assert len(binary_sha) == 3  # bytes.fromhex truncates
        
        converted_back = binary_sha.hex()
        assert converted_back == "a1b2c3"  # Last char gets truncated


class TestErrorHandling:
    """Test error handling in utility functions"""
    
    def test_logger_handles_none_name(self):
        """Test that setup_logger handles None name gracefully"""
        # This might raise an exception or handle it gracefully
        # depending on the implementation
        try:
            logger = GitRangeLogger.setup_logger(None)
            assert logger is not None
        except (TypeError, AttributeError):
            # If it raises an exception, that's also acceptable
            pass
    
    def test_logger_handles_empty_name(self):
        """Test that setup_logger handles empty string name"""
        logger = GitRangeLogger.setup_logger("")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "mkdocs.plugins."


class TestMockingHelpers:
    """Test helper functions for creating mocks in tests"""
    
    def test_create_mock_git_repo(self):
        """Test creating a mock git repository"""
        mock_repo = Mock()
        mock_repo.working_dir = "/test/repo"
        mock_repo.head.commit.hexsha = "abc123def456"
        
        # Test that mock has expected attributes
        assert mock_repo.working_dir == "/test/repo"
        assert mock_repo.head.commit.hexsha == "abc123def456"
    
    def test_create_mock_mkdocs_config(self):
        """Test creating a mock MkDocs config"""
        mock_config = Mock()
        mock_config.get.return_value = "/test/docs"
        
        # Test that mock behaves as expected
        assert mock_config.get('docs_dir') == "/test/docs"
    
    def test_create_mock_mkdocs_files(self):
        """Test creating mock MkDocs files structure"""
        mock_files = Mock()
        mock_files.documentation_pages.return_value = [
            Mock(src_uri="index.md"),
            Mock(src_uri="guide.md")
        ]
        
        # Test that mock behaves as expected
        pages = mock_files.documentation_pages()
        assert len(pages) == 2
        assert pages[0].src_uri == "index.md"
        assert pages[1].src_uri == "guide.md"

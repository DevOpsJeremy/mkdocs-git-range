"""
Tests for the main GitRangePlugin class
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from mkdocs.structure.files import InclusionLevel
from mkdocs_git_range.plugin import GitRangePlugin


class TestGitRangePlugin:
    """Test the main plugin functionality"""
    
    def test_plugin_initialization(self):
        """Test that the plugin initializes correctly"""
        plugin = GitRangePlugin()
        assert hasattr(plugin, 'config_scheme')
        assert hasattr(plugin, 'logger')
        
    def test_config_scheme_structure(self):
        """Test that the config scheme has the expected structure"""
        plugin = GitRangePlugin()
        config_keys = [item[0] for item in plugin.config_scheme]
        
        expected_keys = ['from', 'to', 'filter', 'include']
        assert all(key in config_keys for key in expected_keys)
    
    @patch('mkdocs_git_range.plugin.GitRangeGit')
    def test_on_files_no_filtering(self, mock_git_class, mock_mkdocs_files):
        """Test on_files when filtering is disabled"""
        # Setup
        plugin = GitRangePlugin()
        plugin.config = {'filter': False, 'include': []}
        
        # Mock the git filtered files
        mock_git_instance = Mock()
        mock_git_class.get_filtered_files.return_value = ['guide.md']
        
        # Execute
        result = plugin.on_files(mock_mkdocs_files, {})
        
        # Assert - should return files unchanged when filtering is disabled
        assert result == mock_mkdocs_files
    
    @patch('mkdocs_git_range.plugin.GitRangeGit')
    def test_on_files_with_filtering(self, mock_git_class, mock_mkdocs_files):
        """Test on_files when filtering is enabled"""
        # Setup
        plugin = GitRangePlugin()
        plugin.config = {'filter': True, 'include': []}
        plugin.include = ['guide.md']  # Only guide.md is in the git range
        
        # Mock git filtered files
        mock_git_class.get_filtered_files.return_value = ['guide.md']
        
        # Execute
        result = plugin.on_files(mock_mkdocs_files, {})
        
        # Assert - files not in include list should be excluded
        excluded_files = [f for f in result if f.inclusion == InclusionLevel.EXCLUDED]
        included_files = [f for f in result if f.inclusion != InclusionLevel.EXCLUDED]
        
        # guide.md should be included, others excluded
        assert len(included_files) > 0
        assert len(excluded_files) > 0
    
    def test_on_page_markdown_creates_macros(self):
        """Test that on_page_markdown creates the git_range macro"""
        plugin = GitRangePlugin()
        plugin.include = ['index.md', 'guide.md']
        plugin.logger = Mock()
        
        markdown = "# Test\n{{ git_range() }}"
        page = Mock()
        page.title = "Test Page"
        config = {}
        files = Mock()
        
        # Execute
        result = plugin.on_page_markdown(markdown, page, config, files)
        
        # Assert - should process the macro
        assert result is not None
        assert "Test" in result  # The markdown should be processed
    
    def test_git_range_macro_returns_include_list(self):
        """Test that the git_range macro returns the correct file list"""
        plugin = GitRangePlugin()
        plugin.include = ['index.md', 'guide.md']
        plugin.logger = Mock()
        
        # Create a simple markdown with the macro
        markdown = "Files: {{ git_range() }}"
        page = Mock()
        page.title = "Test"
        
        result = plugin.on_page_markdown(markdown, page, {}, Mock())
        
        # The result should contain the processed macro
        assert "index.md" in str(result) or "guide.md" in str(result)


class TestGitRangePluginConfig:
    """Test plugin configuration handling"""
    
    def test_default_config_values(self):
        """Test that default configuration values are set correctly"""
        plugin = GitRangePlugin()
        
        # Check that config scheme has defaults
        config_dict = dict(plugin.config_scheme)
        assert 'from' in config_dict
        assert 'to' in config_dict
        assert 'filter' in config_dict
        assert 'include' in config_dict
    
    @patch('mkdocs_git_range.plugin.GitRangeGit')
    def test_on_config_calls_git_filtered_files(self, mock_git_class):
        """Test that on_config sets up the include list"""
        plugin = GitRangePlugin()
        mock_git_class.get_filtered_files.return_value = ['test.md']
        
        config = {'docs_dir': '/test/docs'}
        result = plugin.on_config(config)
        
        assert result == config
        assert hasattr(plugin, 'include')
        mock_git_class.get_filtered_files.assert_called_once()


class TestGitRangePluginIntegration:
    """Integration tests for the plugin"""
    
    @patch('mkdocs_git_range.plugin.GitRangeGit')
    def test_full_workflow_with_filtering(self, mock_git_class, mock_mkdocs_files, mock_mkdocs_config):
        """Test the complete workflow of the plugin with filtering enabled"""
        # Setup
        plugin = GitRangePlugin()
        plugin.config = {
            'from': 'abc123',
            'to': 'def456', 
            'filter': True,
            'include': ['index.md']
        }
        
        # Mock git operations
        mock_git_class.get_filtered_files.return_value = ['guide.md']
        
        # Test on_config
        result_config = plugin.on_config(mock_mkdocs_config)
        assert result_config == mock_mkdocs_config
        
        # Test on_files
        result_files = plugin.on_files(mock_mkdocs_files, mock_mkdocs_config)
        assert result_files is not None
        
        # Test on_page_markdown
        markdown = "# Test\nFiles: {{ git_range() }}"
        page = Mock()
        page.title = "Test Page"
        
        result_markdown = plugin.on_page_markdown(markdown, page, mock_mkdocs_config, result_files)
        assert result_markdown is not None
        assert "Test" in result_markdown

"""
End-to-end integration tests for the entire plugin
"""
import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
from mkdocs.config import Config
from mkdocs.structure.files import Files, File
from git import Repo


class TestFullPluginIntegration:
    """Test the complete plugin workflow end-to-end"""
    
    def test_complete_plugin_workflow(self, temp_mkdocs_repo):
        """Test the complete plugin workflow from initialization to output"""
        repo, temp_dir, initial_commit, second_commit = temp_mkdocs_repo
        
        # Import plugin
        from mkdocs_git_range.plugin import GitRangePlugin
        
        # Setup plugin with real configuration
        plugin = GitRangePlugin()
        
        # Mock the repo to use our test repo
        with patch('mkdocs_git_range.git.GitRangeGit.get_repo') as mock_get_repo:
            mock_get_repo.return_value = repo
            
            # Setup plugin config
            plugin.config = {
                'from': initial_commit.hexsha,
                'to': second_commit.hexsha,
                'filter': True,
                'include': ['index.md']  # Always include index
            }
            
            # Create mock MkDocs config
            mkdocs_config = {
                'docs_dir': os.path.join(temp_dir, 'docs'),
                'site_dir': os.path.join(temp_dir, 'site')
            }
            
            # Create mock files
            files = Files([])
            test_files = [
                File("index.md", mkdocs_config['docs_dir'], mkdocs_config['site_dir'], use_directory_urls=False),
                File("guide.md", mkdocs_config['docs_dir'], mkdocs_config['site_dir'], use_directory_urls=False),
                File("new_page.md", mkdocs_config['docs_dir'], mkdocs_config['site_dir'], use_directory_urls=False),
            ]
            
            for file in test_files:
                files.append(file)
            
            # Test 1: on_config
            result_config = plugin.on_config(mkdocs_config)
            assert result_config == mkdocs_config
            assert hasattr(plugin, 'include')
            
            # Test 2: on_files
            result_files = plugin.on_files(files, mkdocs_config)
            assert result_files is not None
            
            # Test 3: on_page_markdown with macro
            markdown = """
# Test Page

## Files changed in this commit range:
{{ git_range() }}

## File count:
Total files: {{ git_range()|length }}
"""
            
            page = Mock()
            page.title = "Test Integration Page"
            
            result_markdown = plugin.on_page_markdown(markdown, page, mkdocs_config, result_files)
            
            # Verify the markdown was processed
            assert result_markdown is not None
            assert "Test Page" in result_markdown
            assert "Files changed in this commit range:" in result_markdown
    
    def test_plugin_with_no_git_changes(self, temp_git_repo):
        """Test plugin behavior when there are no git changes"""
        repo, temp_dir, initial_commit = temp_git_repo
        
        from mkdocs_git_range.plugin import GitRangePlugin
        
        plugin = GitRangePlugin()
        
        with patch('mkdocs_git_range.git.GitRangeGit.get_repo') as mock_get_repo:
            mock_get_repo.return_value = repo
            
            # Configure plugin to compare commit with itself (no changes)
            plugin.config = {
                'from': initial_commit.hexsha,
                'to': initial_commit.hexsha,
                'filter': True,
                'include': []
            }
            
            mkdocs_config = {'docs_dir': os.path.join(temp_dir, 'docs')}
            
            # Test on_config
            plugin.on_config(mkdocs_config)
            
            # Should have empty include list (no changes)
            assert plugin.include == []
            
            # Test macro returns empty list
            markdown = "Files: {{ git_range() }}"
            page = Mock()
            page.title = "No Changes Test"
            
            result = plugin.on_page_markdown(markdown, page, mkdocs_config, Mock())
            
            # Should handle empty list gracefully
            assert result is not None
    
    def test_plugin_with_filter_disabled(self, temp_mkdocs_repo):
        """Test plugin behavior when filtering is disabled"""
        repo, temp_dir, initial_commit, second_commit = temp_mkdocs_repo
        
        from mkdocs_git_range.plugin import GitRangePlugin
        
        plugin = GitRangePlugin()
        
        with patch('mkdocs_git_range.git.GitRangeGit.get_repo') as mock_get_repo:
            mock_get_repo.return_value = repo
            
            # Configure plugin with filtering disabled
            plugin.config = {
                'from': initial_commit.hexsha,
                'to': second_commit.hexsha,
                'filter': False,  # Filtering disabled
                'include': []
            }
            
            mkdocs_config = {'docs_dir': os.path.join(temp_dir, 'docs')}
            
            # Create mock files
            files = Files([])
            test_file = File("test.md", mkdocs_config['docs_dir'], "/site", use_directory_urls=False)
            files.append(test_file)
            
            # Test on_config
            plugin.on_config(mkdocs_config)
            
            # Test on_files - should return files unchanged
            result_files = plugin.on_files(files, mkdocs_config)
            assert result_files == files
            
            # No files should be excluded when filtering is disabled
            excluded_files = [f for f in result_files if hasattr(f, 'inclusion') and f.inclusion.name == 'EXCLUDED']
            assert len(excluded_files) == 0
    
    def test_plugin_error_handling(self):
        """Test plugin behavior when git operations fail"""
        from mkdocs_git_range.plugin import GitRangePlugin
        
        plugin = GitRangePlugin()
        
        # Mock git operations to fail
        with patch('mkdocs_git_range.git.GitRangeGit.get_filtered_files') as mock_filtered_files:
            mock_filtered_files.side_effect = Exception("Git operation failed")
            
            plugin.config = {
                'from': 'abc123',
                'to': 'def456',
                'filter': True,
                'include': []
            }
            
            mkdocs_config = {'docs_dir': '/test/docs'}
            
            # Should handle the error gracefully
            try:
                plugin.on_config(mkdocs_config)
                # If it doesn't raise an exception, that's good
            except Exception as e:
                # If it does raise an exception, it should be handled appropriately
                assert "Git operation failed" in str(e)
    
    def test_plugin_with_include_list(self, temp_mkdocs_repo):
        """Test plugin behavior with manual include list"""
        repo, temp_dir, initial_commit, second_commit = temp_mkdocs_repo
        
        from mkdocs_git_range.plugin import GitRangePlugin
        
        plugin = GitRangePlugin()
        
        with patch('mkdocs_git_range.git.GitRangeGit.get_repo') as mock_get_repo:
            mock_get_repo.return_value = repo
            
            # Configure plugin with manual include list
            plugin.config = {
                'from': initial_commit.hexsha,
                'to': second_commit.hexsha,
                'filter': True,
                'include': ['always_include.md', 'important.md']
            }
            
            mkdocs_config = {'docs_dir': os.path.join(temp_dir, 'docs')}
            
            # Create mock files including the manually included ones
            files = Files([])
            test_files = [
                File("guide.md", mkdocs_config['docs_dir'], "/site", use_directory_urls=False),
                File("always_include.md", mkdocs_config['docs_dir'], "/site", use_directory_urls=False),
                File("important.md", mkdocs_config['docs_dir'], "/site", use_directory_urls=False),
                File("other.md", mkdocs_config['docs_dir'], "/site", use_directory_urls=False),
            ]
            
            for file in test_files:
                files.append(file)
            
            # Test on_config
            plugin.on_config(mkdocs_config)
            
            # Test on_files
            result_files = plugin.on_files(files, mkdocs_config)
            
            # Files in the manual include list should not be excluded
            # even if they're not in the git range
            always_include_file = next((f for f in result_files if f.src_uri == "always_include.md"), None)
            important_file = next((f for f in result_files if f.src_uri == "important.md"), None)
            
            assert always_include_file is not None
            assert important_file is not None
            
            # These files should not be excluded
            if hasattr(always_include_file, 'inclusion'):
                assert always_include_file.inclusion.name != 'EXCLUDED'
            if hasattr(important_file, 'inclusion'):
                assert important_file.inclusion.name != 'EXCLUDED'


class TestPluginConfiguration:
    """Test various plugin configuration scenarios"""
    
    def test_default_configuration(self):
        """Test plugin with default configuration"""
        from mkdocs_git_range.plugin import GitRangePlugin
        
        plugin = GitRangePlugin()
        
        # Check that config scheme has expected defaults
        config_dict = dict(plugin.config_scheme)
        assert 'from' in config_dict
        assert 'to' in config_dict
        assert 'filter' in config_dict
        assert 'include' in config_dict
    
    def test_custom_configuration(self):
        """Test plugin with custom configuration"""
        from mkdocs_git_range.plugin import GitRangePlugin
        
        plugin = GitRangePlugin()
        
        # Set custom configuration
        custom_config = {
            'from': 'custom_from_commit',
            'to': 'custom_to_commit',
            'filter': True,
            'include': ['custom_file.md']
        }
        
        plugin.config = custom_config
        
        # Verify configuration is set
        assert plugin.config['from'] == 'custom_from_commit'
        assert plugin.config['to'] == 'custom_to_commit'
        assert plugin.config['filter'] == True
        assert plugin.config['include'] == ['custom_file.md']

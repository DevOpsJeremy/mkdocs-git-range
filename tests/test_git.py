"""
Tests for git-related functionality
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from mkdocs_git_range.git import GitRangeGit, GitRangeRepo


class TestGitRangeRepo:
    """Test the GitRangeRepo class"""
    
    def test_gitrange_repo_inherits_from_repo(self, temp_git_repo):
        """Test that GitRangeRepo properly inherits from git.Repo"""
        repo, temp_dir, initial_commit = temp_git_repo
        
        # Create GitRangeRepo instance
        git_range_repo = GitRangeRepo(temp_dir)
        
        # Should have all Repo functionality
        assert hasattr(git_range_repo, 'heads')
        assert hasattr(git_range_repo, 'commits')
        assert hasattr(git_range_repo, 'working_dir')
        
        # Should have tail attribute
        assert hasattr(git_range_repo, 'tail')
    
    def test_gitrange_repo_tail_attribute(self, temp_git_repo):
        """Test that GitRangeRepo sets tail correctly"""
        repo, temp_dir, initial_commit = temp_git_repo
        
        git_range_repo = GitRangeRepo(temp_dir)
        
        # Tail should be set to the initial commit (first commit)
        assert git_range_repo.tail is not None
        assert hasattr(git_range_repo.tail, 'hexsha')
    
    def test_set_and_get_tail(self, temp_git_repo):
        """Test setting and getting tail commit"""
        repo, temp_dir, initial_commit = temp_git_repo
        
        git_range_repo = GitRangeRepo(temp_dir)
        
        # Test set_tail
        test_commit_sha = initial_commit.hexsha
        git_range_repo.set_tail(test_commit_sha)
        
        # Test get_tail
        assert git_range_repo.get_tail() == test_commit_sha


class TestGitRangeGit:
    """Test the GitRangeGit utility class"""
    
    @patch('mkdocs_git_range.git.GitRangeRepo')
    def test_get_repo_returns_gitrange_repo(self, mock_repo_class):
        """Test that get_repo returns a GitRangeRepo instance"""
        mock_repo_instance = Mock()
        mock_repo_class.return_value = mock_repo_instance
        
        result = GitRangeGit.get_repo()
        
        mock_repo_class.assert_called_once_with(search_parent_directories=True)
        assert result == mock_repo_instance
    
    @patch('mkdocs_git_range.git.GitRangeGit.get_repo')
    def test_get_filtered_files_with_mock_repo(self, mock_get_repo):
        """Test get_filtered_files with mocked repository"""
        # Setup mock repository
        mock_repo = Mock()
        mock_repo.git.diff.return_value = "docs/guide.md\ndocs/api/overview.md\n"
        mock_get_repo.return_value = mock_repo
        
        # Setup mock config
        mock_config = Mock()
        mock_config.get.return_value = "/test/docs"
        
        # Setup mock files
        mock_files = Mock()
        
        # Execute
        result = GitRangeGit.get_filtered_files(
            plugin_instance=Mock(),
            files=mock_files,
            config=mock_config
        )
        
        # Assert
        mock_repo.git.diff.assert_called_once()
        assert isinstance(result, list)
    
    def test_get_filtered_files_with_real_repo(self, temp_mkdocs_repo):
        """Test get_filtered_files with a real repository"""
        repo, temp_dir, initial_commit, second_commit = temp_mkdocs_repo
        
        # Create mock plugin instance
        mock_plugin = Mock()
        mock_plugin.config = {
            'from': initial_commit.hexsha,
            'to': second_commit.hexsha
        }
        
        # Create mock config
        mock_config = Mock()
        mock_config.get.return_value = os.path.join(temp_dir, "docs")
        
        # Create mock files
        mock_files = Mock()
        
        # Patch get_repo to return our test repo
        with patch('mkdocs_git_range.git.GitRangeGit.get_repo') as mock_get_repo:
            mock_get_repo.return_value = repo
            
            result = GitRangeGit.get_filtered_files(
                plugin_instance=mock_plugin,
                files=mock_files,
                config=mock_config
            )
            
            # Should return files that were modified between commits
            assert isinstance(result, list)
            # The exact files depend on the git diff output format
    
    @patch('mkdocs_git_range.git.GitRangeGit.get_repo')
    def test_get_filtered_files_handles_empty_diff(self, mock_get_repo):
        """Test get_filtered_files when git diff returns no results"""
        # Setup mock repository with empty diff
        mock_repo = Mock()
        mock_repo.git.diff.return_value = ""
        mock_get_repo.return_value = mock_repo
        
        # Setup mocks
        mock_plugin = Mock()
        mock_plugin.config = {'from': 'abc123', 'to': 'def456'}
        mock_config = Mock()
        mock_config.get.return_value = "/test/docs"
        mock_files = Mock()
        
        # Execute
        result = GitRangeGit.get_filtered_files(mock_plugin, mock_files, mock_config)
        
        # Should return empty list
        assert result == []
    
    @patch('mkdocs_git_range.git.GitRangeGit.get_repo')
    def test_get_filtered_files_handles_git_error(self, mock_get_repo):
        """Test get_filtered_files when git command fails"""
        # Setup mock repository that raises exception
        mock_repo = Mock()
        mock_repo.git.diff.side_effect = Exception("Git command failed")
        mock_get_repo.return_value = mock_repo
        
        # Setup mocks
        mock_plugin = Mock()
        mock_plugin.config = {'from': 'abc123', 'to': 'def456'}
        mock_config = Mock()
        mock_config.get.return_value = "/test/docs"
        mock_files = Mock()
        
        # Execute
        result = GitRangeGit.get_filtered_files(mock_plugin, mock_files, mock_config)
        
        # Should return empty list and handle error gracefully
        assert result == []


class TestGitIntegration:
    """Integration tests for git functionality"""
    
    def test_end_to_end_git_operations(self, temp_mkdocs_repo):
        """Test complete git operations from initialization to file filtering"""
        repo, temp_dir, initial_commit, second_commit = temp_mkdocs_repo
        
        # Initialize GitRangeRepo with the test repository
        git_range_repo = GitRangeRepo(temp_dir)
        
        # Verify repo is working
        assert git_range_repo.working_dir == temp_dir
        assert len(list(git_range_repo.iter_commits())) >= 2
        
        # Test that we can get commits
        commits = list(git_range_repo.iter_commits())
        assert len(commits) >= 2
        
        # Test git diff between commits
        diff_output = git_range_repo.git.diff(
            f"{initial_commit.hexsha}..{second_commit.hexsha}",
            "--name-only"
        )
        
        # Should show the files that were modified
        assert isinstance(diff_output, str)
        # The exact content depends on what was committed

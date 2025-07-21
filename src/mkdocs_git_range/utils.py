import os, logging
from git import (
    Repo,
    GitConfigParser,
    Commit
)

class GitRangeLogger():
    def setup_logger(name):
        # Get the plugin's logger
        log = logging.getLogger(f"mkdocs.plugins.{name}")

        return log

class GitRangeRepo(Repo):
    """
    A git.Repo subclass with additional functionality for git range operations.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the GitRangeRepo with an optional tail attribute.
        
        Args:
            path: Path to the git repository
            tail: The tail commit/reference for range operations
            *args, **kwargs: Additional arguments passed to git.Repo
        """
        super().__init__(*args, **kwargs)
        self.tail = Commit(
            repo=self,
            binsha=bytes.fromhex(
                self.git.execute(('git', 'rev-list', '--max-parents=0', 'HEAD'))
            )
        )
    
    def get_tail(self):
        """Get the current tail commit/reference."""
        return self.tail

class GitRangeGit():
    def get_repo():
        """
        Get the git repository instance.
        
        Returns:
            GitRangeRepo: The git repository instance.
        """
        return GitRangeRepo(search_parent_directories=True)

    def get_filtered_files(plugin, config):
        """
        Get a list of files modified within the commit range.
        
        Args:
            from_commit: The starting commit reference
            to_commit: The ending commit reference
            config: MkDocs config object containing docs_dir
            repo: GitRangeRepo instance (optional, will create if not provided)
            
        Returns:
            list: File paths relative to docs_dir that have been modified
        """
        # Get the absolute path to docs_dir from config
        docs_dir_path = config.get('docs_dir')
        repo_path = plugin.repo.working_dir
        
        try:
            # Execute git diff with the specified filters
            # --name-only: only show file names
            # --diff-filter=dux: d=deleted, u=unmerged, x=unknown (modify as needed)
            diff_output = plugin.repo.git.diff(
                f"{plugin.config['from']}..{plugin.config['to']}",
                "--name-only",
                "--diff-filter=dux",
                docs_dir_path
            )
            
            if not diff_output.strip():
                return []
            
            # Split output into lines and filter out empty lines
            modified_files = [f.strip() for f in diff_output.splitlines() if f.strip()]
            
            # Convert absolute paths to relative paths from docs_dir
            relative_files = []
            for file_path in modified_files:
                abs_path = os.path.join(repo_path, file_path)
                relative_path = os.path.relpath(abs_path, docs_dir_path)
                relative_files.append(relative_path)
            
            return relative_files
            
        except Exception as e:
            # Log error and return empty list as fallback
            plugin.logging.error(f"Error getting filtered files: {e}")
            return []

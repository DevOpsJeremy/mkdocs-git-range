from .utils import GitRangeUtils
from git import Repo, Commit


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
                self.git.execute(("git", "rev-list", "--max-parents=0", "HEAD"))
            ),
        )

    def get_tail(self):
        """Get the current tail commit/reference."""
        return self.tail


class GitRangeGit:
    def get_repo():
        """
        Get the git repository instance.

        Returns:
            GitRangeRepo: The git repository instance.
        """
        return GitRangeRepo(search_parent_directories=True)

    def get_filtered_files(plugin, files, config, from_ref=None, to_ref=None):
        if from_ref is None:
            from_ref = plugin.config["from"]
        if to_ref is None:
            to_ref = plugin.config["to"]

        docs_dir_path = config.get("docs_dir")

        try:
            # Execute git diff with the specified filters
            # --name-only: only show file names
            # --diff-filter=dux: d=deleted, u=unmerged, x=unknown
            diff_output = plugin.repo.git.diff(
                f"{from_ref}..{to_ref}",
                "--name-only",
                "--diff-filter=dux",
                docs_dir_path,
            )

            if not diff_output.strip():
                return []

            # Split output into lines and filter out empty lines
            diff_files = [f.strip() for f in diff_output.splitlines() if f.strip()]

            modified_files = []
            for file in files:
                if (
                    GitRangeUtils.convert_rel_docs_to_repo(
                        file.src_uri, plugin.repo, config
                    )
                    in diff_files
                ):
                    modified_files.append(file)

            return modified_files

        except Exception as e:
            # Log error and return empty list as fallback
            plugin.logging.error(f"Error getting filtered files: {e}")
            return []

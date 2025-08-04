from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.structure.files import InclusionLevel, File
from .utils import GitRangeLogger
from .git import GitRangeGit
from jinja2 import Environment, runtime


class GitRangePlugin(BasePlugin):
    """
    An MkDocs plugin to display the git range of the current documentation.
    """

    repo = GitRangeGit.get_repo()
    config_scheme = (
        ("from", config_options.Type(str, default=repo.tail.hexsha)),
        ("to", config_options.Type(str, default=repo.head.commit.hexsha)),
        ("filter", config_options.Type(bool, default=False)),
        ("include", config_options.Type(list, default=[])),
    )
    logger = GitRangeLogger.setup_logger(__name__)

    def on_config(self, config):
        def some_method(self):
            return "This is some method"
    
        File.some_method = some_method

    def on_files(self, files, config):
        """
        Process the files in the documentation.
        """
        # Create list of files to include based on git diff
        self.include = GitRangeGit.get_filtered_files(self, files, config)

        # Check if filtering is enabled
        if not self.config["filter"]:
            return files

        doc_pages = [page.src_uri for page in files.documentation_pages()]

        for file in files:
            # Skip if not a documentation page
            if file.src_uri not in doc_pages:
                continue

            # Skip if the file is in the include list (within the commit range) or config include
            if file.src_uri in self.include or file.src_uri in self.config["include"]:
                continue

            # Exclude from rendering the file
            file.inclusion = InclusionLevel.EXCLUDED
        return files

    def on_env(self, env, config, files):
        """
        Process the environment and add custom filters.
        """
        def git_range_macro(from_ref=None, to_ref=None):
            """Macro available in markdown and templates as {{ git_range() }}"""
            filtered_files = GitRangeGit.get_filtered_files(
                self, files, config, from_ref=from_ref, to_ref=to_ref
            )
            return filtered_files

        git_range_globals = {}
        git_range_globals["git_range"] = git_range_macro
        env.globals = {**env.globals, **git_range_globals}

        for file in files.documentation_pages():
            file.page.content = env.from_string(file.page.content).render(**git_range_globals)

        return env

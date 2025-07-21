from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.structure.files import InclusionLevel
from .utils import GitRangeLogger
from .git import GitRangeGit
#from .macros import macros
from jinja2 import Environment

class GitRangePlugin(BasePlugin):
    """
    An MkDocs plugin to display the git range of the current documentation.
    """
    
    repo = GitRangeGit.get_repo()
    config_scheme = (
        ('from', config_options.Type(str, default=repo.tail.hexsha)),
        ('to', config_options.Type(str, default=repo.head.commit.hexsha)),
        ('filter', config_options.Type(bool, default=False)),
        ('include', config_options.Type(list, default=[]))
    )
    logger = GitRangeLogger.setup_logger(__name__)

    def on_files(self, files, config):
        """
        Process the files in the documentation.
        """
        # Create list of files to include based on git diff
        self.include = GitRangeGit.get_filtered_files(self, files, config)

        # Check if filtering is enabled
        if not self.config['filter']:
            return files

        doc_pages = [page.src_uri for page in files.documentation_pages()]
        
        for file in files:
            # Skip if not a documentation page
            if not file.src_uri in doc_pages:
                continue

            # Skip if the file is in the include list (within the commit range) or config include
            if (file.src_uri in self.include or 
                file.src_uri in self.config['include']):
                continue

            # Exclude from rendering the file
            file.inclusion = InclusionLevel.EXCLUDED
        return files

    def on_page_markdown(self, markdown, page, config, files):
        """
        Process the markdown content of a page.
        """
        # Create a closure that captures config
        def git_range_macro(from_ref=None, to_ref=None):
            """Macro available in markdown as {{ git_range() }}"""
            return GitRangeGit.get_filtered_files(self, files, config, from_ref=from_ref, to_ref=to_ref)
        
        # Create macro dict with config-aware functions
        macros = {
            "git_range": git_range_macro
        }
        
        env = Environment()
        # Render the markdown with the custom environment
        return env.from_string(markdown).render(**macros)

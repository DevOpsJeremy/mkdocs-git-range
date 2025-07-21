from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from .utils import GitRangeLogger, GitRangeGit
from .macros import macros
from jinja2 import Environment

class GitRangePlugin(BasePlugin):
    """
    An MkDocs plugin to display the git range of the current documentation.
    """
    
    repo = GitRangeGit.get_repo()
    config_scheme = (
        ('from', config_options.Type(str, default=repo.tail.hexsha)),
        ('to', config_options.Type(str, default=repo.head.commit.hexsha)),
        ('filter', config_options.Type(bool, default=False))
    )
    logger = GitRangeLogger.setup_logger(__name__)

    def on_files(self, files, config):
        return
        self.logger.info(files.src_uris)
    
    def on_config(self, config):
        self.logger.info(self.config)
        self.logger.info(config.get('docs_dir'))
        self.logger.info(GitRangeGit.get_filtered_files(self, config))

    def on_page_markdown(self, markdown, page, config, files):
        """
        Process the markdown content of a page.
        """
        self.logger.info(f"Processing page: {page.title}")
        env = Environment()
        
        # Render the markdown with the custom environment
        return env.from_string(markdown).render(**macros)

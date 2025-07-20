from mkdocs.plugins import BasePlugin
from .utils import GitRangeLogger

class GitRange(BasePlugin):
    """
    A MkDocs plugin to display the git range of the current documentation.
    """
    logger = GitRangeLogger.setupLogger(__name__)

    def on_files(self, files, config):
        self.logger.info("GitRange plugin is processing files.")

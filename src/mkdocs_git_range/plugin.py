from mkdocs.plugins import BasePlugin
from .utils import GitRangeLogger
from . import filters

class GitRange(BasePlugin):
    """
    A MkDocs plugin to display the git range of the current documentation.
    """
    logger = GitRangeLogger.setupLogger(__name__)

    def on_env(self, env, config, files):
        # Register new filters to the Jinja2 environment
        # https://jinja.palletsprojects.com/en/stable/api/#jinja2.Environment.filters
        self.logger.info("git-range: Registering custom filters for Jinja2 environment.")
        env.filters['test_filter'] = filters.test_filter

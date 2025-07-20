import logging

class GitRangeLogger():
    def setupLogger(name):
        # Get the plugin's logger
        log = logging.getLogger(f"mkdocs.plugins.{name}")

        return log

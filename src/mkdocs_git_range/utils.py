import os, logging

class GitRangeLogger(logging.Logger):
    def setup_logger(name):
        # Get the plugin's logger
        log = logging.getLogger(f"mkdocs.plugins.{name}")

        return log

class GitRangeUtils():
    def convert_rel_docs_to_repo(path, repo, config):
        return os.path.relpath(
            os.path.join(config.get('docs_dir'), path),
            repo.working_dir
        )
    
    def convert_rel_repo_to_docs(path, repo, config):
        return os.path.relpath(
            os.path.join(repo.working_dir, path),
            config.get('docs_dir')
        )

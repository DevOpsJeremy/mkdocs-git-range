"""
Shared fixtures for mkdocs-git-range tests
"""
import pytest
import tempfile
import shutil
import os
from git import Repo
from mkdocs.config import Config
from mkdocs.structure.files import Files, File


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing"""
    temp_dir = tempfile.mkdtemp()
    repo = Repo.init(temp_dir)

    # Configure git user (required for commits)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Create initial commit
    test_file = os.path.join(temp_dir, "README.md")
    with open(test_file, "w") as f:
        f.write("# Test Repo\n")
    repo.index.add([test_file])
    initial_commit = repo.index.commit("Initial commit")

    yield repo, temp_dir, initial_commit

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_mkdocs_repo():
    """Create a temporary repository with MkDocs structure"""
    temp_dir = tempfile.mkdtemp()
    repo = Repo.init(temp_dir)

    # Configure git user
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Create docs directory and files
    docs_dir = os.path.join(temp_dir, "docs")
    os.makedirs(docs_dir)

    # Create initial docs
    files_to_create = [
        ("docs/index.md", "# Home\nWelcome to the docs"),
        ("docs/guide.md", "# Guide\nThis is a guide"),
        ("docs/api/overview.md", "# API Overview\nAPI documentation"),
        ("mkdocs.yml", "site_name: Test Site\ndocs_dir: docs\n")
    ]

    for file_path, content in files_to_create:
        full_path = os.path.join(temp_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    # Initial commit
    repo.index.add([f[0] for f in files_to_create])
    initial_commit = repo.index.commit("Initial docs")

    # Create second commit with changes
    with open(os.path.join(temp_dir, "docs/guide.md"), "w") as f:
        f.write("# Guide\nThis is an updated guide with more content")

    with open(os.path.join(temp_dir, "docs/new_page.md"), "w") as f:
        f.write("# New Page\nThis is a new page")

    repo.index.add(["docs/guide.md", "docs/new_page.md"])
    second_commit = repo.index.commit("Update guide and add new page")

    yield repo, temp_dir, initial_commit, second_commit

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_mkdocs_config():
    """Create a mock MkDocs config object"""
    config = Config(schema=())
    config['docs_dir'] = '/test/docs'
    config['site_dir'] = '/test/site'
    return config


@pytest.fixture
def mock_mkdocs_files():
    """Create mock MkDocs Files object with sample files"""
    files = Files([])

    # Add some test files
    test_files = [
        File("index.md", "/test/docs", "/test/site", use_directory_urls=False),
        File("guide.md", "/test/docs", "/test/site", use_directory_urls=False),
        File("api/overview.md", "/test/docs", "/test/site", use_directory_urls=False),
    ]

    for file in test_files:
        files.append(file)

    return files

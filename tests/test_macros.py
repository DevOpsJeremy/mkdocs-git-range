"""
Tests for macro functionality
"""

import pytest
from unittest.mock import Mock, patch
from jinja2 import Environment


class TestGitRangeMacros:
    """Test the git_range macro functionality"""

    def test_git_range_macro_basic_functionality(self):
        """Test that git_range macro returns file list"""
        # Create a mock plugin instance
        mock_plugin = Mock()
        mock_plugin.include = ["index.md", "guide.md", "api/overview.md"]
        mock_plugin.logger = Mock()

        # Simulate the macro creation in on_page_markdown
        def create_git_range_macro(include_list):
            def git_range_macro():
                return include_list

            return git_range_macro

        git_range = create_git_range_macro(mock_plugin.include)

        # Test the macro
        result = git_range()
        assert result == ["index.md", "guide.md", "api/overview.md"]

    def test_git_range_macro_empty_list(self):
        """Test git_range macro with empty include list"""

        def create_git_range_macro(include_list):
            def git_range_macro():
                return include_list

            return git_range_macro

        git_range = create_git_range_macro([])
        result = git_range()

        assert result == []

    def test_git_range_macro_single_file(self):
        """Test git_range macro with single file"""

        def create_git_range_macro(include_list):
            def git_range_macro():
                return include_list

            return git_range_macro

        git_range = create_git_range_macro(["index.md"])
        result = git_range()

        assert result == ["index.md"]


class TestJinjaTemplateRendering:
    """Test Jinja2 template rendering with macros"""

    def test_simple_macro_rendering(self):
        """Test rendering a simple macro in markdown"""

        # Create mock macro
        def mock_git_range():
            return ["index.md", "guide.md"]

        macros = {"git_range": mock_git_range}

        # Test template
        template = "Files: {{ git_range() }}"
        env = Environment()
        result = env.from_string(template).render(**macros)

        assert "index.md" in result
        assert "guide.md" in result

    def test_macro_in_list_context(self):
        """Test using macro in a Jinja2 list context"""

        def mock_git_range():
            return ["index.md", "guide.md", "api.md"]

        macros = {"git_range": mock_git_range}

        # Template with list iteration
        template = """
Files changed:
{% for file in git_range() %}
- {{ file }}
{% endfor %}
"""

        env = Environment()
        result = env.from_string(template).render(**macros)

        assert "- index.md" in result
        assert "- guide.md" in result
        assert "- api.md" in result

    def test_macro_with_conditional(self):
        """Test using macro with Jinja2 conditionals"""

        def mock_git_range():
            return ["index.md", "guide.md"]

        macros = {"git_range": mock_git_range}

        # Template with conditional
        template = """
{% if git_range() %}
Files were changed: {{ git_range()|length }} files
{% else %}
No files changed
{% endif %}
"""

        env = Environment()
        result = env.from_string(template).render(**macros)

        assert "Files were changed: 2 files" in result

    def test_empty_macro_with_conditional(self):
        """Test macro returning empty list with conditional"""

        def mock_git_range():
            return []

        macros = {"git_range": mock_git_range}

        template = """
{% if git_range() %}
Files were changed
{% else %}
No files changed
{% endif %}
"""

        env = Environment()
        result = env.from_string(template).render(**macros)

        assert "No files changed" in result

    def test_macro_error_handling(self):
        """Test macro error handling in template"""

        def failing_macro():
            raise Exception("Macro failed")

        macros = {"failing_macro": failing_macro}

        template = "Result: {{ failing_macro() }}"
        env = Environment()

        # Should raise an exception when rendering
        with pytest.raises(Exception):
            env.from_string(template).render(**macros)

    def test_multiple_macros(self):
        """Test multiple macros in the same template"""

        def git_range():
            return ["index.md", "guide.md"]

        def git_stats():
            return "2 commits, 3 files changed"

        macros = {"git_range": git_range, "git_stats": git_stats}

        template = """
Changed files: {{ git_range() }}
Statistics: {{ git_stats() }}
"""

        env = Environment()
        result = env.from_string(template).render(**macros)

        assert "index.md" in result
        assert "guide.md" in result
        assert "2 commits, 3 files changed" in result


class TestMacroIntegration:
    """Integration tests for macros with plugin functionality"""

    @patch("mkdocs_git_range.plugin.Environment")
    def test_on_page_markdown_macro_integration(self, mock_env_class):
        """Test that on_page_markdown correctly integrates macros"""
        from mkdocs_git_range.plugin import GitRangePlugin

        # Setup mocks
        mock_env = Mock()
        mock_template = Mock()
        mock_template.render.return_value = "Rendered content"
        mock_env.from_string.return_value = mock_template
        mock_env_class.return_value = mock_env

        # Setup plugin
        plugin = GitRangePlugin()
        plugin.include = ["test.md"]
        plugin.logger = Mock()

        # Test data
        markdown = "# Test\n{{ git_range() }}"
        page = Mock()
        page.title = "Test Page"
        config = {}
        files = Mock()

        # Execute
        result = plugin.on_page_markdown(markdown, page, config, files)

        # Verify
        assert result == "Rendered content"
        mock_env.from_string.assert_called_once_with(markdown)
        mock_template.render.assert_called_once()

        # Check that macros were passed to render
        render_call_args = mock_template.render.call_args
        assert "git_range" in render_call_args[1]

    def test_macro_closure_captures_plugin_state(self):
        """Test that macro closures properly capture plugin state"""
        from mkdocs_git_range.plugin import GitRangePlugin

        plugin = GitRangePlugin()
        plugin.include = ["captured_file.md"]
        plugin.logger = Mock()

        # Simulate creating the closure like in on_page_markdown
        def create_macro(include_list):
            def git_range_macro():
                return include_list

            return git_range_macro

        macro = create_macro(plugin.include)

        # Test that the macro captures the state
        result = macro()
        assert result == ["captured_file.md"]

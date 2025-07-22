from mkdocs_git_range.plugin import GitRangePlugin


def test_plugin_can_be_initialized():
    """Test that the GitRangePlugin can be created without errors"""
    plugin = GitRangePlugin()
    
    # Basic assertions to verify the plugin is properly initialized
    assert plugin is not None
    assert hasattr(plugin, 'config_scheme')
    assert hasattr(plugin, 'logger')

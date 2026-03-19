import os

import pytest


def test_imports():
    """Ensure essential modules can be imported without crashing."""
    try:
        from agent.documentary_agent import DocumentaryAgent
        from mcp.notion_client import execute_tool
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")


def test_streamlit_config_exists():
    """Check if the Streamlit theme config was created."""
    config_path = os.path.join(".streamlit", "config.toml")
    assert os.path.exists(config_path), "Streamlit config.toml should exist"


def test_sample_output_exists():
    """Check if the sample output data exists."""
    data_path = os.path.join("data", "sample_output.json")
    assert os.path.exists(data_path), "sample_output.json should exist"

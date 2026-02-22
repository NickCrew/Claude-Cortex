import pytest
from pathlib import Path
from claude_ctx_py.core.hooks import validate_hooks_config, _check_hook_executable

def test_check_hook_executable_exists(tmp_path):
    script = tmp_path / "test.py"
    script.write_text("print('test')")
    
    # Should be valid (exists)
    assert _check_hook_executable(f"python3 {script}") is None
    # Test with interpreter and flags
    assert _check_hook_executable(f"python3 -u {script}") is None
    # Test with env indirection
    assert _check_hook_executable(f"/usr/bin/env python3 {script}") is None

def test_check_hook_executable_missing():
    # Absolute path that doesn't exist
    assert _check_hook_executable("python3 /tmp/non_existent_script_xyz.py") is not None

def test_check_hook_executable_malformed():
    # Unterminated quote
    result = _check_hook_executable("python3 'unterminated")
    assert "Malformed" in result

def test_check_hook_executable_relative():
    # Relative paths are currently skipped (returns None)
    assert _check_hook_executable("python3 ./local_script.py") is None

def test_validate_hooks_config_missing_script():
    config = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "",
                    "hooks": [
                        {"type": "command", "command": "python3 /tmp/missing_xyz.py"}
                    ]
                }
            ]
        }
    }
    is_valid, errors = validate_hooks_config(config)
    # It might still be "valid" in the sense of JSON structure, but should have errors
    assert not is_valid
    assert any("missing_xyz.py" in e for e in errors)


try:
    from claude_ctx_py.tui import main, AgentTUI
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()

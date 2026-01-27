"""Dashboard command handler."""

import uvicorn
from .server.main import app

def dashboard(host: str = "127.0.0.1", port: int = 8000) -> int:
    """Start the dashboard server."""
    print(f"Starting Cortex Dashboard at http://{host}:{port}")
    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
    return 0


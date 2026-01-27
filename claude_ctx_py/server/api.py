"""API endpoints for Cortex dashboard."""

from typing import List, Dict, Any
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get system status."""
    return {
        "status": "online",
        "version": "2.5.0",
    }

from claude_ctx_py.core.agents import build_agent_graph

# ... existing imports ...

@router.get("/agents")
async def get_agents() -> List[Dict[str, str]]:
    """List available agents."""
    agents = []
    try:
        nodes = build_agent_graph()
        
        for node in nodes:
            content = ""
            try:
                content = node.path.read_text(encoding="utf-8")
            except Exception:
                pass
                
            agents.append({
                "name": node.name,
                "state": node.status, # "active" or "disabled"
                "category": node.category or "General",
                "content": content
            })

    except Exception as e:
        print(f"Error fetching agents: {e}")
        pass
        
    return sorted(agents, key=lambda x: (x.get("category", ""), x.get("name", "")))

@router.post("/agents/{name}/activate")
async def activate_agent(name: str) -> Dict[str, Any]:
    """Activate an agent."""
    from claude_ctx_py import core
    code, msg = core.agent_activate(name)
    return {"success": code == 0, "message": msg}

@router.post("/agents/{name}/deactivate")
async def deactivate_agent(name: str) -> Dict[str, Any]:
    """Deactivate an agent."""
    from claude_ctx_py import core
    code, msg = core.agent_deactivate(name)
    return {"success": code == 0, "message": msg}

@router.get("/modes")
async def get_modes() -> List[Dict[str, str]]:
    """List available modes."""
    modes = []
    try:
        from claude_ctx_py.core.base import _iter_md_files, _resolve_cortex_root
        
        root = _resolve_cortex_root()
        modes_dir = root / "modes"
        
        if modes_dir.exists():
            for path in _iter_md_files(modes_dir):
                name = path.stem
                modes.append({"name": name})
    except Exception:
        pass
    return sorted(modes, key=lambda x: x["name"])

@router.get("/workflows")
async def get_workflows() -> List[Dict[str, str]]:
    """List available workflows."""
    workflows = []
    try:
        from claude_ctx_py.core.base import _resolve_claude_dir
        
        claude_dir = _resolve_claude_dir()
        workflows_dir = claude_dir / "workflows"
        
        if workflows_dir.exists():
            for path in workflows_dir.glob("*.yaml"):
                if path.name == "README.md": continue
                workflows.append({"name": path.stem})
    except Exception:
        pass
    return sorted(workflows, key=lambda x: x["name"])

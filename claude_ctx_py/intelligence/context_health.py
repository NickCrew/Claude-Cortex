"""Context Health Analyzer.

Analyzes the alignment between active context (modes, agents) and actual user activity.
"""
from typing import List, Dict, Set
from pathlib import Path
import os

class ContextHealth:
    """Analyzes context alignment and calculates health score."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def calculate_health(self, active_modes: List[str], active_agents: List[str], recent_files: List[str]) -> Dict[str, any]:
        """Calculate health score (0-100) and identify issues.

        Args:
            active_modes: List of currently active mode names.
            active_agents: List of currently active agent names.
            recent_files: List of paths to recently modified files.

        Returns:
            Dict containing score, issues, and suggestions.
        """
        issues = []
        score = 100

        # 1. Check Language Alignment
        extensions = {os.path.splitext(f)[1] for f in recent_files}
        
        if ".py" in extensions and "python-pro" not in active_agents:
            issues.append("Editing Python files but 'python-pro' agent is inactive.")
            score -= 15
        
        if (".ts" in extensions or ".tsx" in extensions) and "typescript-pro" not in active_agents:
            issues.append("Editing TypeScript files but 'typescript-pro' agent is inactive.")
            score -= 15

        # 2. Check Mode Alignment
        # If editing many files rapidly, suggest Amphetamine
        if len(recent_files) > 5 and "Amphetamine" not in active_modes:
             issues.append("High file churn detected. Consider 'Amphetamine' mode for speed.")
             score -= 5 # Minor suggestion

        # 3. Security Check
        # If touching sensitive files without Security Audit
        sensitive_keywords = ["auth", "secret", "password", "key", "token"]
        sensitive_files = [f for f in recent_files if any(k in f.lower() for k in sensitive_keywords)]
        
        if sensitive_files and "Security_Audit" not in active_modes:
             issues.append(f"Editing sensitive files ({len(sensitive_files)}) without 'Security Audit' mode.")
             score -= 25

        # 4. Agent Overload
        if len(active_agents) > 3:
            issues.append(f"High cognitive load: {len(active_agents)} agents active. Context may be diluted.")
            score -= 10

        # 5. Stale Agent Detection (Recommending DISABLE)
        recommendations = []
        
        # Check for unused language agents
        if "python-pro" in active_agents and ".py" not in extensions:
            issues.append("Agent 'python-pro' is active but no Python files are being edited.")
            recommendations.append({"type": "disable", "target": "python-pro", "reason": "No Python activity"})
            score -= 5

        if "typescript-pro" in active_agents and not any(e in extensions for e in [".ts", ".tsx"]):
             issues.append("Agent 'typescript-pro' is active but no TypeScript files are being edited.")
             recommendations.append({"type": "disable", "target": "typescript-pro", "reason": "No TypeScript activity"})
             score -= 5

        # 6. Mode Conflict Detection
        if "Amphetamine" in active_modes:
            if "Security_Audit" in active_modes:
                issues.append("Conflict: 'Amphetamine' (speed) and 'Security_Audit' (caution) are both active.")
                score -= 20
                recommendations.append({"type": "disable", "target": "Amphetamine", "reason": "Conflict with Security Audit"})
            if "Architect" in active_modes:
                issues.append("Conflict: 'Amphetamine' (hacking) and 'Architect' (planning) are both active.")
                score -= 15
                recommendations.append({"type": "disable", "target": "Amphetamine", "reason": "Conflict with Architect"})

        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "status": "Healthy" if score > 80 else "Warning" if score > 50 else "Critical"
        }

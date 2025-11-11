"""AI assistant CLI commands for intelligent recommendations."""

from pathlib import Path
import json
from .intelligence import IntelligentAgent
from .core import _resolve_claude_dir


def ai_recommend() -> int:
    """Show AI recommendations for the current context.

    Returns:
        Exit code (0 for success)
    """
    # Initialize intelligent agent
    claude_dir = _resolve_claude_dir()
    agent = IntelligentAgent(claude_dir / "intelligence")

    # Analyze context
    agent.analyze_context()

    # Get recommendations
    recommendations = agent.get_recommendations()

    if not recommendations:
        print("🤖 No recommendations at this time.")
        print("   Context analysis found no specific suggestions.")
        return 0

    print("🤖 AI RECOMMENDATIONS\n")
    print("═" * 70)

    for i, rec in enumerate(recommendations, 1):
        # Urgency indicator
        if rec.urgency == "critical":
            urgency_icon = "🔴"
        elif rec.urgency == "high":
            urgency_icon = "🟡"
        elif rec.urgency == "medium":
            urgency_icon = "🔵"
        else:
            urgency_icon = "⚪"

        # Auto-activate indicator
        auto_badge = " [AUTO]" if rec.auto_activate else ""

        print(f"\n{i}. {urgency_icon} {rec.agent_name}{auto_badge}")
        print(f"   Confidence: {rec.confidence * 100:.0f}%")
        print(f"   Reason: {rec.reason}")

    # Show workflow prediction
    print("\n" + "═" * 70)
    print("\n🎯 WORKFLOW PREDICTION\n")

    workflow = agent.predict_workflow()

    if workflow:
        print(f"Workflow: {workflow.workflow_name}")
        print(f"Confidence: {workflow.confidence * 100:.0f}%")
        print(
            f"Estimated Duration: {workflow.estimated_duration // 60}m {workflow.estimated_duration % 60}s"
        )
        print(f"Success Probability: {workflow.success_probability * 100:.0f}%")
        print(f"\nAgent Sequence:")
        for i, agent_name in enumerate(workflow.agents_sequence, 1):
            print(f"  {i}. {agent_name}")
    else:
        print("Not enough data for workflow prediction.")
        print("(Need 3+ similar sessions)")

    # Show context
    print("\n" + "═" * 70)
    print("\n📊 CONTEXT ANALYSIS\n")

    context = agent.current_context
    if context:
        print(f"Files Changed: {len(context.files_changed)}")

        contexts = []
        if context.has_frontend:
            contexts.append("Frontend")
        if context.has_backend:
            contexts.append("Backend")
        if context.has_database:
            contexts.append("Database")
        if context.has_tests:
            contexts.append("Tests")
        if context.has_auth:
            contexts.append("Auth")
        if context.has_api:
            contexts.append("API")

        if contexts:
            print(f"Detected: {', '.join(contexts)}")

        if context.errors_count > 0 or context.test_failures > 0:
            print(
                f"\n⚠️  Issues: {context.errors_count} errors, {context.test_failures} test failures"
            )

    print("\n" + "═" * 70)
    print("\n💡 TIP: Press '0' in the TUI for interactive AI assistant")
    print("        Press 'A' to auto-activate recommended agents")

    return 0


def ai_auto_activate() -> int:
    """Auto-activate high-confidence agent recommendations.

    Returns:
        Exit code (0 for success)
    """
    from .core import agent_activate

    # Initialize intelligent agent
    claude_dir = _resolve_claude_dir()
    agent = IntelligentAgent(claude_dir / "intelligence")

    # Analyze context
    agent.analyze_context()

    # Get auto-activation candidates
    auto_agents = agent.get_auto_activations()

    if not auto_agents:
        print("🤖 No auto-activation recommendations.")
        print("   Current context doesn't warrant automatic changes.")
        return 0

    print(f"🤖 Auto-activating {len(auto_agents)} agents...\n")

    activated = []
    failed = []

    for agent_name in auto_agents:
        try:
            exit_code, message = agent_activate(agent_name)
            if exit_code == 0:
                activated.append(agent_name)
                agent.mark_auto_activated(agent_name)
                print(f"✓ {agent_name}")
            else:
                failed.append(agent_name)
                print(f"✗ {agent_name}: {message}")
        except Exception as e:
            failed.append(agent_name)
            print(f"✗ {agent_name}: {str(e)}")

    print(f"\n✓ Activated {len(activated)}/{len(auto_agents)} agents")

    if failed:
        print(f"✗ Failed: {', '.join(failed)}")
        return 1

    return 0


def ai_export_json(output_file: str = "ai-recommendations.json") -> int:
    """Export AI recommendations to JSON.

    Args:
        output_file: Output file path

    Returns:
        Exit code (0 for success)
    """
    # Initialize intelligent agent
    claude_dir = _resolve_claude_dir()
    agent = IntelligentAgent(claude_dir / "intelligence")

    # Analyze context
    agent.analyze_context()

    # Get smart suggestions
    suggestions = agent.get_smart_suggestions()

    # Export to file
    output_path = Path(output_file)
    with open(output_path, "w") as f:
        json.dump(suggestions, f, indent=2)

    print(f"✓ Exported AI recommendations to {output_path}")
    print(
        f"  {len(suggestions.get('agent_recommendations', []))} agent recommendations"
    )

    workflow = suggestions.get("workflow_prediction")
    if workflow:
        print(f"  1 workflow prediction ({workflow['confidence']} confidence)")

    return 0


def ai_record_success(outcome: str = "success") -> int:
    """Record the current session as successful for learning.

    Args:
        outcome: Outcome description

    Returns:
        Exit code (0 for success)
    """
    from .core.base import _parse_active_entries
    from datetime import datetime

    # Initialize intelligent agent
    claude_dir = _resolve_claude_dir()
    agent = IntelligentAgent(claude_dir / "intelligence")

    # Analyze context
    context = agent.analyze_context()

    # Get active agents
    active_agents_file = claude_dir / "agents" / "active.txt"
    active_agents = []
    if active_agents_file.exists():
        active_agents = list(_parse_active_entries(active_agents_file))

    if not active_agents:
        print("⚠️  No active agents to record.")
        return 1

    # Calculate duration (use a default for now)
    duration = 600  # 10 minutes default

    # Record success
    agent.record_session_success(
        agents_used=active_agents, duration=duration, outcome=outcome
    )

    print(f"✓ Recorded successful session for learning")
    print(f"  Context: {len(context.files_changed)} files changed")
    print(f"  Agents: {', '.join(active_agents)}")
    print(f"  Outcome: {outcome}")
    print(f"\n💡 This session will improve future recommendations!")

    return 0

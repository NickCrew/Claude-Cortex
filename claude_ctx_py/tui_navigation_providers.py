"""Navigation command providers for Textual's native command palette.

This prototype demonstrates:
1. Navigation stack with back/forward support
2. View history tracking
3. Cross-view item search
4. Integration with Textual's native command palette
"""

from __future__ import annotations

from typing import AsyncIterator, Callable, Any

from textual.command import Hit, Hits, Provider

from .tui_icons import Icons


class NavigationProvider(Provider):
    """Command provider for navigation history (back/forward/recent views).

    Enables browser-like navigation:
    - "back" → Go to previous view
    - "forward" → Go to next view
    - "recent" → Show recently viewed screens
    """

    @property
    def app_instance(self) -> Any:
        """Get typed app instance."""
        return self.app

    async def search(self, query: str) -> AsyncIterator[Hit]:
        """Search for navigation commands.

        Args:
            query: Search query from command palette

        Yields:
            Navigation command hits
        """
        matcher = self.matcher(query)
        app = self.app_instance

        # Back command (if history exists)
        if hasattr(app, 'navigation_index') and app.navigation_index > 0:
            previous_view = app.navigation_stack[app.navigation_index - 1]
            from .tui.constants import VIEW_TITLES
            previous_title = VIEW_TITLES.get(previous_view, previous_view)

            if match := matcher.match("back previous"):
                yield Hit(
                    match + 10,  # Boost score for common navigation
                    matcher.highlight(f"{Icons.ARROW_LEFT} Back"),
                    self._navigate_back,
                    help=f"Return to [cyan]{previous_title}[/cyan]",
                )

        # Forward command (if forward history exists)
        if hasattr(app, 'navigation_index') and \
           hasattr(app, 'navigation_stack') and \
           app.navigation_index < len(app.navigation_stack) - 1:
            next_view = app.navigation_stack[app.navigation_index + 1]
            from .tui.constants import VIEW_TITLES
            next_title = VIEW_TITLES.get(next_view, next_view)

            if match := matcher.match("forward next"):
                yield Hit(
                    match + 10,
                    matcher.highlight(f"Forward {Icons.ARROW_RIGHT}"),
                    self._navigate_forward,
                    help=f"Go to [cyan]{next_title}[/cyan]",
                )

        # Recent views (last 10, excluding current)
        if hasattr(app, 'navigation_stack'):
            # Get unique recent views (excluding current)
            seen = set()
            recent_views = []
            for view in reversed(app.navigation_stack):
                if view != app.current_view and view not in seen:
                    recent_views.append(view)
                    seen.add(view)
                    if len(recent_views) >= 10:
                        break

            from .tui.constants import VIEW_TITLES
            for idx, view_name in enumerate(recent_views):
                view_title = VIEW_TITLES.get(view_name, view_name)
                if match := matcher.match(f"recent {view_title} {view_name}"):
                    yield Hit(
                        match,
                        matcher.highlight(f"{Icons.CLOCK} Recent: {view_title}"),
                        self._jump_to_view(view_name),
                        help=f"[dim]Return to recently viewed {view_name}[/dim]",
                    )

    def _navigate_back(self) -> None:
        """Navigate to previous view in history."""
        app = self.app_instance
        if hasattr(app, 'navigation_index') and app.navigation_index > 0:
            app.navigation_index -= 1
            new_view = app.navigation_stack[app.navigation_index]
            app.current_view = new_view
            app.notify(f"{Icons.ARROW_LEFT} Back to {new_view}", severity="information")

    def _navigate_forward(self) -> None:
        """Navigate to next view in history."""
        app = self.app_instance
        if hasattr(app, 'navigation_index') and \
           hasattr(app, 'navigation_stack') and \
           app.navigation_index < len(app.navigation_stack) - 1:
            app.navigation_index += 1
            new_view = app.navigation_stack[app.navigation_index]
            app.current_view = new_view
            app.notify(f"Forward {Icons.ARROW_RIGHT} {new_view}", severity="information")

    def _jump_to_view(self, view_name: str) -> Callable[[], None]:
        """Create callback to jump to specific view.

        Args:
            view_name: Target view name

        Returns:
            Callback function
        """
        def callback() -> None:
            app = self.app_instance
            app.current_view = view_name
            app.notify(f"Jumped to {view_name}", severity="information")
        return callback


class ViewNavigationProvider(Provider):
    """Command provider for view switching with enhanced metadata.

    Provides all views with descriptions and keyboard shortcuts.
    """

    @property
    def app_instance(self) -> Any:
        """Get typed app instance."""
        return self.app

    async def search(self, query: str) -> AsyncIterator[Hit]:
        """Search for view navigation commands.

        Args:
            query: Search query from command palette

        Yields:
            View navigation command hits
        """
        matcher = self.matcher(query)

        # Define all views with metadata
        views = [
            # Primary views (numeric keys)
            ("overview", "📊 Overview", "Dashboard and metrics", "1"),
            ("agents", "👥 Agents", "View and manage agents", "2"),
            ("modes", "🎨 Modes", "View behavioral modes", "3"),
            ("rules", "📜 Rules", "View active rules", "4"),
            ("principles", "📝 Principles", "Manage principles snippets", "p"),
            ("skills", "💎 Skills", "Browse skill library", "5"),
            ("workflows", "⚙️ Workflows", "Monitor workflows", "6"),
            ("mcp", "🔌 MCP", "Manage MCP servers", "7"),
            ("profiles", "👤 Profiles", "Manage profiles", "8"),
            ("export", "📦 Export", "Configure export", "9"),
            ("ai_assistant", "🤖 AI Assistant", "AI assistant view", "0"),

            # Secondary views (mnemonic keys)
            ("watch_mode", "👁️ Watch Mode", "File watching", "w"),
            ("flags", "🚩 Flags", "Flag explorer", "F"),
            ("assets", "📁 Assets", "Asset manager", "A"),
            ("memory", "🧠 Memory", "Memory vault", "M"),
            ("scenarios", "🗺️ Scenarios", "View scenarios", "S"),
            ("orchestrate", "🎯 Orchestrate", "Task orchestration", "o"),
            ("galaxy", "✨ Galaxy", "Agent constellation", "g"),
            ("flag_manager", "⚙️ Flag Manager", "Manage flags", "Ctrl+G"),
            ("tasks", "📋 Tasks", "Task queue", "t"),
            ("commands", "⌨️ Commands", "Slash commands", "/"),
        ]

        for view_name, title, description, shortcut in views:
            # Match against title, view name, and description
            search_text = f"{title} {view_name} {description}"
            if match := matcher.match(search_text):
                yield Hit(
                    match,
                    matcher.highlight(title),
                    self._switch_to_view(view_name),
                    help=f"{description} [dim]│[/dim] [yellow]Key: {shortcut}[/yellow]",
                )

    def _switch_to_view(self, view_name: str) -> Callable[[], None]:
        """Create callback to switch to specific view.

        Args:
            view_name: Target view name

        Returns:
            Callback function
        """
        def callback() -> None:
            app = self.app_instance
            app.current_view = view_name
        return callback


class ItemJumpProvider(Provider):
    """Command provider for jumping to specific items across views.

    Enables cross-view search:
    - Search agents by name
    - Search skills by name
    - Search workflows by name
    - Search modes, rules, etc.

    Automatically switches to correct view and selects the item.
    """

    @property
    def app_instance(self) -> Any:
        """Get typed app instance."""
        return self.app

    async def search(self, query: str) -> AsyncIterator[Hit]:
        """Search for items across all views.

        Args:
            query: Search query from command palette

        Yields:
            Item jump command hits
        """
        matcher = self.matcher(query)
        app = self.app_instance

        # Search agents
        if hasattr(app, 'agents'):
            for agent in app.agents:
                name = agent.get('name', '')
                description = agent.get('description', '')
                active = agent.get('active', False)

                search_text = f"agent {name} {description}"
                if match := matcher.match(search_text):
                    status = Icons.SUCCESS if active else Icons.SPACE
                    yield Hit(
                        match,
                        matcher.highlight(f"{status} Agent: {name}"),
                        self._jump_to_item("agents", name),
                        help=f"[dim]{description}[/dim]",
                    )

        # Search skills
        if hasattr(app, 'skills'):
            for skill in app.skills:
                name = skill.get('name', '')
                description = skill.get('description', '')

                search_text = f"skill {name} {description}"
                if match := matcher.match(search_text):
                    yield Hit(
                        match,
                        matcher.highlight(f"💎 Skill: {name}"),
                        self._jump_to_item("skills", name),
                        help=f"[dim]{description}[/dim]",
                    )

        # Search workflows
        if hasattr(app, 'workflows'):
            for workflow in app.workflows:
                name = workflow.get('name', '')
                description = workflow.get('description', '')

                search_text = f"workflow {name} {description}"
                if match := matcher.match(search_text):
                    yield Hit(
                        match,
                        matcher.highlight(f"⚙️ Workflow: {name}"),
                        self._jump_to_item("workflows", name),
                        help=f"[dim]{description}[/dim]",
                    )

        # Search modes
        if hasattr(app, 'modes'):
            for mode in app.modes:
                name = mode.get('name', '')
                description = mode.get('description', '')
                active = mode.get('active', False)

                search_text = f"mode {name} {description}"
                if match := matcher.match(search_text):
                    status = Icons.SUCCESS if active else Icons.SPACE
                    yield Hit(
                        match,
                        matcher.highlight(f"{status} Mode: {name}"),
                        self._jump_to_item("modes", name),
                        help=f"[dim]{description}[/dim]",
                    )

        # Search rules
        if hasattr(app, 'rules'):
            for rule in app.rules:
                name = rule.get('name', '')
                description = rule.get('description', '')
                active = rule.get('active', False)

                search_text = f"rule {name} {description}"
                if match := matcher.match(search_text):
                    status = Icons.SUCCESS if active else Icons.SPACE
                    yield Hit(
                        match,
                        matcher.highlight(f"{status} Rule: {name}"),
                        self._jump_to_item("rules", name),
                        help=f"[dim]{description}[/dim]",
                    )

    def _jump_to_item(self, view_name: str, item_name: str) -> Callable[[], None]:
        """Create callback to jump to specific item in a view.

        Args:
            view_name: Target view name
            item_name: Item name to select

        Returns:
            Callback function
        """
        def callback() -> None:
            app = self.app_instance

            # Switch to the view
            app.current_view = view_name

            # Find and select the item in the DataTable
            # This will be implemented by adding a helper method to CtxTUI
            if hasattr(app, 'select_item_by_name'):
                app.select_item_by_name(item_name)

            app.notify(f"Jumped to {item_name} in {view_name}", severity="information")

        return callback

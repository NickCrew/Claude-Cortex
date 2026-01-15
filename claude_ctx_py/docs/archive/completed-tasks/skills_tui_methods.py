"""
Skills View Methods for TUI
These methods should be added to the AgentTUI class in tui.py
"""

def load_skills(self) -> None:
    """Load skills from the system."""
    try:
        skills = []
        claude_dir = _resolve_claude_dir()
        skills_dir = claude_dir / "skills"

        if not skills_dir.is_dir():
            self.state.status_message = "No skills directory found"
            self.state.skills = []
            return

        # Load metrics
        try:
            metrics = get_all_metrics()
        except Exception:
            metrics = {}

        # Iterate through skill directories
        for skill_path in sorted(skills_dir.iterdir()):
            if not skill_path.is_dir():
                continue

            skill_file = skill_path / "SKILL.md"
            if not skill_file.is_file():
                continue

            skill_name = skill_path.name

            try:
                # Read skill file
                content = skill_file.read_text(encoding="utf-8")
                front_matter = _extract_front_matter(content)

                if front_matter:
                    lines = front_matter.strip().splitlines()
                    tokens = _tokenize_front_matter(lines)

                    description = _extract_scalar_from_paths(
                        tokens, (("description",),)
                    ) or "No description"

                    category = _extract_scalar_from_paths(
                        tokens, (("category",),)
                    ) or "general"
                else:
                    description = "No description"
                    category = "general"

                # Get metrics if available
                skill_metrics = metrics.get(skill_name, {})
                uses = skill_metrics.get("activation_count", 0)
                last_used = skill_metrics.get("last_activated")
                tokens_saved = skill_metrics.get("total_tokens_saved", 0)
                success_rate = skill_metrics.get("success_rate", 0.0)

                skills.append(
                    SkillInfo(
                        name=skill_name,
                        description=description,
                        category=category,
                        uses=uses,
                        last_used=last_used,
                        tokens_saved=tokens_saved,
                        success_rate=success_rate,
                        is_community=False,
                        installed=True,
                    )
                )

            except Exception:
                # Skip skills that fail to parse
                continue

        # Sort by uses (most used first), then by name
        skills.sort(key=lambda s: (-s.uses, s.name.lower()))

        self.state.skills = skills
        self.state.status_message = f"Loaded {len(skills)} skills"

    except Exception as e:
        self.state.status_message = f"Error loading skills: {e}"
        self.state.skills = []


def get_filtered_skills(self) -> List[SkillInfo]:
    """Get skills filtered by current filter text."""
    if not self.state.filter_text:
        return self.state.skills

    filter_lower = self.state.filter_text.lower()
    return [
        skill
        for skill in self.state.skills
        if filter_lower in skill.name.lower()
        or filter_lower in skill.description.lower()
        or filter_lower in skill.category.lower()
    ]


def create_skills_table(self) -> Table:
    """Create the skills list table."""
    table = Table(
        show_header=True,
        header_style="bold magenta",
        show_lines=False,
        expand=True,
    )

    table.add_column("", width=2, no_wrap=True)  # Selection indicator
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Category", width=15, no_wrap=True)
    table.add_column("Uses", width=8, no_wrap=True, justify="right")
    table.add_column("Last Used", width=20, no_wrap=True)
    table.add_column("Tokens Saved", width=15, no_wrap=True, justify="right")

    filtered_skills = self.get_filtered_skills()

    if not filtered_skills:
        table.add_row("", "No skills found", "", "", "", "")
        return table

    for idx, skill in enumerate(filtered_skills):
        # Determine if this row is selected
        is_selected = idx == self.state.selected_index

        # Selection indicator
        indicator = ">" if is_selected else ""

        # Format last used date
        if skill.last_used:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(skill.last_used.replace("Z", "+00:00"))
                last_used_str = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, AttributeError):
                last_used_str = skill.last_used[:16]
        else:
            last_used_str = "Never"

        # Format tokens saved
        tokens_str = f"{skill.tokens_saved:,}" if skill.tokens_saved > 0 else "-"

        # Row style
        row_style = "reverse" if is_selected else None

        table.add_row(
            indicator,
            skill.name,
            skill.category,
            str(skill.uses),
            last_used_str,
            tokens_str,
            style=row_style,
        )

    return table


def create_skills_details_panel(self) -> Optional[Panel]:
    """Create the details panel for the selected skill."""
    if self.state.skills_view_mode != "details":
        return None

    filtered_skills = self.get_filtered_skills()
    if not filtered_skills or self.state.selected_index >= len(filtered_skills):
        return None

    skill = filtered_skills[self.state.selected_index]

    details = Text()
    details.append("Skill: ", style="bold")
    details.append(f"{skill.name}\n\n")

    details.append("Description:\n", style="bold")
    details.append(f"  {skill.description}\n\n")

    details.append("Category: ", style="bold")
    details.append(f"{skill.category}\n")

    details.append("Statistics:\n", style="bold")
    details.append(f"  Uses: {skill.uses}\n")
    details.append(f"  Tokens Saved: {skill.tokens_saved:,}\n")
    details.append(f"  Success Rate: {skill.success_rate:.1%}\n")
    details.append(f"  Last Used: {skill.last_used or 'Never'}\n")

    if skill.is_community:
        details.append("\nCommunity Info:\n", style="bold")
        details.append(f"  Author: {skill.author or 'Unknown'}\n")
        if skill.rating:
            stars = "★" * int(skill.rating) + "☆" * (5 - int(skill.rating))
            details.append(f"  Rating: {stars} ({skill.rating:.1f}/5)\n")
        details.append(f"  Installed: {'Yes' if skill.installed else 'No'}\n")

    return Panel(details, title="Skill Details", border_style="cyan")


def create_skills_metrics_panel(self) -> Panel:
    """Create metrics panel for selected skill."""
    filtered_skills = self.get_filtered_skills()
    if not filtered_skills or self.state.selected_index >= len(filtered_skills):
        return Panel(
            Text("No skill selected", style="yellow"),
            title="Metrics",
            border_style="yellow"
        )

    skill = filtered_skills[self.state.selected_index]

    # Get detailed metrics
    try:
        skill_metrics = get_skill_metrics(skill.name)
        if not skill_metrics:
            return Panel(
                Text(f"No metrics available for {skill.name}", style="yellow"),
                title="Metrics",
                border_style="yellow"
            )

        metrics_text = Text()
        metrics_text.append(f"Skill: {skill.name}\n\n", style="bold cyan")

        metrics_text.append("Usage Statistics:\n", style="bold")
        metrics_text.append(f"  Activation Count: {skill_metrics.get('activation_count', 0)}\n")
        metrics_text.append(f"  Total Tokens Saved: {skill_metrics.get('total_tokens_saved', 0):,}\n")
        metrics_text.append(f"  Average Tokens: {skill_metrics.get('avg_tokens', 0):,}\n")
        metrics_text.append(f"  Success Rate: {skill_metrics.get('success_rate', 0):.1%}\n\n")

        last_activated = skill_metrics.get("last_activated")
        if last_activated:
            metrics_text.append("Last Activation:\n", style="bold")
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_activated.replace("Z", "+00:00"))
                metrics_text.append(f"  {dt.strftime('%Y-%m-%d %H:%M:%S')}\n")
            except (ValueError, AttributeError):
                metrics_text.append(f"  {last_activated}\n")

        return Panel(metrics_text, title="Detailed Metrics", border_style="green")

    except Exception as e:
        return Panel(
            Text(f"Error loading metrics: {e}", style="red"),
            title="Metrics Error",
            border_style="red"
        )


def create_community_skills_table(self) -> Table:
    """Create community skills browser table."""
    table = Table(
        show_header=True,
        header_style="bold magenta",
        show_lines=False,
        expand=True,
    )

    table.add_column("", width=2, no_wrap=True)  # Selection indicator
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Author", width=20, no_wrap=True)
    table.add_column("Rating", width=12, no_wrap=True)
    table.add_column("Status", width=12, no_wrap=True)
    table.add_column("Description", width=40)

    # This would need to fetch community skills
    # For now, show placeholder
    table.add_row("", "Loading...", "", "", "", "Community skills browser coming soon")

    return table


def validate_selected_skill(self) -> None:
    """Validate the selected skill."""
    filtered_skills = self.get_filtered_skills()
    if not filtered_skills or self.state.selected_index >= len(filtered_skills):
        self.state.status_message = "No skill selected"
        return

    skill = filtered_skills[self.state.selected_index]

    try:
        # Call validation
        exit_code, message = skill_validate(skill.name)

        # Clean ANSI codes
        import re
        clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)

        # Show first line in status
        self.state.status_message = clean_message.split("\n")[0]

        # If validation failed, could show full results in a panel
        # For now, just update status message

    except Exception as e:
        self.state.status_message = f"Validation error: {e}"


def toggle_skills_view_mode(self, mode: str) -> None:
    """Switch between different skills view modes."""
    if mode in ["local", "community", "details", "metrics", "validate"]:
        self.state.skills_view_mode = mode
        self.state.status_message = f"Switched to {mode} view"
    else:
        self.state.status_message = f"Unknown view mode: {mode}"


def handle_skills_key(self, key: str) -> bool:
    """Handle key presses specific to skills view.

    Returns True if key was handled, False otherwise.
    """
    if key == "v":
        self.validate_selected_skill()
        return True
    elif key == "m":
        if self.state.skills_view_mode == "metrics":
            self.toggle_skills_view_mode("local")
        else:
            self.toggle_skills_view_mode("metrics")
        return True
    elif key == "c":
        if self.state.skills_view_mode == "community":
            self.toggle_skills_view_mode("local")
        else:
            self.toggle_skills_view_mode("community")
            self.state.status_message = "Community skills browser not yet implemented"
        return True
    elif key == "\r" or key == "\n":
        # Toggle details mode
        if self.state.skills_view_mode == "details":
            self.toggle_skills_view_mode("local")
            self.state.show_details = False
        else:
            self.toggle_skills_view_mode("details")
            self.state.show_details = True
        return True

    return False  # Key not handled

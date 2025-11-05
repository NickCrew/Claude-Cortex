"""Workflow and Orchestration view methods for TUI - to be integrated."""

    def load_workflows(self) -> List[WorkflowInfo]:
        """Load workflows from the workflows directory."""
        workflows: List[WorkflowInfo] = []
        try:
            claude_dir = _resolve_claude_dir()
            workflows_dir = claude_dir / "workflows"
            tasks_dir = claude_dir / "tasks" / "current"

            # Load active workflow status if exists
            active_workflow_file = tasks_dir / "active_workflow"
            active_workflow = None
            if active_workflow_file.is_file():
                active_workflow = active_workflow_file.read_text(encoding="utf-8").strip()

            if workflows_dir.is_dir():
                for workflow_file in sorted(workflows_dir.glob("*.yaml")):
                    if workflow_file.stem == "README":
                        continue

                    try:
                        content = workflow_file.read_text(encoding="utf-8")
                        workflow_data = yaml.safe_load(content)

                        name = workflow_data.get("name", workflow_file.stem)
                        description = workflow_data.get("description", "")
                        steps = [step.get("name", "") for step in workflow_data.get("steps", [])]

                        # Determine status
                        status = "pending"
                        progress = 0
                        started = None
                        current_step = None

                        if active_workflow == workflow_file.stem:
                            status_file = tasks_dir / "workflow_status"
                            if status_file.is_file():
                                status = status_file.read_text(encoding="utf-8").strip()

                            started_file = tasks_dir / "workflow_started"
                            if started_file.is_file():
                                started = float(started_file.read_text(encoding="utf-8").strip())

                            current_step_file = tasks_dir / "current_step"
                            if current_step_file.is_file():
                                current_step = current_step_file.read_text(encoding="utf-8").strip()

                            # Calculate progress based on current step
                            if current_step and steps:
                                try:
                                    step_index = steps.index(current_step)
                                    progress = int((step_index / len(steps)) * 100)
                                except ValueError:
                                    progress = 0

                        workflows.append(WorkflowInfo(
                            name=name,
                            description=description,
                            status=status,
                            progress=progress,
                            started=started,
                            steps=steps,
                            current_step=current_step,
                            file_path=workflow_file,
                        ))

                    except Exception:
                        # Skip malformed workflows
                        continue

        except Exception as e:
            self.state.status_message = f"Error loading workflows: {e}"

        return workflows

    def create_workflows_table(self) -> Table:
        """Create the workflows list table."""
        table = Table(
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
        )

        table.add_column("", width=2, no_wrap=True)  # Selection indicator
        table.add_column("Name", style="cyan", no_wrap=True, width=30)
        table.add_column("Status", width=12, no_wrap=True)
        table.add_column("Progress", width=12, no_wrap=True)
        table.add_column("Started", width=20, no_wrap=True)
        table.add_column("Description", width=40)

        workflows = self.load_workflows()

        if not workflows:
            table.add_row("", "No workflows found", "", "", "", "")
            return table

        for idx, workflow in enumerate(workflows):
            is_selected = idx == self.state.selected_index

            # Selection indicator
            indicator = ">" if is_selected else ""

            # Status styling
            status_styles = {
                "pending": "yellow",
                "running": "bold green",
                "paused": "cyan",
                "complete": "bold blue",
                "error": "bold red",
            }
            status_text = Text(workflow.status.title(), style=status_styles.get(workflow.status, "white"))

            # Progress bar
            progress_text = ""
            if workflow.status in ("running", "paused", "complete"):
                bar_width = 10
                filled = int((workflow.progress / 100) * bar_width)
                progress_text = f"[{'█' * filled}{'░' * (bar_width - filled)}] {workflow.progress}%"
            else:
                progress_text = "-"

            # Started time
            started_text = "-"
            if workflow.started:
                elapsed = int(time.time() - workflow.started)
                hours = elapsed // 3600
                minutes = (elapsed % 3600) // 60
                started_text = f"{hours}h {minutes}m ago"

            # Row style
            row_style = "reverse" if is_selected else None

            table.add_row(
                indicator,
                workflow.name,
                status_text,
                progress_text,
                started_text,
                workflow.description[:40],
                style=row_style,
            )

        return table

    def create_workflow_details_panel(self) -> Optional[Panel]:
        """Create the details panel for the selected workflow."""
        if not self.state.show_details:
            return None

        workflows = self.load_workflows()
        if not workflows or self.state.selected_index >= len(workflows):
            return None

        workflow = workflows[self.state.selected_index]

        details = Text()
        details.append(f"Workflow: ", style="bold")
        details.append(f"{workflow.name}\n\n")

        details.append(f"Description: ", style="bold")
        details.append(f"{workflow.description}\n\n")

        details.append(f"Status: ", style="bold")
        status_styles = {
            "pending": "yellow",
            "running": "bold green",
            "paused": "cyan",
            "complete": "bold blue",
            "error": "bold red",
        }
        details.append(f"{workflow.status}\n\n", style=status_styles.get(workflow.status, "white"))

        if workflow.started:
            elapsed = int(time.time() - workflow.started)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            details.append(f"Started: ", style="bold")
            details.append(f"{hours}h {minutes}m ago\n\n")

        details.append(f"Progress: ", style="bold")
        details.append(f"{workflow.progress}%\n\n")

        if workflow.steps:
            details.append(f"Steps:\n", style="bold")
            for i, step in enumerate(workflow.steps):
                if workflow.current_step == step:
                    details.append(f"  → {step} ", style="bold green")
                    details.append("(current)\n")
                elif workflow.current_step and workflow.steps.index(workflow.current_step) > i:
                    details.append(f"  ✓ {step}\n", style="dim green")
                else:
                    details.append(f"  ○ {step}\n", style="dim")

        return Panel(details, title="Workflow Details", border_style="cyan")

    def load_agent_tasks(self) -> List[AgentTask]:
        """Load active agent tasks for orchestration view."""
        tasks: List[AgentTask] = []
        try:
            claude_dir = _resolve_claude_dir()
            tasks_dir = claude_dir / "tasks" / "current"

            # Check for active tasks file
            active_tasks_file = tasks_dir / "active_agents.json"
            if active_tasks_file.is_file():
                import json
                task_data = json.loads(active_tasks_file.read_text(encoding="utf-8"))

                for task_id, task_info in task_data.items():
                    tasks.append(AgentTask(
                        agent_id=task_id,
                        agent_name=task_info.get("name", task_id),
                        workstream=task_info.get("workstream", "primary"),
                        status=task_info.get("status", "pending"),
                        progress=task_info.get("progress", 0),
                        started=task_info.get("started"),
                        completed=task_info.get("completed"),
                    ))
        except Exception:
            # No active tasks or error reading
            pass

        return tasks

    def create_orchestrate_view(self) -> Layout:
        """Create the orchestration dashboard view."""
        layout = Layout()
        layout.split_column(
            Layout(name="workstreams", size=15),
            Layout(name="agents"),
            Layout(name="metrics", size=8),
        )

        # Workstreams panel
        workstreams_content = Text()
        workstreams_content.append("Orchestration Dashboard\n", style="bold cyan")
        workstreams_content.append("━" * 60 + "\n\n", style="cyan")

        workstreams_content.append("Workstream Layout:\n\n", style="bold yellow")
        workstreams_content.append("Primary               Quality (‖)\n", style="bold")
        workstreams_content.append("Implementation        • Code Review\n", style="dim")
        workstreams_content.append("████████████ 90%      • Tests\n\n", style="green")

        layout["workstreams"].update(Panel(workstreams_content, title="Workstreams"))

        # Active agents table
        agents_table = Table(
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
        )

        agents_table.add_column("Agent", style="cyan", width=20)
        agents_table.add_column("Workstream", width=15)
        agents_table.add_column("Status", width=12)
        agents_table.add_column("Progress", width=30)

        tasks = self.load_agent_tasks()

        if not tasks:
            # Show example data if no active tasks
            agents_table.add_row(
                "[Agent-1] Implementation",
                "primary",
                Text("Running", style="bold green"),
                "[██████████░░░░░░░░░░] 75%",
            )
            agents_table.add_row(
                "[Agent-2] Code Review",
                "quality",
                Text("Complete", style="bold blue"),
                "[████████████████████] 100%",
            )
            agents_table.add_row(
                "[Agent-3] Test Automation",
                "quality",
                Text("Running", style="bold green"),
                "[████████████░░░░░░░░] 60%",
            )
        else:
            for task in tasks:
                status_styles = {
                    "pending": "yellow",
                    "running": "bold green",
                    "complete": "bold blue",
                    "error": "bold red",
                }

                status_text = Text(task.status.title(), style=status_styles.get(task.status, "white"))

                # Progress bar
                bar_width = 20
                filled = int((task.progress / 100) * bar_width)
                progress_bar = f"[{'█' * filled}{'░' * (bar_width - filled)}] {task.progress}%"

                agents_table.add_row(
                    f"[{task.agent_id}] {task.agent_name}",
                    task.workstream,
                    status_text,
                    progress_bar,
                )

        layout["agents"].update(Panel(agents_table, title="Active Agents"))

        # Metrics panel
        metrics_content = Text()
        metrics_content.append("Metrics:\n", style="bold yellow")

        # Calculate metrics
        if tasks:
            total_progress = sum(t.progress for t in tasks) // len(tasks) if tasks else 0
            running_count = sum(1 for t in tasks if t.status == "running")
            complete_count = sum(1 for t in tasks if t.status == "complete")
            parallel_efficiency = int((running_count / len(tasks)) * 100) if tasks else 0

            metrics_content.append(f"  Parallel Efficiency: ", style="bold")
            metrics_content.append(f"{parallel_efficiency}%\n", style="green")

            metrics_content.append(f"  Overall Progress: ", style="bold")
            metrics_content.append(f"{total_progress}%\n", style="cyan")

            metrics_content.append(f"  Active Agents: ", style="bold")
            metrics_content.append(f"{running_count}/{len(tasks)}\n", style="yellow")

            metrics_content.append(f"  Completed: ", style="bold")
            metrics_content.append(f"{complete_count}/{len(tasks)}\n", style="blue")

            # Estimate completion time
            if running_count > 0 and total_progress > 0:
                estimated_minutes = int((100 - total_progress) * 0.5)  # Rough estimate
                metrics_content.append(f"  Estimated Completion: ", style="bold")
                metrics_content.append(f"{estimated_minutes}m\n", style="magenta")
        else:
            metrics_content.append("  Parallel Efficiency: ", style="bold")
            metrics_content.append("87%\n", style="green")

            metrics_content.append(f"  Overall Progress: ", style="bold")
            metrics_content.append(f"78%\n", style="cyan")

            metrics_content.append(f"  Estimated Completion: ", style="bold")
            metrics_content.append(f"2m 30s\n", style="magenta")

        layout["metrics"].update(Panel(metrics_content, title="Orchestration Metrics"))

        return layout

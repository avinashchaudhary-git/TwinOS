import re


class MockLLM:
    """Deterministic offline LLM that analyzes assembled context and synthesizes grounded answers with citations."""

    def generate(self, prompt: str, context: str, question: str) -> str:
        q = question.lower()

        # Handle out of scope questions
        out_of_scope_keywords = [
            "weather",
            "capital of",
            "recipe",
            "write a poem",
            "movie",
            "sports",
            "joke",
        ]
        if any(w in q for w in out_of_scope_keywords):
            return "I cannot answer this question. TwinOS Assistant only answers queries relating to organizational status, project risk, tasks, deadlines, and engineering activity."

        # Risk queries: "which projects are at risk?", "project risk", etc.
        if "at risk" in q or "risk" in q or "slip" in q or "delay" in q:
            # Extract projects mentioned in context
            project_matches = re.findall(
                r"\[source:\s*project:([^\]]+)\]\s*Project:\s*([^\n\.]+)", context
            )

            # Build grounded answer from context
            lines = [
                "Based on the organizational knowledge graph and predictive risk models, the following projects are at risk:"
            ]

            # Check for Cloud Migration or Telemetry pipeline or generic projects in context
            found = False
            for line in context.split("\n"):
                if "at_risk" in line or "high" in line or "critical" in line:
                    lines.append(f"- {line.strip()}")
                    found = True

            if not found and project_matches:
                for p_id, p_name in project_matches[:3]:
                    lines.append(
                        f"- Project '{p_name}' [source: project:{p_id}] exhibits deadline slippage and task blockers."
                    )
            elif not found:
                lines.append(
                    "- Several active deliverables show elevated risk due to overdue tasks and blocked dependencies."
                )

            lines.append(
                "\nMitigation recommendation: Review task distribution and unblock critical path dependencies."
            )
            return "\n".join(lines)

        # Workload / who is working on what queries
        if "workload" in q or "who is working" in q or "assignee" in q or "overload" in q:
            lines = ["Based on the current knowledge graph task assignments:"]
            emp_matches = re.findall(r"\[source:\s*employee:([^\]]+)\]\s*([^\n]+)", context)
            for e_id, e_info in emp_matches[:4]:
                lines.append(f"- {e_info} [source: employee:{e_id}]")
            if not emp_matches:
                lines.append(
                    "Team members are actively tracking assigned tasks across active boards."
                )
            return "\n".join(lines)

        # Tasks / overdue / blockers
        if "task" in q or "overdue" in q or "blocked" in q or "todo" in q:
            lines = ["Current task status overview from the knowledge graph:"]
            task_matches = re.findall(r"\[source:\s*task:([^\]]+)\]\s*([^\n]+)", context)
            for t_id, t_info in task_matches[:5]:
                lines.append(f"- {t_info} [source: task:{t_id}]")
            if not task_matches:
                lines.append("I don't have data on that in the organizational knowledge graph.")
            return "\n".join(lines)

        # Commits / git / repositories
        if "commit" in q or "repo" in q or "code" in q or "github" in q:
            lines = ["Recent technical activity recorded across connected repositories:"]
            commit_matches = re.findall(r"\[source:\s*commit:([^\]]+)\]\s*([^\n]+)", context)
            for c_id, c_info in commit_matches[:4]:
                lines.append(f"- {c_info} [source: commit:{c_id}]")
            return "\n".join(lines)

        # General context-derived fallback
        sources = re.findall(r"\[source:\s*([a-zA-Z_]+):([^\]]+)\]", context)
        if sources:
            cited = ", ".join([f"[source: {stype}:{sid}]" for stype, sid in sources[:3]])
            return f"According to organizational records in the knowledge graph ({cited}), relevant activity is actively tracked for this query."

        return "I don't have data on that in the organizational knowledge graph."

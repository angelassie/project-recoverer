"""
Recovery Main Program - recoverer
Coordinates all modules to provide complete recovery workflow
"""
import sys
import os
import pathlib
import json
from datetime import datetime

# Add core to path
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from analyzer import ErrorAnalyzer
from context_builder import ContextBuilder
from memory_sync import MemorySync


class ProjectRecoverer:
    """Main class for project recovery assistant"""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.analyzer = ErrorAnalyzer()
        self.context_builder = ContextBuilder(project_root)
        self.memory_sync = MemorySync(project_root)

    def run_recovery(self, error_text: str = "") -> dict:
        """
        Execute the complete recovery workflow.

        Args:
            error_text: Error message before interruption (can be empty)

        Returns:
            Recovery report dictionary
        """
        output_lines = []
        output_lines.append("=" * 50)
        output_lines.append("Project Recovery Assistant Started")
        output_lines.append("=" * 50)

        # Step 1: Load memory
        output_lines.append("")
        output_lines.append("[1/5] Loading memory...")
        memory = {
            "index": self.context_builder.load_memory_index()["content"],
            "status": self.context_builder.load_memory_status()["content"],
            "conventions": self.context_builder.load_memory_conventions()["content"],
            "logs": self.context_builder.load_memory_logs()["content"],
        }

        # Step 2: Analyze errors
        output_lines.append("[2/5] Analyzing error messages...")
        errors = []
        error_summary = "No error messages"
        if error_text and error_text.strip():
            errors = self.analyzer.analyze(error_text)
            classification = self.analyzer.classify(errors)
            error_summary = classification["summary"]
            output_lines.append("  Found %d errors" % classification["total"])
            for e in errors:
                safe_raw = "".join(c for c in e.raw_text if ord(c) < 128 or c in "\n\r\t")
                output_lines.append("  [%s] %s: %s" % (e.severity, e.error_type, safe_raw[:80]))
        else:
            output_lines.append("  No error messages, only recovering context")

        # Step 3: Reconstruct context
        output_lines.append("[3/5] Reconstructing project context...")
        project_files = self.context_builder.scan_project_files()
        output_lines.append("  Project file count: %d" % len(project_files))

        # Step 4: Find incomplete tasks
        output_lines.append("[4/5] Finding incomplete tasks...")
        incomplete_tasks = self.context_builder.find_incomplete_tasks()
        undone = [t for t in incomplete_tasks if not t["done"]]
        done = [t for t in incomplete_tasks if t["done"]]
        output_lines.append("  Completed: %d, Pending: %d" % (len(done), len(undone)))
        for t in undone:
            output_lines.append("  [Pending] %s" % t["text"])

        # Step 5: Generate recovery suggestions
        output_lines.append("[5/5] Generating recovery suggestions...")
        next_action = self.context_builder.get_next_action()
        output_lines.append("  Next step: %s" % next_action)

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "error_summary": error_summary,
            "errors_found": len(errors),
            "memory_loaded": True,
            "project_files_count": len(project_files),
            "tasks_done": len(done),
            "tasks_pending": len(undone),
            "next_action": next_action,
            "undone_tasks": undone,
            "project_files": project_files,
            "output_log": output_lines,
        }

        # Update memory
        self.memory_sync.mark_recovery_complete(
            error_summary=error_summary,
            recovered_tasks=len(done),
            next_action=next_action,
        )

        # Print summary
        output_lines.append("")
        output_lines.append("=" * 50)
        output_lines.append("Recovery Report")
        output_lines.append("=" * 50)
        output_lines.append("Error Summary: %s" % error_summary)
        output_lines.append("Memory Status: %s" % ("Loaded" if report["memory_loaded"] else "Not Found"))
        output_lines.append("Project Files: %d" % report["project_files_count"])
        output_lines.append("Completed Tasks: %d" % report["tasks_done"])
        output_lines.append("Pending Tasks: %d" % report["tasks_pending"])
        output_lines.append("Next Action: %s" % next_action)
        output_lines.append("=" * 50)

        # Print to console (safely)
        for line in output_lines:
            safe = "".join(c for c in line if ord(c) < 128 or c in "\n\r\t")
            print(safe)

        return report


def main():
    """Command-line entry point"""
    project_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    error_text = sys.argv[2] if len(sys.argv) > 2 else ""

    recoverer = ProjectRecoverer(project_root)
    report = recoverer.run_recovery(error_text)

    # Save report to outputs/
    output_dir = pathlib.Path(project_root) / "outputs"
    output_dir.mkdir(exist_ok=True)
    report_file = output_dir / ("recovery_report_%s.json" % datetime.now().strftime("%Y%m%d_%H%M%S"))
    # Convert non-serializable objects
    serializable_report = {}
    for k, v in report.items():
        if isinstance(v, list):
            serializable_report[k] = v
        elif isinstance(v, (str, int, float, bool, type(None))):
            serializable_report[k] = v
        else:
            serializable_report[k] = str(v)
    report_file.write_text(json.dumps(serializable_report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nReport saved to: %s" % report_file)


if __name__ == "__main__":
    main()

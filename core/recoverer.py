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
from memory_init import init_memory


class ProjectRecoverer:
    """Main class for project recovery assistant"""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.analyzer = ErrorAnalyzer()
        self.context_builder = ContextBuilder(project_root)
        self.memory_sync = MemorySync(project_root)

    def init_project_memory(self, project_name: str = "", tech_stack: str = "") -> dict:
        '''
        Initialize memory files for a new project.
        This is called automatically when a project doesn't have memory files yet.
        '''
        memory_dir = pathlib.Path(self.project_root) / "记忆体"
        if memory_dir.exists() and any(memory_dir.iterdir()):
            return {"skipped": True, "reason": "Memory already exists"}

        print("\n" + "=" * 50)
        print("Initializing project memory...")
        print("=" * 50)

        result = init_memory(self.project_root, project_name, tech_stack)

        if result["success"]:
            print("Memory initialized successfully!")
            print("Created files: %s" % ", ".join(result["files_created"]))
        else:
            print("Memory initialization failed:")
            for err in result["errors"]:
                print("  - %s" % err)

        return result

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

        # Step 0: Check and initialize memory if needed
        output_lines.append("")
        output_lines.append("[0/6] Checking memory files...")
        memory_dir = pathlib.Path(self.project_root) / "记忆体"
        if not memory_dir.exists() or not any(memory_dir.iterdir()):
            output_lines.append("  Memory not found, initializing...")
            mem_result = self.init_project_memory()
            if mem_result.get("skipped"):
                output_lines.append("  Memory already exists, skipping.")
            elif not mem_result["success"]:
                output_lines.append("  WARNING: Memory initialization failed!")
                for err in mem_result["errors"]:
                    output_lines.append("    - %s" % err)
        else:
            output_lines.append("  Memory files found.")

        # Step 1: Load memory
        output_lines.append("")
        output_lines.append("[1/6] Loading memory...")
        memory = {
            "index": self.context_builder.load_memory_index()["content"],
            "status": self.context_builder.load_memory_status()["content"],
            "conventions": self.context_builder.load_memory_conventions()["content"],
            "logs": self.context_builder.load_memory_logs()["content"],
        }

        # Step 2: Analyze errors
        output_lines.append("[2/6] Analyzing error messages...")
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
        output_lines.append("[3/6] Reconstructing project context...")
        project_files = self.context_builder.scan_project_files()
        output_lines.append("  Project file count: %d" % len(project_files))

        # Step 4: Find incomplete tasks
        output_lines.append("[4/6] Finding incomplete tasks...")
        incomplete_tasks = self.context_builder.find_incomplete_tasks()
        undone = [t for t in incomplete_tasks if not t["done"]]
        done = [t for t in incomplete_tasks if t["done"]]
        output_lines.append("  Completed: %d, Pending: %d" % (len(done), len(undone)))
        for t in undone:
            output_lines.append("  [Pending] %s" % t["text"])

        # Step 5: Generate recovery suggestions
        output_lines.append("[5/6] Generating recovery suggestions...")
        next_action = self.context_builder.get_next_action()
        output_lines.append("  Next step: %s" % next_action)

        # Step 6: Save recovery log
        output_lines.append("[6/6] Saving recovery log...")

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
    init_flag = "--init-memory" in sys.argv

    recoverer = ProjectRecoverer(project_root)

    if init_flag:
        print("\nInitializing memory for project: %s" % project_root)
        result = recoverer.init_project_memory()
        if result.get("skipped"):
            print("Memory already exists, skipped.")
        elif result["success"]:
            print("Memory initialized successfully!")
        else:
            print("Initialization failed:")
            for err in result["errors"]:
                print("  - %s" % err)
        return

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

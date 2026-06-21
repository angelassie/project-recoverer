import pathlib

code = '''\"\"\"
Memory Synchronization Module - memory_sync
Automatically updates memory status in both .md and .json formats.
Adds deduplication for recovery logs to prevent duplicate entries.
\"\"\"
import pathlib
import json
import hashlib
from datetime import datetime


class MemorySync:
    def __init__(self, project_root: str):
        self.project_root = pathlib.Path(project_root)
        self.memory_dir = self.project_root / \"\u8bb0\u5fc6\u4f53\"

    def _compute_hash(self, text: str) -> str:
        return hashlib.md5(text.encode(\"utf-8\")).hexdigest()[:12]

    def _is_duplicate(self, log_file, entry: str) -> bool:
        if not log_file.exists():
            return False
        content = log_file.read_text(encoding=\"utf-8\")
        return entry.strip() in content

    def append_log(self, timestamp: str, title: str, details: list):
        log_file = self.memory_dir / \"\u5bf9\u8bdd\u8bb0\u5f55.md\"
        if not log_file.exists():
            log_file.write_text(\"# Project Memory Dialogue Logs\\n\\n\", encoding=\"utf-8\")

        entry_lines = [f\"### {timestamp} - {title}\"]
        for d in details:
            entry_lines.append(f\"- {d}\")
        entry_text = \"\\n\" + \"\\n\".join(entry_lines) + \"\\n\"

        if self._is_duplicate(log_file, entry_text):
            return

        content = log_file.read_text(encoding=\"utf-8\")
        footer = \"*Continue updating this file*\"
        if footer in content:
            content = content.replace(footer, entry_text + \"\\n\" + footer)
        else:
            content += entry_text

        log_file.write_text(content, encoding=\"utf-8\")

    def update_status(self, completed_tasks=None, in_progress_tasks=None, next_steps=None):
        status_file = self.memory_dir / \"\u72b6\u6001.md\"
        if not status_file.exists():
            return

        content = status_file.read_text(encoding=\"utf-8\")

        if completed_tasks:
            for task in completed_tasks:
                marker = \"- [ ] \" + task
                if marker in content:
                    content = content.replace(marker, \"- [x] \" + task)

        if in_progress_tasks:
            for task in in_progress_tasks:
                marker = \"- [ ] \" + task
                if marker in content:
                    content = content.replace(marker, \"- [>] \" + task)

        if next_steps:
            lines = content.split(\"\\n\")
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if line.strip() == \"## Next Steps\":
                    for step in next_steps:
                        new_lines.append(f\"- [ ] {step}\")
            content = \"\\n\".join(new_lines)

        now_str = datetime.now().strftime(\"%Y-%m-%d\")
        import re
        pattern = r\"\\*Last Updated: [^\\*]*\\*\"
        if re.search(pattern, content):
            content = re.sub(pattern, f\"*Last Updated: {now_str}*\", content)
        else:
            content += f\"\\n\\n*Last Updated: {now_str}*\\n\"

        status_file.write_text(content, encoding=\"utf-8\")

    def mark_recovery_complete(self, error_summary: str, recovered_tasks: int, next_action: str):
        ts = datetime.now().strftime(\"%H:%M\")
        self.append_log(
            timestamp=f\"{datetime.now().strftime(chr(37)+\"Y-\"+chr(37)+\"m-\"+chr(37)+\"d\")} - {ts}\",
            title=\"Recovery Execution Complete\",
            details=[
                f\"Error Summary: {error_summary}\",
                f\"Recovered Tasks: {recovered_tasks}\",
                f\"Next Action: {next_action}\",
            ],
        )
        self.update_status(next_steps=[next_action])

        json_record = {{
            \"timestamp\": datetime.now().isoformat(),
            \"error_summary\": error_summary,
            \"recovered_tasks\": recovered_tasks,
            \"next_action\": next_action,
        }}
        json_file = self.memory_dir / \"\u6062\u590d\u8bb0\u5f55.json\"
        records = []
        if json_file.exists():
            try:
                existing = json_file.read_text(encoding=\"utf-8\")
                records = json.loads(existing)
                if not isinstance(records, list):
                    records = [records]
            except (json.JSONDecodeError, ValueError):
                records = []

        is_dup = False
        for r in records[-20:]:
            if r.get(\"error_summary\") == error_summary and r.get(\"next_action\") == next_action:
                is_dup = True
                break

        if not is_dup:
            records.append(json_record)
            json_file.write_text(
                json.dumps(records, ensure_ascii=False, indent=2),
                encoding=\"utf-8\"
            )
'''

target = pathlib.Path(r\"F:\\codex\\Project002_CodexMonitor\\core\\memory_sync.py\")
target.write_text(code, encoding=\"utf-8\")
print(\"Done\")

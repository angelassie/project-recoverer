"""
Context Reconstruction Module - context_builder
Recovers lost information from memory and project files
"""
import json
import pathlib
from datetime import datetime
from typing import Optional


class ContextBuilder:
    def __init__(self, project_root: str):
        self.project_root = pathlib.Path(project_root)
        self.memory_dir = self.project_root / "???"
        self.core_dir = self.project_root / "core"

    def load_memory_index(self) -> dict:
        idx = self.memory_dir / "索引.md"
        if idx.exists():
            return {"source": "index", "content": idx.read_text(encoding="utf-8")}
        return {"source": "index", "content": ""}

    def load_memory_status(self) -> dict:
        st = self.memory_dir / "状态.md"
        if st.exists():
            return {"source": "status", "content": st.read_text(encoding="utf-8")}
        return {"source": "status", "content": ""}

    def load_memory_conventions(self) -> dict:
        cn = self.memory_dir / "约定.md"
        if cn.exists():
            return {"source": "conventions", "content": cn.read_text(encoding="utf-8")}
        return {"source": "conventions", "content": ""}

    def load_memory_logs(self) -> dict:
        lg = self.memory_dir / "对话记录.md"
        if lg.exists():
            return {"source": "logs", "content": lg.read_text(encoding="utf-8")}
        return {"source": "logs", "content": ""}

    def scan_project_files(self, extensions=None) -> list:
        if extensions is None:
            extensions = [".py", ".md", ".json", ".txt", ".cfg", ".ini"]
        files = []
        for ext in extensions:
            for f in self.project_root.rglob(f"*{ext}"):
                if "memory" in str(f) or "_build" in str(f) or "_gen" in str(f):
                    continue
                files.append({
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
        return files

    def build_recovery_report(self) -> dict:
        report = {
            "timestamp": datetime.now().isoformat(),
            "memory": {
                "index": self.load_memory_index(),
                "status": self.load_memory_status(),
                "conventions": self.load_memory_conventions(),
                "logs": self.load_memory_logs(),
            },
            "project_files": self.scan_project_files(),
            "has_core_code": bool(list(self.core_dir.glob("*.py"))),
        }
        return report

    def find_incomplete_tasks(self) -> list:
        status = self.load_memory_status()
        tasks = []
        if status["content"]:
            for line in status["content"].split("\n"):
                line = line.strip()
                if line.startswith("- [ ]") or line.startswith("- [x]"):
                    checked = "[x]" in line
                    task_text = line.replace("- [ ] ", "").replace("- [x] ", "")
                    tasks.append({"text": task_text, "done": checked})
        return tasks

    def get_next_action(self) -> str:
        tasks = self.find_incomplete_tasks()
        for t in tasks:
            if not t["done"]:
                return t["text"]
        return "All tasks completed, no further action needed."

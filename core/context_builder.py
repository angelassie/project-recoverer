"""
Context Reconstruction Module - context_builder
Recovers lost information from memory and project files
Supports multiple memory formats: .md, .json, .yaml, .txt
"""
import json
import pathlib
from datetime import datetime
from typing import Optional


class ContextBuilder:
    def __init__(self, project_root: str):
        self.project_root = pathlib.Path(project_root)
        self.memory_dir = self.project_root / "记忆体"

    # ---- Legacy methods (kept for backward compatibility) ----

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

    # ---- New unified loader ----

    def load_memory_unified(self) -> dict:
        """Load all memory files using the multi-format MemoryLoader."""
        try:
            from memory_loader import MemoryLoader
            loader = MemoryLoader(str(self.memory_dir))
            all_mem = loader.load_all()

            result = {
                "index": all_mem.get("索引", {"content": "", "format": "unknown"}),
                "status": all_mem.get("状态", {"content": "", "format": "unknown"}),
                "conventions": all_mem.get("约定", {"content": "", "format": "unknown"}),
                "logs": all_mem.get("对话记录", {"content": "", "format": "unknown"}),
            }

            for key, val in all_mem.items():
                if key not in ("索引", "状态", "约定", "对话记录"):
                    result[key] = val

            return result

        except ImportError:
            return {
                "index": self.load_memory_index(),
                "status": self.load_memory_status(),
                "conventions": self.load_memory_conventions(),
                "logs": self.load_memory_logs(),
            }

    def scan_project_files(self, extensions=None) -> list:
        if extensions is None:
            extensions = [".py", ".md", ".json", ".txt", ".cfg", ".ini", ".yaml", ".yml"]
        files = []
        for ext in extensions:
            for f in self.project_root.rglob(f"*{ext}"):
                if "记忆体" in str(f) or "_build" in str(f) or "_gen" in str(f):
                    continue
                files.append({
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
        return files

    def build_recovery_report(self) -> dict:
        unified = self.load_memory_unified()
        formats = []
        for key in ["index", "status", "conventions", "logs"]:
            fmt = unified.get(key, {}).get("format", "")
            if fmt:
                formats.append(fmt)
        report = {
            "timestamp": datetime.now().isoformat(),
            "memory": {
                "index": unified.get("index", {}).get("content", ""),
                "status": unified.get("status", {}).get("content", ""),
                "conventions": unified.get("conventions", {}).get("content", ""),
                "logs": unified.get("logs", {}).get("content", ""),
            },
            "project_files": self.scan_project_files(),
            "has_core_code": (self.project_root / "core").exists(),
            "formats_detected": list(set(formats)),
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

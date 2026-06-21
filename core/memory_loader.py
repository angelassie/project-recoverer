"""
Memory Loader Module - memory_loader
Unified loader for memory files in multiple formats: .md, .json, .yaml, .txt
"""
import json
import pathlib
import re
from typing import Dict, List, Optional, Any


class MemoryLoader:
    """Loads memory files from multiple formats and presents a unified interface."""

    SUPPORTED_EXTENSIONS = {'.md', '.json', '.yaml', '.yml', '.txt'}

    def __init__(self, memory_dir: str):
        self.memory_dir = pathlib.Path(memory_dir)

    def list_available(self) -> List[Dict[str, Any]]:
        """List all memory files found in the memory directory."""
        if not self.memory_dir.exists():
            return []

        files = []
        for f in sorted(self.memory_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                files.append({
                    "path": str(f),
                    "name": f.name,
                    "format": f.suffix.lower().lstrip('.'),
                    "size": f.stat().st_size,
                })
        return files

    def load_all(self) -> Dict[str, Any]:
        """Load all memory files and return as a unified dictionary.

        Keys are stem names (e.g. '索引', '对话记录'), values are dicts with
        'content', 'format', and 'raw_path'.
        """
        result = {}
        for f in self.list_available():
            stem = f["name"].rsplit(".", 1)[0]
            try:
                content = self._read_file(f["path"], f["format"])
                result[stem] = {
                    "content": content,
                    "format": f["format"],
                    "raw_path": f["path"],
                }
            except Exception as e:
                result[stem] = {
                    "content": "",
                    "format": f["format"],
                    "raw_path": f["path"],
                    "error": str(e),
                }
        return result

    def load_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a specific memory file by stem name (case-insensitive).

        Priority: .md > .json > .yaml > .txt
        """
        candidates = []
        if not self.memory_dir.exists():
            return None

        for f in self.memory_dir.iterdir():
            if f.is_file() and f.stem.lower() == name.lower():
                candidates.append(f)

        if not candidates:
            return None

        # Sort by priority
        priority = {'.md': 0, '.json': 1, '.yaml': 2, '.yml': 2, '.txt': 3}
        candidates.sort(key=lambda p: priority.get(p.suffix.lower(), 99))

        chosen = candidates[0]
        fmt = chosen.suffix.lower().lstrip('.')
        content = self._read_file(str(chosen), fmt)

        return {
            "content": content,
            "format": fmt,
            "raw_path": str(chosen),
        }

    def load_index(self) -> Optional[Dict[str, Any]]:
        return self.load_by_name("索引")

    def load_status(self) -> Optional[Dict[str, Any]]:
        return self.load_by_name("状态")

    def load_conventions(self) -> Optional[Dict[str, Any]]:
        return self.load_by_name("约定")

    def load_logs(self) -> Optional[Dict[str, Any]]:
        return self.load_by_name("对话记录")

    # ---- Internal helpers ----

    def _read_file(self, filepath: str, fmt: str) -> str:
        """Read a file and return its content as a string.

        For structured formats (JSON, YAML), the content is returned as a
        human-readable string representation.
        """
        path = pathlib.Path(filepath)
        text = path.read_text(encoding="utf-8")

        if fmt == "json":
            # Pretty-print JSON for readability
            try:
                data = json.loads(text)
                return json.dumps(data, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                return text  # Fall back to raw text if invalid JSON

        elif fmt in ("yaml", "yml"):
            # Return YAML as-is (simple key-value/subset only)
            return text

        elif fmt == "txt":
            return text

        else:  # .md or unknown
            return text

    def save_memory(self, name: str, content: str, fmt: str = "md") -> bool:
        """Save memory content to a file in the specified format.

        Args:
            name: Stem name (e.g. '索引')
            content: Content string
            fmt: Output format ('md', 'json', 'yaml', 'txt')

        Returns:
            True if saved successfully, False otherwise.
        """
        if not self.memory_dir.exists():
            try:
                self.memory_dir.mkdir(parents=True, exist_ok=True)
            except OSError:
                return False

        ext_map = {
            "md": ".md",
            "json": ".json",
            "yaml": ".yaml",
            "yml": ".yaml",
            "txt": ".txt",
        }
        ext = ext_map.get(fmt.lower(), ".md")
        target = self.memory_dir / (name + ext)

        try:
            # For JSON, validate before writing
            if fmt.lower() == "json":
                # Try to parse existing file if it's JSON, then update
                if target.exists():
                    try:
                        existing = json.loads(target.read_text(encoding="utf-8"))
                        if isinstance(existing, dict):
                            existing.update(content)
                            content = existing
                    except (json.JSONDecodeError, TypeError):
                        pass

            target.write_text(content, encoding="utf-8")
            return True
        except OSError as e:
            print(f"Failed to save memory '{name}' ({fmt}): {e}")
            return False

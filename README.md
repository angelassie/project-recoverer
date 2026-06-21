# Codex Project Recovery Assistant

> **A powerful tool that recovers project context when Codex conversations are interrupted by errors.**

## Features

- **Error Analysis**: Automatically detects and classifies error messages (JSON parse, syntax errors, runtime errors, etc.)
- **Memory Recovery**: Loads and repairs project memory (记忆体) files
- **Task Tracking**: Identifies completed and pending tasks from status.md
- **Context Reconstruction**: Scans project structure and rebuilds understanding
- **Smart Suggestions**: Generates actionable next-step recommendations
- **Auto-Initialization**: Creates memory files for new projects automatically

## Quick Start

### Method 1: Use as a Codex Skill (Recommended)

In any Codex conversation, simply say:

> Use project-recoverer to recover my project

Or:

> I got an error, help me recover context

### Method 2: Run from Command Line

First, clone or download this repository:

```bash
git clone https://github.com/angelassie/project-recoverer.git
cd project-recoverer
```

Then run from your project folder:

```powershell
# Go to your project folder
cd /path/to/your/project

# Run the recovery assistant (adjust the path to where you cloned this repo)
python /path/to/project-recoverer/core/recoverer.py
```

With an error message:

```powershell
python /path/to/project-recoverer/core/recoverer.py /path/to/your/project Your_error_message_here
```

### Method 3: Use the Batch File

Copy 恢复助手.bat into any Codex project folder, then double-click it.

## Project Structure

```
project-recoverer/
+-- core/                    # Core modules
|   +-- analyzer.py          # Error pattern detection and classification
|   +-- context_builder.py   # Context reconstruction from memory
|   +-- memory_init.py       # Memory initialization for new projects
|   +-- memory_loader.py     # Memory file parser
|   +-- memory_sync.py       # Automatic memory status updates
|   +-- recoverer.py         # Main coordinator
|   +-- _extend_patterns.py  # Extended error patterns
+-- 记忆体/                   # Project memory (per project)
|   +-- 索引.md               # Project overview
|   +-- 状态.md               # Task checklist
|   +-- 约定.md               # Development rules
|   +-- 对话记录.md           # Conversation log
+-- outputs/                 # Generated recovery reports
+-- 恢复助手.bat               # Quick launcher (Windows)
+-- README.md                # This file
```

## How It Works

1. **Check Memory** - Verifies 记忆体 folder exists; initializes from template if missing
2. **Load Memory** - Reads all memory files (index, status, conventions, logs)
3. **Analyze Errors** - Categorizes error severity and type
4. **Scan Project** - Counts and catalogs project files
5. **Find Tasks** - Identifies incomplete tasks from status.md checkboxes
6. **Generate Report** - Saves recovery summary to outputs/recovery_report_*.json

## Memory Files (记忆体)

Each project uses a 记忆体 folder to track state:

| File | Purpose |
|------|---------|
| 索引.md | Project overview and file structure |
| 状态.md | Task checklist with [x] completed / [ ] pending |
| 约定.md | Development rules and coding conventions |
| 对话记录.md | Chronological log of Codex conversations |

**Tip:** Keep 状态.md updated with [x] for completed tasks to get accurate recovery suggestions.

## Supported Error Types

- JSON parse errors (BadRequestError)
- Python syntax/type errors
- Rust compilation errors
- PowerShell command errors
- File/permission/network errors
- Bad request errors
- Generic runtime errors

## Requirements

- Python 3.12+
- No external dependencies (standard library only)
- Windows PowerShell (for batch file usage)

## Output

Recovery reports are saved to: 项目路径/outputs/recovery_report_YYYYMMDD_HHMMSS.json

Reports include:
- Error summary and classification
- Task completion status
- Next action recommendation
- Project file inventory

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Memory not found | Run with --init-memory flag or double-click 恢复助手.bat |
| No tasks shown | Check that 状态.md has - [ ] task entries |
| Error analysis empty | Ensure error text is passed as second argument |
| Python not found | Install Python 3.12+ or use full path to python.exe |

## License

MIT

## Author

AngelaSie

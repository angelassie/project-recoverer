# Codex Project Recovery Assistant

A helper tool that recovers project context when Codex conversations are interrupted by errors.

## Features

- **Error Extraction**: Automatically extracts key error messages from interrupted conversations
- **Memory Repair**: Updates project memory status and marks stuck tasks
- **Recovery Suggestions**: Tells you where things left off and what to do next
- **Context Reconstruction**: Recovers lost information from memory and project files

## Project Structure

```
Project002_CodexMonitor/
├── core/                    # Core modules
│   ├── analyzer.py          # Error pattern detection and classification
│   ├── context_builder.py   # Context reconstruction from memory files
│   ├── memory_sync.py       # Automatic memory status updates
│   └── recoverer.py         # Main entry point, coordinates all modules
├── memory/                  # Project memory (Chinese filenames)
│   ├── index.md              # Index overview
│   ├── status.md              # Current status
│   ├── conventions.md              # Conventions and standards
│   └── dialogue_logs.md          # Dialogue logs
├── outputs/                 # Generated recovery reports
└── README.md                # This file
```

## Usage

Run the recovery assistant from the project root:

```bash
py core/recoverer.py <project_root> <error_text>
```

Example:

```bash
py core/recoverer.py F:/codex/Project002_CodexMonitor "JSON parse error occurred"
```

## Requirements

- Python 3.12+
- No external dependencies (uses only standard library)

## How It Works

1. Loads memory files (index, status, conventions, logs)
2. Analyzes error messages against known patterns
3. Scans project files and reconstructs context
4. Finds incomplete tasks from memory status
5. Generates recovery report and saves to outputs/
6. Updates memory with recovery results

## Known Issues

- JSON parse errors occur when using apply_patch on files with Chinese content. Use shell_command + Out-File instead.
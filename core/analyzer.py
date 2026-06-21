import re
from dataclasses import dataclass
from typing import List


@dataclass
class ErrorInfo:
    raw_text: str
    error_type: str
    severity: str
    module: str = ""
    suggestion: str = ""


_ERROR_PATTERNS = [
    {"name": "json_parse_error", "pattern": r"(BadRequestError|json.decoder.JSONDecodeError|Expecting property name)", "severity": "critical", "suggestion": "Check JSON format, use double quotes. Use shell_command + Out-File for Chinese content."},
    {"name": "timeout_error", "pattern": r"(TimeoutError|timed out|command .* exceeded time)", "severity": "warning", "suggestion": "Command took too long. Consider splitting the task."},
    {"name": "file_not_found", "pattern": r"(FileNotFoundError|No such file|path not found)", "severity": "critical", "suggestion": "Check file path, confirm the target file exists."},
    {"name": "permission_denied", "pattern": r"(PermissionError|AccessDenied|access denied)", "severity": "critical", "suggestion": "Check file/directory permissions, try running as admin."},
    {"name": "api_error", "pattern": r"(APIError|api_error|rate limit|too many requests)", "severity": "warning", "suggestion": "Check API call frequency, retry after rate limit resets."},
    {"name": "tool_failed", "pattern": r"(tool.*error|tool.*failed|unsupported.*tool)", "severity": "warning", "suggestion": "Check tool name and parameters, confirm tool is available."},
    {"name": "memory_error", "pattern": r"(MemoryError|out of memory|OOM)", "severity": "critical", "suggestion": "Reduce data size per operation or increase system memory."},
    {"name": "network_error", "pattern": r"(ConnectionError|URLError|requests.exceptions|network.*error)", "severity": "warning", "suggestion": "Check network connection, confirm target address is reachable."},
    {"name": "rust_compile_error", "pattern": r"(error\[E\d+\]|unresolved import|cannot find|this function takes.*arguments but.*supplied|mismatched types|field.*is private|no .* in .*)", "severity": "critical", "suggestion": "Rust compilation error detected. Check import paths, function signatures, and struct field visibility."},
    {"name": "python_syntax_error", "pattern": r"(SyntaxError|IndentationError|TypeError.*expected.*got|NameError.*not defined)", "severity": "critical", "suggestion": "Python syntax or type error. Check code structure and variable names."},
    {"name": "unicode_encode_error", "pattern": r"(UnicodeEncodeError|UnicodeDecodeError|codec.*can't encode)", "severity": "warning", "suggestion": "Encoding issue detected. Ensure consistent UTF-8 encoding throughout the project."},
    {"name": "module_import_error", "pattern": r"(ModuleNotFoundError|ImportError|No module named|cannot import)", "severity": "critical", "suggestion": "Missing module. Check pip install or virtual environment setup."},
    {"name": "power_shell_error", "pattern": r"(is not recognized as the name of a cmdlet|CommandNotFoundException|ParserError)", "severity": "warning", "suggestion": "PowerShell command parsing error. Check command syntax and quotes."},
]

_ERROR_NAMES = {
    "json_parse_error": "JSON Parse Error",
    "timeout_error": "Command Timeout",
    "file_not_found": "File Path Error",
    "permission_denied": "Permission Error",
    "api_error": "API Call Error",
    "tool_failed": "Tool Invocation Failed",
    "memory_error": "Out of Memory",
    "network_error": "Network Error",
    "rust_compile_error": "Rust Compilation Error",
    "python_syntax_error": "Python Syntax Error",
    "unicode_encode_error": "Encoding Error",
    "module_import_error": "Module Import Error",
    "power_shell_error": "PowerShell Command Error",
    "unknown": "Unknown Error",
}

_ERROR_SUGGESTIONS = {
    "json_parse_error": "Check JSON format, ensure double quotes are used. For Chinese content, use shell_command + Out-File instead of apply_patch.",
    "timeout_error": "Command execution took too long. Consider splitting the task or increasing the timeout limit.",
    "file_not_found": "Check if the file path is correct and confirm the target file exists.",
    "permission_denied": "Check file/directory access permissions, try running as administrator.",
    "api_error": "Check API call frequency, wait for rate limit to reset before retrying.",
    "tool_failed": "Check if the tool name and parameters are correct, confirm the tool is available.",
    "memory_error": "Reduce the amount of data processed per operation, or increase system memory.",
    "network_error": "Check network connection, confirm the target address is reachable.",
    "rust_compile_error": "Rust compilation error detected. Check import paths, function signatures, and struct field visibility.",
    "python_syntax_error": "Python syntax or type error. Check code structure and variable names.",
    "unicode_encode_error": "Encoding issue. Ensure consistent UTF-8 encoding throughout the project.",
    "module_import_error": "Missing module. Check pip install or virtual environment configuration.",
    "power_shell_error": "PowerShell command parsing error. Check command syntax and quote usage.",
    "unknown": "Unable to automatically identify error type, please manually check the error message.",
}


class ErrorAnalyzer:
    def __init__(self):
        self._compiled = []
        for p in _ERROR_PATTERNS:
            self._compiled.append({
                "code": p["name"],
                "regex": re.compile(p["pattern"], re.IGNORECASE),
                "severity": p["severity"],
                "suggestion": p["suggestion"],
            })

    def analyze(self, text):
        errors = []
        if not text or not text.strip():
            return errors
        lines = text.split("\n")
        seen_patterns = set()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            matched = False
            for pat in self._compiled:
                if pat["regex"].search(line):
                    errors.append(ErrorInfo(
                        raw_text=line,
                        error_type=_ERROR_NAMES.get(pat["code"], pat["code"]),
                        severity=pat["severity"],
                        suggestion=_ERROR_SUGGESTIONS.get(pat["code"], ""),
                    ))
                    seen_patterns.add(pat["code"])
                    matched = True
                    break
            if not matched:
                errors.append(ErrorInfo(
                    raw_text=line,
                    error_type=_ERROR_NAMES.get("unknown", "Unknown Error"),
                    severity="info",
                    suggestion=_ERROR_SUGGESTIONS.get("unknown", ""),
                ))
        return errors

    def classify(self, errors):
        result = {
            "total": len(errors),
            "critical": [e for e in errors if e.severity == "critical"],
            "warning": [e for e in errors if e.severity == "warning"],
            "info": [e for e in errors if e.severity == "info"],
            "summary": "",
        }
        if result["total"] == 0:
            result["summary"] = "No error messages found. The conversation may have been interrupted for non-error reasons."
        elif result["critical"]:
            types = ", ".join(e.error_type for e in result["critical"])
            result["summary"] = "Found %d critical errors: %s" % (len(result["critical"]), types)
        elif result["warning"]:
            types = ", ".join(e.error_type for e in result["warning"])
            result["summary"] = "Found %d warnings: %s" % (len(result["warning"]), types)
        else:
            result["summary"] = "Only general information found, no errors."
        return result

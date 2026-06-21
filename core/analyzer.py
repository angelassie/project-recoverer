"""
Error Analysis Module - analyzer
Extracts and categorizes error messages from conversation interruptions.
Extended with additional common error patterns.
"""
import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ErrorInfo:
    raw_text: str
    error_type: str
    severity: str
    module: str = ""
    suggestion: str = ""


_ERROR_PATTERNS: List[Dict[str, Any]] = [
    {
        "name": "json_parse_error",
        "pattern": r"Expecting property name enclosed in double quotes",
        "severity": "high",
        "suggestion": "Check JSON format, ensure double quotes are used. For Chinese content, use shell_command + Out-File instead of apply_patch.",
    },
    {
        "name": "bad_request_error",
        "pattern": r"BadRequestError",
        "severity": "high",
        "suggestion": "API rejected the request. Check request format and parameters.",
    },
    {
        "name": "timeout_error",
        "pattern": r"timeout|timed out|deadline exceeded",
        "severity": "medium",
        "suggestion": "Command execution took too long. Consider splitting the task or increasing the timeout limit.",
    },
    {
        "name": "file_not_found",
        "pattern": r"FileNotFoundError|No such file or directory|cannot access",
        "severity": "medium",
        "suggestion": "Check if the file path is correct and confirm the target file exists.",
    },
    {
        "name": "permission_denied",
        "pattern": r"PermissionError|access denied|insufficient privileges",
        "severity": "high",
        "suggestion": "Check file/directory access permissions, try running as administrator.",
    },
    {
        "name": "unicode_error",
        "pattern": r"UnicodeEncodeError|UnicodeDecodeError|encoding error",
        "severity": "medium",
        "suggestion": "Encoding issue. Ensure consistent UTF-8 encoding throughout the project.",
    },
    {
        "name": "syntax_error",
        "pattern": r"SyntaxError|invalid syntax",
        "severity": "high",
        "suggestion": "Python syntax error. Check code structure and variable names.",
    },
    {
        "name": "import_error",
        "pattern": r"ModuleNotFoundError|ImportError|No module named",
        "severity": "medium",
        "suggestion": "Missing module. Check pip install or virtual environment configuration.",
    },
    {
        "name": "network_error",
        "pattern": r"ConnectionError|NetworkError|socket error|request failed",
        "severity": "high",
        "suggestion": "Check network connection, confirm the target address is reachable.",
    },
    {
        "name": "api_rate_limit",
        "pattern": r"rate limit|too many requests|429",
        "severity": "medium",
        "suggestion": "API rate limit exceeded. Wait and retry after cooldown.",
    },
    {
        "name": "auth_error",
        "pattern": r"authentication failed|unauthorized|401|token expired",
        "severity": "high",
        "suggestion": "Authentication failed. Check API keys or tokens.",
    },
    {
        "name": "context_window",
        "pattern": r"context window|context length|maximum context|token limit",
        "severity": "high",
        "suggestion": "Context window limit reached. Consider summarizing or splitting task.",
    },
    {
        "name": "tool_error",
        "pattern": r"tool.*(not found|failed|error|invalid)",
        "severity": "medium",
        "suggestion": "Check if the tool name and parameters are correct, confirm the tool is available.",
    },
    {
        "name": "sandbox_error",
        "pattern": r"sandbox.*(restriction|denied|blocked)",
        "severity": "medium",
        "suggestion": "Sandbox security restriction. Check required permissions.",
    },
    {
        "name": "memory_error",
        "pattern": r"MemoryError|out of memory",
        "severity": "high",
        "suggestion": "Reduce the amount of data processed per operation, or increase system memory.",
    },
{
        "name": "regex_error",
        "pattern": r"regex|regular expression|invalid pattern|pattern syntax",
        "severity": "medium",
        "suggestion": "Regular expression syntax error. Check for unescaped characters or invalid groups.",
    },
    {
        "name": "file_encoding_error",
        "pattern": r"file.*(encoding|decode|encode).*error|codec.*error",
        "severity": "medium",
        "suggestion": "File encoding mismatch. Ensure consistent UTF-8 encoding across all files.",
    },
    {
        "name": "path_resolution_error",
        "pattern": r"path.*(resolution|not found)|invalid path|relative path",
        "severity": "medium",
        "suggestion": "Path resolution error. Check for invalid characters or overly long paths.",
    },
    {
        "name": "empty_response",
        "pattern": r"empty.*(response|result)|no data returned|returned nothing",
        "severity": "low",
        "suggestion": "Received empty response. Check API endpoint or input parameters.",
    },
    {
        "name": "markdown_parse_error",
        "pattern": r"markdown.*(parse|error)|invalid markdown",
        "severity": "low",
        "suggestion": "Markdown parsing failed. Check for malformed syntax or unsupported features.",
    },
    {
        "name": "mcp_server_error",
        "pattern": r"MCP.*(server|connection|error)|model context protocol",
        "severity": "high",
        "suggestion": "MCP server connection error. Check server status and configuration.",
    },
    {
        "name": "imagegen_error",
        "pattern": r"image.*(generation|create|render).*error|imagegen",
        "severity": "medium",
        "suggestion": "Image generation failed. Check model availability and input parameters.",
    },
    {
        "name": "automation_error",
        "pattern": r"automation.*(error|fail)|schedule.*(error|fail)|cron.*(error|fail)",
        "severity": "medium",
        "suggestion": "Automation or scheduling error. Check cron jobs or scheduled tasks.",
    },
    {
        "name": "file_system_error",
        "pattern": r"file.*(system|operation).*error|disk.*(full|error)|storage.*(error|full)",
        "severity": "high",
        "suggestion": "File system error. Check disk space and file permissions.",
    },
    {
        "name": "process_killed",
        "pattern": r"process.*(killed|terminated|stopped)|SIGKILL|SIGTERM",
        "severity": "high",
        "suggestion": "Process was killed unexpectedly. Check system resources and limits.",
    },
    {
        "name": "dependency_error",
        "pattern": r"dependency.*(error|conflict|resolution)|package.*(conflict|error)",
        "severity": "medium",
        "suggestion": "Dependency resolution error. Check package versions and compatibility.",
    },
    {
        "name": "config_error",
        "pattern": r"config.*(uration)?.*(error|fail)|settings.*(error|invalid)",
        "severity": "medium",
        "suggestion": "Configuration error. Check settings files and environment variables.",
    },
    {
        "name": "conversion_error",
        "pattern": r"conversion.*(error|fail)|type.*(cast|convert).*error",
        "severity": "low",
        "suggestion": "Data conversion error. Check format compatibility and type constraints.",
    },
    {
        "name": "browser_error",
        "pattern": r"browser.*(automation|error|fail)|playwright|selenium",
        "severity": "medium",
        "suggestion": "Browser automation error. Check browser installation and driver compatibility.",
    },
    {
        "name": "database_error",
        "pattern": r"database.*(error|connection|query)|SQL.*(error|syntax)|mongo.*(error)",
        "severity": "high",
        "suggestion": "Database error. Check connection pool, query syntax, and server status.",
    },
    {
        "name": "http_status_error",
        "pattern": r"HTTP.*(error|status)|status code.*(5|4)[0-9]{2}|response.*(error|fail)",
        "severity": "medium",
        "suggestion": "HTTP error status code received. Check request URL and server response.",
    },
    {
        "name": "ssl_certificate_error",
        "pattern": r"SSL|TLS|certificate.*(error|expired|invalid)|unsafe certificate",
        "severity": "high",
        "suggestion": "SSL/TLS certificate error. Check certificate validity and hostname match.",
    },
    {
        "name": "model_quota_error",
        "pattern": r"quota|rate limit|token limit|context window|maximum.*length",
        "severity": "medium",
        "suggestion": "API quota or billing issue. Check account balance and usage limits.",
    },
    {
        "name": "thread_management_error",
        "pattern": r"thread.*(management|error|fail)|session.*(error|expire)|conversation.*(error|lost)",
        "severity": "medium",
        "suggestion": "Thread or session management error. Check conversation thread status.",
    },
]

_ERROR_TYPE_NAMES = {
    "json_parse_error": "JSON Parse Error",
    "bad_request_error": "Bad Request Error",
    "timeout_error": "Command Timeout",
    "file_not_found": "File Path Error",
    "permission_denied": "Permission Error",
    "unicode_error": "Encoding Error",
    "syntax_error": "Python Syntax Error",
    "import_error": "Module Import Error",
    "network_error": "Network Error",
    "api_rate_limit": "Rate Limit Exceeded",
    "auth_error": "Authentication Error",
    "context_window": "Context Window Exceeded",
    "tool_error": "Tool Invocation Failed",
    "sandbox_error": "Sandbox Restriction",
    "memory_error": "Out of Memory",
}

_ERROR_SUGGESTIONS = {
    "json_parse_error": "Check JSON format, ensure double quotes are used. For Chinese content, use shell_command + Out-File instead of apply_patch.",
    "bad_request_error": "API rejected the request. Check request format and parameters.",
    "timeout_error": "Command execution took too long. Consider splitting the task or increasing the timeout limit.",
    "file_not_found": "Check if the file path is correct and confirm the target file exists.",
    "permission_denied": "Check file/directory access permissions, try running as administrator.",
    "unicode_error": "Encoding issue. Ensure consistent UTF-8 encoding throughout the project.",
    "syntax_error": "Python syntax error. Check code structure and variable names.",
    "import_error": "Missing module. Check pip install or virtual environment configuration.",
    "network_error": "Check network connection, confirm the target address is reachable.",
    "api_rate_limit": "API rate limit exceeded. Wait and retry after cooldown.",
    "auth_error": "Authentication failed. Check API keys or tokens.",
    "context_window": "Context window limit reached. Consider summarizing or splitting task.",
    "tool_error": "Check if the tool name and parameters are correct, confirm the tool is available.",
    "sandbox_error": "Sandbox security restriction. Check required permissions.",
    "memory_error": "Reduce the amount of data processed per operation, or increase system memory.",
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

    def analyze(self, text: str) -> List[ErrorInfo]:
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
                    if pat["code"] not in seen_patterns:
                        seen_patterns.add(pat["code"])
                        errors.append(ErrorInfo(
                            raw_text=line,
                            error_type=pat["code"],
                            severity=pat["severity"],
                            suggestion=pat["suggestion"],
                        ))
                    matched = True
                    break
            if not matched:
                for code, name in _ERROR_TYPE_NAMES.items():
                    if code.lower() in line.lower():
                        if code not in seen_patterns:
                            seen_patterns.add(code)
                            errors.append(ErrorInfo(
                                raw_text=line,
                                error_type=code,
                                severity="medium",
                                suggestion=_ERROR_SUGGESTIONS.get(code, "Please check the error message manually."),
                            ))
                        break
        if not errors:
            errors.append(ErrorInfo(
                raw_text=text.strip()[:200],
                error_type="unknown",
                severity="low",
                suggestion="Unable to automatically identify error type, please manually check the error message.",
            ))
        return errors

    def classify(self, errors: List[ErrorInfo]) -> Dict[str, Any]:
        total = len(errors)
        high_count = sum(1 for e in errors if e.severity == "high")
        summary_parts = []
        for e in errors:
            name = _ERROR_TYPE_NAMES.get(e.error_type, e.error_type)
            summary_parts.append("[%s] %s" % (e.severity.upper(), name))
        summary = "; ".join(summary_parts) if summary_parts else "No specific error type identified"
        return {
            "total": total,
            "high_severity": high_count,
            "summary": summary,
        }

    def get_summary(self, errors: List[ErrorInfo]) -> str:
        if not errors:
            return "No errors detected."
        result_lines = [f"Found {len(errors)} error(s):"]
        for i, err in enumerate(errors, 1):
            name = _ERROR_TYPE_NAMES.get(err.error_type, err.error_type)
            result_lines.append(f"  {i}. [{err.severity.upper()}] {name}")
            result_lines.append(f"     Detail: {err.raw_text}")
            if err.suggestion:
                result_lines.append(f"     Suggestion: {err.suggestion}")
        return "\n".join(result_lines)

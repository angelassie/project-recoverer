import pathlib
import re

# Read current analyzer.py
path = r"F:/codex/Project002_CodexMonitor/core/analyzer.py"
content = pathlib.Path(path).read_text(encoding="utf-8")

# Find the _ERROR_PATTERNS list and extend it
new_patterns = '''    {
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
'''

# Insert new patterns before the closing bracket of _ERROR_PATTERNS
# Find the position after the last existing pattern
insert_marker = '    },\n]'
insert_pos = content.rfind(insert_marker)
if insert_pos > 0:
    new_content = content[:insert_pos] + "\\n" + new_patterns + content[insert_pos:]
    pathlib.Path(path).write_text(new_content, encoding="utf-8")
    print("Extended _ERROR_PATTERNS successfully")
else:
    print("Could not find insertion point")

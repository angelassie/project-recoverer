'''
Memory Initialization Module - memory_init
Generates project-specific memory files for new projects.
Copies template from F:/codex/记忆体模板/ and customizes content.
'''
import pathlib
from datetime import datetime


# Template files to initialize
_MEMORY_FILES = ['索引.md', '对话记录.md', '状态.md', '约定.md']
_TEMPLATE_DIR = pathlib.Path('F:/codex/记忆体模板')


def init_memory(project_root, project_name='', tech_stack=''):
    '''
    Initialize memory folder and files for a new project.

    Args:
        project_root: Absolute path to the project root directory.
        project_name: Human-readable project name.
        tech_stack: Brief technology stack description.

    Returns:
        Dictionary with initialization results.
    '''
    project_path = pathlib.Path(project_root)
    memory_dir = project_path / '记忆体'

    result = {
        'success': True,
        'memory_dir': str(memory_dir),
        'files_created': [],
        'errors': [],
    }

    # Step 1: Create memory directory
    try:
        memory_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        result['success'] = False
        result['errors'].append('Failed to create memory directory: %s' % e)
        return result

    # Step 2: Copy template files
    for fname in _MEMORY_FILES:
        src = _TEMPLATE_DIR / fname
        dst = memory_dir / fname
        try:
            if src.exists():
                content = src.read_text(encoding='utf-8')
                content = _customize_content(content, project_name, str(project_root), tech_stack)
                dst.write_text(content, encoding='utf-8')
                result['files_created'].append(fname)
            else:
                result['errors'].append('Template file not found: %s' % fname)
        except Exception as e:
            result['success'] = False
            result['errors'].append('Failed to create %s: %s' % (fname, e))

    return result


def _customize_content(template, project_name, project_root, tech_stack):
    '''Replace template placeholders with actual project info.'''
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    ts_now = datetime.now().strftime('%Y-%m-%d')

    # Replace project name
    if project_name:
        template = template.replace('记忆体模板项目', project_name)
        template = template.replace('待创建实际项目', project_name)

    # Replace project path
    if project_root:
        safe_root = project_root.replace('\\', '/')
        template = template.replace('F:/codex (待创建实际项目)', safe_root)
        if project_name:
            short_name = safe_root.replace('F:/codex/', '').rstrip('/')
            insert_line = '- **本项目路径**: %s/' % short_name
            if insert_line not in template:
                # Insert after the first heading in 约定.md
                if '# 项目记忆体 · 约定' in template:
                    idx = template.index('# 项目记忆体 · 约定')
                    next_newline = template.index('\n', idx)
                    template = template[:next_newline+1] + insert_line + template[next_newline+1:]

    # Replace timestamps in index
    template = template.replace('2026-06-20 14:23', now)
    template = template.replace('2026-06-20', ts_now)

    # Replace status.md initial state
    if project_name:
        template = template.replace('记忆体模板项目', project_name)

    # Add tech stack to convention.md if provided
    if tech_stack:
        tech_section = '\n## 技术选型\n\n' + tech_stack + '\n'
        if '## 技术选型' not in template:
            # Insert before the last '---'
            parts = template.rsplit('---', 1)
            if len(parts) == 2:
                template = parts[0] + tech_section + '\n---\n' + parts[1]
            else:
                template += tech_section

    # Add initialization timestamp to dialogue log
    if project_name:
        log_entry = '\n### %s - Project Initialization\n' % ts_now
        log_entry += '- Project memory initialized\n'
        log_entry += '- Project name: %s\n' % project_name
        log_entry += '- Memory files created: 索引.md, 对话记录.md, 状态.md, 约定.md\n'

        footer = '*持续更新此文件，确保每次新对话都能快速恢复上下文。*'
        if footer in template:
            template = template.replace(footer, log_entry + '\n' + footer)

    # Update the 'recent updates' in index.md
    if project_name:
        update_line = '- %s — Memory initialized for %s' % (ts_now, project_name)
        old_update = '\\2026-06-20 14:23\\ — 初始化记忆体结构'
        if old_update in template:
            template = template.replace(old_update, update_line)

    return template

"""Small, conservative HDS directory/index helper. Python 3.10+, stdlib only."""
import argparse
from collections import Counter
from datetime import date, datetime
import json
from pathlib import Path
import re
from string import Template
import sys
from urllib.parse import quote, unquote, urlsplit

SECTIONS = [
    ('文档控制', '保留设计基线与重要变更依据。', '简记文档标识、版本、修订原因和重验范围；普通润色不另建变更报告。', [12]),
    ('项目介绍与范围', '说明为什么开发以及系统边界。', '记录背景、目标、场景和范围；详细指标引用系统需求。', [3]),
    ('系统需求', '明确硬件必须满足什么及如何验收。', '重点记录需求原因、量化边界、优先级、验收标准与设计关联；重要需求给稳定编号。', [4, 10]),
    ('系统架构', '说明总体方案、模块与资源如何配合。', '重点记录方案选择、电源与信号流向、模块依赖和资源冲突；适用时用Mermaid。', [3, 5, 8]),
    ('硬件详细设计', '提供可实施、可复核的模块电路依据。', '重点记录器件选型、工作原理、关键公式、参数来源、设计裕量、PCB约束与验证方法；按问题拆分。', [6, 7, 8, 9, 10]),
    ('接口规格', '明确模块与外部的连接契约。', '按实际接口列引脚、方向、电平、协议、时序和边界；不重复电路原理。', [5, 7]),
    ('PCB与机械设计', '把电气设计转成布板与结构约束。', '按需记录叠层、阻抗依据、布局布线、隔离距离和机械尺寸；不复制原理图。', [5, 6, 8]),
    ('功耗与热分析', '检查电源容量、功率裕量和热约束。', '记录模式、负载、效率假设、最坏条件及温升依据；引用权威参数，不把估算当实测。', [4, 5, 7]),
    ('可靠性与保护', '汇总保护目标、故障行为和覆盖缺口。', '简记EMC、ESD、EFT及故障条件；保护电路细节引用05章，高风险事项按必要深度展开。', [5, 10, 11]),
    ('设计验证', '把需求与验收方法、证据对应起来。', '优先表格记录项目、条件、标准、状态及证据；没有实测记录不得标通过。', [3, 5, 11]),
    ('风险与未决问题', '让影响当前设计的未知和风险可见。', '用短表记录问题、影响、措施、状态及关联；不生成冗长审计报告。', [5, 8, 10]),
    ('附录与参考资料', '定位设计原件和可追溯来源。', '索引原理图、网表、PCB、BOM、手册与报告及版本；不重复复制工程原件。', [1]),
]
START, END = '<!-- hds:index:start -->', '<!-- hds:index:end -->'
TEMPLATES = Path(__file__).resolve().parents[1] / 'assets' / 'templates'


def section_name(number):
    return f'{number:02}_{SECTIONS[number - 1][0]}'


def read(path):
    return path.read_text(encoding='utf-8-sig')


def safe_tree(docs):
    # Never follow a symlink/junction into a different project during mutations.
    if docs.is_symlink() or (docs.exists() and docs.resolve() != docs.absolute()):
        raise ValueError(f'文档目录包含重定向路径：{docs}')
    if docs.exists():
        for p in docs.rglob('*'):
            if p.is_symlink() or p.resolve() != p.absolute():
                raise ValueError(f'请先人工处理符号链接/联接：{p}')


def save(path, content):
    if path.exists() and read(path) == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='\n')
    return True


def render(name, **values):
    return Template(read(TEMPLATES / name)).substitute(values)


def metadata(text):
    """Read a deliberately small flat YAML subset; preserve original files."""
    m = re.match(r'\A---\n(.*?)\n---(?:\n|$)', text, re.S)
    result = {}
    if m:
        for line in m[1].splitlines():
            item = re.match(r'^([a-z_]+):\s*(.*?)\s*$', line)
            if item:
                key, value = item.groups()
                if value.startswith('"'):
                    try:
                        value = json.loads(value)
                    except ValueError:
                        pass
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1].replace("''", "'")
                else:
                    value = re.split(r'\s+#', value, maxsplit=1)[0]
                result[key] = str(value)
    return result


def documents(folder):
    return sorted(p for p in folder.rglob('*.md') if p.name != 'README.md')


def cell(value):
    return str(value).replace('|', '&#124;').replace('[', '&#91;').replace(']', '&#93;').replace('\n', ' ')


def link(label, relative):
    return f'[{cell(label)}]({quote(relative, safe="/")})'


def section_index(folder):
    rows = ['| 文档名称 | 主要解决的问题 | 当前状态 | 最近更新 |', '|---|---|---|---|']
    for p in documents(folder):
        m = metadata(read(p))
        status = m.get('status', '待核对')
        if '归档' in p.relative_to(folder).parts:
            status = f'归档 / {status}'
        rows.append('| ' + ' | '.join([
            link(m.get('title', p.stem), p.relative_to(folder).as_posix()),
            cell(m.get('purpose', '见文档正文')), cell(status), cell(m.get('updated', '待核对')),
        ]) + ' |')
    return '\n'.join(rows)


def root_index(docs):
    rows = ['| 章节 | 作用 | 文档概况（非完成度） |', '|---|---|---|']
    for n, (_, goal, _, _) in enumerate(SECTIONS, 1):
        folder = docs / section_name(n)
        active = [p for p in documents(folder) if '归档' not in p.relative_to(folder).parts and metadata(read(p)).get('status') != 'Obsolete']
        counts = Counter(metadata(read(p)).get('status', '待核对') for p in active)
        summary = '、'.join(f'{k} {v}' for k, v in sorted(counts.items())) if active else '尚无活跃主题，按需补充'
        rows.append(f'| {link(section_name(n), section_name(n) + "/README.md")} | {goal} | {summary} |')
    return '\n'.join(rows)


def replace_index(text, index):
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise ValueError('缺少唯一且顺序正确的索引标记；保留文件，请人工接入')
    a = text.index(START) + len(START)
    b = text.index(END)
    return text[:a] + '\n' + index + '\n' + text[b:]


def sync(docs):
    safe_tree(docs)
    changed, warnings = [], []
    targets = [(docs / section_name(n) / 'README.md', section_index(docs / section_name(n))) for n in range(1, 13)]
    targets.append((docs / 'README.md', root_index(docs)))
    for p, index in targets:
        try:
            value = replace_index(read(p), index)
        except (ValueError, FileNotFoundError) as e:
            warnings.append(f'{p}: {e}')
            continue
        if save(p, value):
            changed.append(p)
    return changed, warnings


def initialize(docs, project, day):
    safe_tree(docs)
    for n, (_, goal, guidance, related) in enumerate(SECTIONS, 1):
        p = docs / section_name(n) / 'README.md'
        if not p.exists():
            save(p, render('section-readme.md', section=section_name(n), goal=goal, guidance=guidance,
                           index=section_index(p.parent), related='、'.join(link(section_name(x), '../' + section_name(x) + '/README.md') for x in related)))
    p = docs / 'README.md'
    if not p.exists():
        save(p, render('root-readme.md', project=project, date=day.isoformat(), index=root_index(docs)))
    return sync(docs)


def new_document(docs, section, title, purpose, body, day):
    safe_tree(docs)
    if not re.search(r'[\u4e00-\u9fff]', title) or re.search(r'[<>:"/\\|?*\x00-\x1f]', title) or title.endswith((' ', '.')):
        raise ValueError('主题必须含中文，且不含路径、换行或Windows非法文件名字符')
    if not body.strip() or body.lstrip().startswith('---'):
        raise ValueError('须提供有内容且不含frontmatter的正文；不要创建空占位文档')
    if not all((docs / section_name(n) / 'README.md').is_file() for n in range(1, 13)):
        raise ValueError('请先初始化十二章')
    used_ids = set()
    for p in docs.rglob('*.md'):
        m = metadata(read(p))
        used_ids.add(m.get('document_id'))
        if m.get('title') == title or re.sub(r'_\d{2}_\d{2}_\d{2}$', '', p.stem) == title:
            raise ValueError(f'已存在该主题，应更新原文档：{p}')
    serial = 1
    while f'HDS-{section:02}-{serial:03}' in used_ids:
        serial += 1
    p = docs / section_name(section) / f'{title}_{day:%y_%m_%d}.md'
    if p.exists():
        raise ValueError(f'文件已存在：{p}')
    q = lambda x: json.dumps(x, ensure_ascii=False)
    save(p, render('design-document.md', title=q(title), document_id=f'HDS-{section:02}-{serial:03}',
                   created=day.isoformat(), updated=day.isoformat(), purpose=q(purpose), heading=title, body=body.strip()))
    return p


def prose(text):
    text = re.sub(r'^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$', '', text, flags=re.M | re.S)
    return re.sub(r'`[^`\n]*`', '', text)


def check(docs):
    safe_tree(docs)
    problems, titles, ids = [], {}, {}
    expected = {section_name(n) for n in range(1, 13)}
    if docs.exists():
        for p in docs.iterdir():
            if p.is_dir() and p.name not in expected:
                problems.append(f'额外一级目录需人工分类：{p.name}')
            if p.is_file() and p.name != 'README.md':
                problems.append(f'根目录文件应归入章节：{p.name}')
    for name in [''] + sorted(expected):
        p = docs / name / 'README.md'
        if not p.is_file():
            problems.append(f'缺少入口：{p}')
            continue
        index = root_index(docs) if not name else section_index(p.parent)
        try:
            if read(p) != replace_index(read(p), index):
                problems.append(f'索引过期：{p}')
        except ValueError as e:
            problems.append(f'{p}: {e}')
    root = docs / 'README.md'
    if root.exists() and not re.match(r'\A# Hardware Design Specification\n\nDocument ID: [^\n]+\nRevision: [^\n]+\nStatus: [^\n]+', read(root)):
        problems.append('总入口缺少规定的HDS标题/ID/版本/状态开头')
    for p in sorted(docs.rglob('*.md')):
        text = read(p)
        if p.name != 'README.md':
            m = metadata(text)
            for key in ['title', 'document_id', 'created', 'updated', 'revision', 'status']:
                if not m.get(key):
                    problems.append(f'{p}: 缺少元数据 {key}')
            try:
                created, updated = date.fromisoformat(m.get('created', '')), date.fromisoformat(m.get('updated', ''))
                if updated < created:
                    problems.append(f'{p}: updated早于created')
                if not p.name.endswith(f'_{created:%y_%m_%d}.md'):
                    problems.append(f'{p}: 文件日期与created不符')
            except ValueError:
                problems.append(f'{p}: 日期无效')
            if not re.fullmatch(r'.*[\u4e00-\u9fff].*_\d{2}_\d{2}_\d{2}\.md', p.name):
                problems.append(f'{p}: 主题命名不符合中文创建日期规范')
            for key, seen in [('title', titles), ('document_id', ids)]:
                value = m.get(key)
                if value and value in seen:
                    problems.append(f'{p}: 重复{key}，另见 {seen[value]}')
                elif value:
                    seen[value] = p
        # Check local inline/image links and reference definitions; not a full Markdown parser.
        clean = prose(text)
        links = re.findall(r'!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)', clean)
        links += re.findall(r'^\s{0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)', clean, re.M)
        for raw in links:
            target = raw.strip('<>')
            parts = urlsplit(target)
            if not target or target.startswith('#') or parts.scheme or parts.netloc:
                continue
            file_part = unquote(parts.path)
            if file_part and not (p.parent / file_part).exists():
                problems.append(f'{p}: 本地链接失效 {target}')
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for cmd in ['init', 'new', 'sync', 'check']:
        child = sub.add_parser(cmd)
        child.add_argument('--root', type=Path, required=True)
        if cmd in ['init', 'new']:
            child.add_argument('--date', type=date.fromisoformat, help='项目本地日期；省略使用系统本地日期')
        if cmd == 'init':
            child.add_argument('--project', required=True)
        if cmd == 'new':
            child.add_argument('--section', type=int, choices=range(1, 13), required=True)
            child.add_argument('--title', required=True)
            child.add_argument('--purpose', required=True)
            child.add_argument('--body-file', type=Path, required=True)
    args = parser.parse_args()
    docs = args.root.absolute() / 'docs'
    try:
        if args.command == 'check':
            problems = check(docs)
            for item in problems:
                print(item)
            print(f'机械检查：{len(problems)} 项问题（不代表技术审查）')
            return bool(problems)
        if args.command == 'init':
            changed, warnings = initialize(docs, args.project, args.date or datetime.now().astimezone().date())
        else:
            if args.command == 'new':
                print(new_document(docs, args.section, args.title, args.purpose, read(args.body_file), args.date or datetime.now().astimezone().date()))
            changed, warnings = sync(docs)
        print(f'索引修改：{len(changed)}')
        for warning in warnings:
            print(warning)
        return bool(warnings)
    except (ValueError, OSError, UnicodeError) as e:
        print(f'未完成：{e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

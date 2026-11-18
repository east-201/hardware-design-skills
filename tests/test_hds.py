"""Observable workflow regressions. Fixtures are synthetic, not hardware evidence."""
import importlib.util
from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hds', BASE / 'hardware-design-docs/scripts/hds.py')
hds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hds)


class Workflow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.docs = Path(self.tmp.name) / 'docs'
        self.day = date.today()
        hds.initialize(self.docs, 'STM32H743工控主板（合成测试）', self.day)

    def add(self, section, title, body, purpose='记录已确认设计与待复核条件'):
        return hds.new_document(self.docs, section, title, purpose, body, self.day)

    def test_A_initialization_and_noop(self):
        self.assertEqual(len(list(self.docs.iterdir())), 13)
        self.assertEqual(len(list(self.docs.rglob('*.md'))), 13)
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.docs.rglob('*.md')}
        hds.initialize(self.docs, '不同名称不得覆盖现有项目', self.day + timedelta(days=1))
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.docs.rglob('*.md')})
        self.assertEqual(hds.check(self.docs), [])

    def test_B_module_index_and_duplicate_refusal(self):
        p = self.add(5, '隔离RS485模块设计', '已确认隔离RS485方案；隔离电源料号TBD。\n\n相关预算见[功耗章](../08_功耗与热分析/README.md)。')
        hds.sync(self.docs)
        self.assertIn(self.day.strftime('_%y_%m_%d.md'), p.name)
        self.assertIn('隔离RS485模块设计', hds.read(p.parent / 'README.md'))
        with self.assertRaises(ValueError):
            hds.new_document(self.docs, 5, '隔离RS485模块设计', '重复', '重复正文', self.day + timedelta(days=1))
        self.assertEqual(len(list(self.docs.rglob('*.md'))), 14)
        self.assertEqual(hds.check(self.docs), [])

    def test_C_D_incremental_change_next_day(self):
        p = self.add(5, '隔离RS485模块设计', '电源采用原方案。\n\n其余收发器方案保留。')
        budget = self.add(8, '隔离侧功率预算', '当前预算对应原方案。')
        pcb = self.add(7, '隔离模块布板约束', '封装对应原方案。')
        next_day = self.day + timedelta(days=1)
        original_id = hds.metadata(hds.read(p))['document_id']
        # Simulate Codex's targeted edits; helper intentionally does not replace technical bodies.
        hds.save(p, hds.read(p).replace('电源采用原方案。', '电源变更为新DC-DC，料号及参数TBD，尚未实装。').replace(f'updated: {self.day}', f'updated: {next_day}'))
        for target in [budget, pcb]:
            hds.save(target, hds.read(target).replace('原方案。', '原方案；新DC-DC参数与封装待复核。').replace(f'updated: {self.day}', f'updated: {next_day}'))
        change = self.add(1, '修订记录', f'| 变更 | 原因 | 影响 | 重验 |\n|---|---|---|---|\n| 隔离电源替换（目标变更） | 用户决定 | [模块](../05_硬件详细设计/{p.name})、功率预算、PCB约束 | 电源与温升待执行 |')
        self.assertTrue(change.exists())
        hds.sync(self.docs)
        self.assertEqual(len(hds.documents(p.parent)), 1)
        self.assertEqual(hds.metadata(hds.read(p))['created'], str(self.day))
        self.assertEqual(hds.metadata(hds.read(p))['updated'], str(next_day))
        self.assertEqual(hds.metadata(hds.read(p))['document_id'], original_id)
        self.assertIn('其余收发器方案保留。', hds.read(p))
        self.assertIn(str(next_day), hds.read(p.parent / 'README.md'))
        self.assertEqual(hds.check(self.docs), [])

    def test_E_one_short_risk(self):
        p = self.add(5, '隔离电源设计', '功率裕量需复核。')
        risk = self.add(11, '设计风险与待确认事项', f'| 风险 | 影响 | 措施 | 状态 |\n|---|---|---|---|\n| 隔离电源功率裕量不足 | 可能欠压 | [复核负载](../05_硬件详细设计/{p.name}) | 待处理 |')
        hds.sync(self.docs)
        self.assertEqual(len(hds.documents(risk.parent)), 1)
        self.assertEqual(len(list(self.docs.rglob('*.md'))), 15)
        self.assertEqual(hds.check(self.docs), [])

    def test_F_architecture_body_and_graph_edit(self):
        body = '已确认STM32H743连接隔离RS485模块；电源实现TBD。\n\n```mermaid\nflowchart LR\n    A["STM32H743"] -->|UART| B["隔离RS485"]\n```'
        p = self.add(4, '系统总体架构', body)
        # A confirmed module rename changes both narrative and diagram together.
        hds.save(p, hds.read(p).replace('隔离RS485', '隔离RS485接口'))
        hds.sync(self.docs)
        self.assertEqual(hds.read(p).count('隔离RS485接口'), 2)
        self.assertEqual(hds.check(self.docs), [])

    def test_preserve_readme_handwriting_and_detect_stale_links(self):
        p = self.docs / hds.section_name(5) / 'README.md'
        hds.save(p, hds.read(p) + '\n手写重要约束：保持隔离边界。\n')
        d = self.add(5, '接口电路', '[缺失](不存在.md)\n\n[ref]: 不存在的资料.pdf\n\n`[示例](不检查.md)`')
        self.assertTrue(any('索引过期' in x for x in hds.check(self.docs)))
        hds.sync(self.docs)
        problems = hds.check(self.docs)
        self.assertEqual(sum('本地链接失效' in x for x in problems), 2)
        self.assertIn('手写重要约束', hds.read(p))
        hds.save(d, hds.read(d).replace('[缺失](不存在.md)', '待提供资料').replace('[ref]: 不存在的资料.pdf', ''))
        self.assertEqual(hds.check(self.docs), [])

    def test_existing_readme_not_overwritten(self):
        root = self.docs / 'README.md'
        original = '# 已有项目入口\n\n保留既有工程说明。\n'
        hds.save(root, original)
        _, warnings = hds.initialize(self.docs, '新名称', self.day)
        self.assertTrue(warnings)
        self.assertEqual(hds.read(root), original)

    def test_move_archive_inbound_and_outbound_links(self):
        p = self.add(5, '电源模块', '[预算](../08_功耗与热分析/README.md)')
        ref = self.add(11, '风险记录', f'[设计](../05_硬件详细设计/{p.name})')
        dest = p.parent / '归档' / p.name
        dest.parent.mkdir()
        p.rename(dest)
        hds.save(dest, hds.read(dest).replace('status: Draft', 'status: Obsolete').replace('../08_', '../../08_'))
        hds.save(ref, hds.read(ref).replace(f'../05_硬件详细设计/{p.name}', f'../05_硬件详细设计/归档/{p.name}'))
        hds.sync(self.docs)
        self.assertIn('归档 / Obsolete', hds.read(dest.parent.parent / 'README.md'))
        self.assertEqual(hds.check(self.docs), [])
        # Explicit deletion is mechanical here, not the default Skill behavior.
        hds.save(ref, hds.read(ref).replace(f'[设计](../05_硬件详细设计/归档/{p.name})', '设计已按测试要求删除。'))
        dest.unlink()
        hds.sync(self.docs)
        self.assertNotIn('电源模块', hds.read(dest.parent.parent / 'README.md'))
        self.assertEqual(hds.check(self.docs), [])

    def test_invalid_input_rejected_before_mutation(self):
        for title, body in [('纯英文/路径', '内容'), ('中文主题', ''), ('中文主题', '---\ntitle: 嵌套元数据')]:
            with self.assertRaises(ValueError):
                self.add(5, title, body)
        self.assertEqual(len(list(self.docs.rglob('*.md'))), 13)


if __name__ == '__main__':
    unittest.main(verbosity=2)

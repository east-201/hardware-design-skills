"""Build an inspectable synthetic example; no claims about the user's real board."""
from datetime import date
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_hds import hds, BASE

docs = BASE / 'examples/STM32H743工控主板/docs'
# Explicit project-local creation date supplied for this delivery, not a Skill default.
day = date.fromisoformat(sys.argv[1])
hds.initialize(docs, 'STM32H743工控主板（合成示例）', day)

def add(section, title, purpose, body):
    found = [p for p in hds.documents(docs / hds.section_name(section)) if hds.metadata(hds.read(p)).get('title') == title]
    return found[0] if found else hds.new_document(docs, section, title, purpose, body, day)

scope = add(2, '项目背景与设计目标', '限定示例项目的已知信息与边界', '本目录是用于演示Skill行为的合成项目，不代表可直接制造或已经验证的实际硬件。\n\n示例输入：计划开发STM32H743工控主板，已有隔离RS485模块方案，隔离电源拟替换为另一颗DC-DC。未提供原理图、BOM、料号、接口指标或测试记录；这些信息均不得推定。')
module = add(5, '隔离RS485模块设计', '记录隔离接口方案与电源变更的待复核范围', '结论：示例输入已确认采用隔离RS485；DC-DC替换属于目标变更，尚不能据此断言已经实装。\n\n| 项目 | 当前信息 |\n|---|---|\n| 收发器、隔离器厂商/完整料号/封装 | TBD，需提供方案或BOM |\n| 隔离电源 | 拟替换DC-DC，新旧料号/电压/功率/效率TBD |\n| 计算依据 | 缺负载和效率数据，不能计算功率裕量 |\n| PCB约束 | 新封装、引脚、隔离间距及热约束待复核 |\n| 验证 | 替换后需复核输出、纹波、负载与温升；条件/验收值TBD，未执行 |\n\n关联：[电源/热预算](../08_功耗与热分析/README.md)、[PCB与机械约束](../07_PCB与机械设计/README.md)、[设计验证](../10_设计验证/README.md)。')
architecture = add(4, '系统总体架构', '说明已知模块与尚未确认的连接', '已知模块为STM32H743及隔离RS485接口；连接方式与供电实现尚未提供，图中明确标为TBD。\n\n```mermaid\nflowchart LR\n    MCU["STM32H743"] -.->|"连接方式TBD"| IF["隔离RS485接口"]\n    P["隔离DC-DC：型号及供电关系TBD"] -.->|"待确认"| IF\n```\n\n虚线表示待确认关系，不能作为原理图接线依据。详见[隔离接口设计](../05_硬件详细设计/' + module.name + ')。')
risk = add(11, '设计风险与待确认事项', '跟踪隔离电源裕量不足这一项风险', '| 风险 | 影响 | 处理措施 | 状态 |\n|---|---|---|---|\n| 隔离电源功率裕量不足（示例输入，未实测确认） | 可能欠压或温升超限 | 补齐负载/效率和降额条件，复核[模块](../05_硬件详细设计/' + module.name + ') | 待处理 |')
changes = add(1, '修订记录', '保留重要目标变更和重验范围', '| 内容/原因 | 影响 | 重验 |\n|---|---|---|\n| 示例用户决定替换隔离DC-DC，具体替换原因TBD | [模块](../05_硬件详细设计/' + module.name + ')、功率/热预算、封装与PCB约束；工程文件未提供 | 输出/纹波/负载/温升，条件与标准TBD，未执行 |')
root = docs / 'README.md'
text = hds.read(root).replace('当前设计指标与已有工程资料仍需按实际信息整理；不推定已有实现或验证通过。', '示例缺少接口指标、隔离DC-DC新旧料号与负载数据；功率裕量、PCB兼容性和重验条件待复核。')
hds.save(root, text)
hds.sync(docs)
issues = hds.check(docs)
if issues:
    raise SystemExit('\n'.join(issues))
print('合成示例生成并通过机械检查；图未执行渲染。')

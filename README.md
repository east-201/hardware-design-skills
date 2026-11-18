# hardware_design-skills

为个人硬件工程师和中小型研发项目提供轻量化设计文档管理 Skill。目前包含一个 Skill：**`hardware-design-docs`**，面向 Codex，将需求、架构、电路分析、接口、PCB、验证和变更持续整理为中文 Hardware Design Specification（HDS）。

**固定分类，按需写作。** 保留十二章和必要索引，主题文档有实质内容时才创建；更新已有设计时局部修改，不为日常讨论增加繁重流程。

## 能做什么

- 初始化 `docs/`、十二个中文章节目录及其 README。
- 整理已确认的设计决策、器件选型、计算依据和已有工程资料。
- 持续更新原文档，保留首次创建日期，维护章节索引和关联。
- 审查文档一致性，跟踪影响设计推进的风险和未决问题。
- 记录重要工程变更及重验范围；按需使用 Mermaid 表达架构关系。

适用于 MCU 工控板、电源板、模拟采集板及常规嵌入式硬件项目。Skill 负责文档工作，不替代 EDA、实际测试或工程判断。

## 安装

将本仓库克隆或下载到本地，进入仓库根目录。安装整个 `hardware-design-docs` 文件夹，不能只复制 `SKILL.md`。辅助脚本需要 **Python 3.10+**，运行与回归测试均只依赖标准库。

### Windows / PowerShell

以下命令安装到用户级目录；如果同名 Skill 已存在，会停止，便于先比较已有版本。

```powershell
$skillsDirectory = Join-Path $HOME '.agents\skills'
$skillDestination = Join-Path $skillsDirectory 'hardware-design-docs'
if (Test-Path -LiteralPath $skillDestination) {
    throw '同名 Skill 已存在，请先比较或备份已有版本。'
}
New-Item -ItemType Directory -Path $skillsDirectory -Force | Out-Null
Copy-Item -LiteralPath '.\hardware-design-docs' -Destination $skillDestination -Recurse
```

### macOS / Linux

```bash
if [ -e "$HOME/.agents/skills/hardware-design-docs" ]; then
  echo '同名 Skill 已存在，请先比较或备份已有版本。'
else
  mkdir -p "$HOME/.agents/skills"
  cp -R hardware-design-docs "$HOME/.agents/skills/"
fi
```

也可将该文件夹放入硬件项目的 `.agents/skills/`，供项目成员共享。用户级与项目级按需选一种，避免同名副本造成维护混淆。未显示新 Skill 时，重新打开 Codex 后再调用。发现与配置机制见 [Codex 官方技能文档](https://learn.chatgpt.com/docs/build-skills)。

## 开始使用

在硬件项目中向 Codex 提出任务，例如：

```text
使用 $hardware-design-docs，为当前项目初始化设计文档，只记录已知信息。

使用 $hardware-design-docs，把刚才确认的隔离 RS485 方案整理进已有设计文档。

使用 $hardware-design-docs，隔离电源已决定换成另一颗 DC-DC，检查功耗预算、PCB 约束和验证的影响。

使用 $hardware-design-docs，记录隔离电源功率裕量不足这一项风险。

使用 $hardware-design-docs，审查当前文档，只报告影响设计的重要问题。
```

提供可读的原理图导出、网表、BOM、手册或明确决策，可以提高文档质量。尚未确认的指标和料号保持 TBD，候选方案不会自动变成最终设计，未执行的测试不能记为通过。

## HDS 文档结构

```text
硬件项目/
└── docs/
    ├── README.md
    ├── 01_文档控制/
    ├── 02_项目介绍与范围/
    ├── 03_系统需求/
    ├── 04_系统架构/
    ├── 05_硬件详细设计/
    ├── 06_接口规格/
    ├── 07_PCB与机械设计/
    ├── 08_功耗与热分析/
    ├── 09_可靠性与保护/
    ├── 10_设计验证/
    ├── 11_风险与未决问题/
    └── 12_附录与参考资料/
```

每章都有 `README.md`，承担章节目标、编写准则、子文档索引、关键待办和关联导航；主题按需拆分。需求、架构和详细设计优先展开，其他章节根据项目复杂度裁剪，不统一规定篇幅或小节数。

主题文件采用 `中文主题_YY_MM_DD.md`，日期表示首次创建日。后续修改保留原文件名与 `created`，更新内部 `updated`，不按天生成副本。版本和重要修订另行记录，普通润色不创建变更报告。

查看 [STM32H743 合成示例](examples/STM32H743工控主板/docs/README.md)、[章节 README 实例](examples/STM32H743工控主板/docs/05_硬件详细设计/README.md)和[模块设计实例](examples/STM32H743工控主板/docs/05_硬件详细设计/隔离RS485模块设计_26_11_13.md)。示例用于展示组织方式，未提供完整工程参数，也未进行真实硬件验证。

## 仓库内容

```text
hardware_design-skills/
├── README.md
├── LICENSE                         MIT
├── hardware-design-docs/
│   ├── SKILL.md                    Codex 入口与工作规则
│   ├── LICENSE                     安装副本保留 MIT 许可声明
│   ├── agents/openai.yaml          UI 元数据
│   ├── references/                 章节职责、写作、生命周期与来源依据
│   ├── assets/templates/           总入口、章节索引与独立主题模板
│   └── scripts/hds.py              目录初始化、索引同步和机械检查
├── examples/                       可直接查看的合成 HDS
└── tests/                          回归测试与示例构建器
```

完整规则见 [SKILL.md](hardware-design-docs/SKILL.md)；实际模板见 [总入口](hardware-design-docs/assets/templates/root-readme.md)、[章节 README](hardware-design-docs/assets/templates/section-readme.md)和[独立主题](hardware-design-docs/assets/templates/design-document.md)。模板中的变量需要替换，不能原样写入项目。

## 辅助命令

通常直接让 Codex 操作即可。需要手动维护时，可从本仓库根目录运行：

```powershell
# 替换为真实硬件项目根目录；脚本将在其中维护 docs/
$projectRoot = 'D:\Projects\MyBoard'
$localDate = Get-Date -Format 'yyyy-MM-dd'

python hardware-design-docs/scripts/hds.py init --root $projectRoot --project '我的硬件项目' --date $localDate
python hardware-design-docs/scripts/hds.py sync --root $projectRoot
python hardware-design-docs/scripts/hds.py check --root $projectRoot
```

`--date` 应使用项目本地日期；省略时使用运行系统本地日期。`new` 命令需提供有实质内容的 UTF-8 正文文件，完整参数用 `python hardware-design-docs/scripts/hds.py new --help` 查看。

`init` 不覆盖已有 README；`new` 拒绝同名主题；`sync` 只重建 `hds:index` 标记内的索引，保留外部手写内容，无变化不写盘。已有无标记索引需由 Codex 或人工先接入。目录目标、重点待办和总更新摘要仍按实际设计维护。

移动文档时同时修正入链与相对出链；旧方案优先原地标为 Obsolete 并链接替代方案，必要时放所属章的“归档/”子目录。操作细节见 [生命周期规则](hardware-design-docs/references/lifecycle-workflow.md)。

## 验证与开发

从仓库根目录运行：

```bash
python -m unittest discover -s tests -v
python hardware-design-docs/scripts/hds.py check --root examples/STM32H743工控主板
```

已有 9 项回归测试，覆盖初始化、模块新增、跨日期局部更新、简洁风险、架构正文与图同步、重复主题拒绝、手写内容保留、链接检查、移动归档及删除后的索引维护。测试使用临时目录与合成数据；它们验证工具行为，不代表技术设计正确或独立模型盲测通过。

需要重新构建示例时，可运行 `python tests/build_example.py YYYY-MM-DD`，将日期参数替换为实际项目本地日期。已有主题会保留原创建日期；示例中现有日期是历史创建日。

## 能力边界与参考

- `check` 检查命名、元数据、重复标题/ID、索引和常见本地 Markdown 文件链接；不验证标题锚点、远程网址、完整 YAML/Markdown 语法、参数语义或需求覆盖。
- 不内置 EDA 二进制解析器，不从不可解析文件中猜测电路；根据可读资料与证据开展工作。
- Mermaid 用于架构说明，不替代原理图和 PCB；仓库中的图尚未执行渲染验证。
- Skill 在调用时工作，不提供后台文件监听；符号链接和目录联接由辅助工具保守拒绝自动处理。

编写方法参考 ISO/IEC/IEEE 29148 公开摘要、FHWA 设计规格模板、NASA 系统工程手册附录、TI 参考设计资料入口及 OLIMEX 开源工程的组织方式。具体借鉴和访问范围见 [资料依据](hardware-design-docs/references/technical-evidence.md)。本项目不声称自动满足任何机构的标准认证。

## 许可证

本项目采用 [MIT License](LICENSE)。引用的第三方资料遵循各自许可证和使用条款，本项目未复制其规范全文或设计文件。

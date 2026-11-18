# 参考与裁剪依据

查阅日期：2026-11-13。以下是本Skill的工程取舍，不是标准全文或合规声明；不用这些机构名暗示认证。

| 一手来源 | 实际借鉴 | 裁剪方式 |
|---|---|---|
| [ISO/IEC/IEEE 29148:2018公开摘要](https://www.iso.org/standard/72089.html) | 需求工程覆盖生命周期及需求信息项；页面只公开摘要，未获取付费全文 | 明确、可验证、稳定标识等具体写法同时参考NASA附录C，不声称逐条实现ISO条文 |
| [FHWA 6.6 Design Specification Template](https://ops.fhwa.dot.gov/seits/sections/section6/6_6.html) | 高层设计与详细设计分开，6.6.2按项目复杂度裁剪 | 固定分类保留，简单项目少建主题；不搬运交通工程流程 |
| [NASA Systems Engineering Handbook附录C/D/I/J](https://www.nasa.gov/reference/system-engineering-handbook-appendix/) | 可验证需求、需求验证矩阵、小项目可合并记录、按规模裁剪 | 少量需求用一张含设计/验收链接的表，关键风险和重验就近记录；不设多级评审门禁 |
| [TI TIDA-010250资料入口](https://www.ti.com/tool/TIDA-010250) | 设计指南、原理图、BOM、PCB和验证资料相互配套 | 设计结论带计算/证据及原件链接；未成功读取完整设计指南，不据其臆造技术细节 |
| [OLIMEX ESP32-POE开源工程](https://github.com/OLIMEX/ESP32-POE) | 仓库分开DOCUMENTS/HARDWARE/SOFTWARE，README保留产品入口和许可证说明 | 文档引用工程原件，避免复制源文件与维护双份事实；只借鉴组织方法，未复制其设计或文档 |
| [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills) | SKILL.md入口、按需资源及可发现的技能目录 | 入口简短、引用按需读取、单一标准库辅助脚本，默认可自动选择 |

固定十二章、中文命名和创建日期后缀来自本任务要求，不是上述标准的强制目录。这里不将开源工程目录原样套为HDS。

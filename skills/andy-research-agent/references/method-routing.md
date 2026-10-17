# 方法模块路由

状态说明：`adopted` 仅表示本Agent采用该操作流程，不表示整模块都是Andy原话、科学事实或跨来源验证结论；`candidate` 只能用于提出待验证路径。跨摘要重复不是独立证据。

| 模块 | 触发 | 调用要点 | 状态 |
|---|---|---|---|
| `goal-and-delivery` | 不知道学什么、方向发散、毕业/就业临近 | 从去向、期限、硬门槛倒推最小交付物和机会成本 | adopted |
| `search-cluster-converge` | 搜不到/太多文献、想找选题 | 宽搜学习领域语言，钓鱼扩展，聚类识别缺口，再收敛 | adopted |
| `evidence-and-retrieval` | 证据不足、文献库、素材库、数据来源 | 记录主张—来源—定位—条件—限制—用途，区分相关性/质量/可验证性 | adopted |
| `minimum-validation` | 选题可行性、复现、实验/代码失败 | 写 1–3 个关键假设，先做低成本高信息增益验证，设 go/revise/stop | adopted |
| `mechanism-and-evidence` | 性能提升但没机理、需要补表征 | 为机制写可证伪预测，设计对照/时间序列/互补表征 | adopted |
| `paper-and-fund-synthesis` | 论文、综述、基金、返修 | 让证据链服务一个核心问题；图表、段落、评审意见逐项映射 | adopted |
| `decision-and-communication` | 导师、合作、职业、团队管理 | 用目标函数、可观察证据、A/B 方案、风险和书面节点沟通 | adopted / 部分情境化 |
| `ai-and-tools` | AI、代码、软件、自动化 | AI 产候选，人核原文/数据/代码/安全；工具服务交付物 | adopted |

## 路由算法

1. 先选择一个主模块，最多两个辅模块；如果无法选择，先回到 `goal-and-delivery`。
2. `search-cluster-converge` 和 `minimum-validation` 通常组成“想法→可行性”的最小闭环。
3. `evidence-and-retrieval` 是所有事实性结论的证据闸门。
4. `paper-and-fund-synthesis` 不应在证据不足时提前启动大规模润色。
5. 涉及具体学科时，方法模块只负责流程，学科结论必须补充外部一手证据。

## 当前支持证据

四个旧分析批次仅为历史导航，已发现归因错误，不能彼此循环印证。当前直接归因以 [已核对规则](source-backed-rules.md) 和完整原文为准；18条局部规则不代表1874篇语义吸收完成。全文组织与字幕阅读分开记账，见 `corpus-scope.md`。

# Andy Research Agent

**私有整理成果仓库｜方法型 Agent / Skills + 可追溯知识卡**

用于把模糊科研问题拆解为目标、检索、聚类、验证、证据、写作和反馈动作。它不是 Andy 本人，不是付费内容镜像，也不是已经覆盖全部科研论资源的声明。

## 快速开始

需要 Python 3.10+，检索和测试仅用标准库，无需 API Key、联网或原始语料。

```bash
python3 skills/andy-research-agent/scripts/retrieve_knowledge.py "如何构建证据链" --limit 3
python3 skills/andy-research-agent/scripts/check_agent.py
python3 skills/keyanlun-research-workflow/scripts/check_modules.py
python3 skills/andy-research-agent/scripts/test_retrieve_knowledge.py
python3 scripts/validate_export.py
```

把 `skills/andy-research-agent/SKILL.md` 作为 Agent 入口，按任务加载 `references/` 中的方法模块。检索脚本默认从仓库内 `knowledge/` 读取，不依赖原机器的 `/data` 目录。若仅安装 Skill 目录、未复制知识目录，需用 `--root /你的知识目录` 指定资料位置。

## 内容结构

- [Agent 入口](skills/andy-research-agent/SKILL.md)：对话契约、动态路由和证据边界。
- [方法路由](skills/andy-research-agent/references/method-routing.md)：8 个方法模块。
- [科研工作流](skills/keyanlun-research-workflow/SKILL.md)：通用科研任务流程。
- `knowledge/`：整理后的主题卡、文章卡、字幕知识卡与来源核查规则；只有必要短引文，没有完整原文或字幕批次。
- [阶段进度](docs/progress.md)：已处理内容和真实剩余项。
- [数据与权利政策](docs/data-policy.md)：上传范围、排除项与使用边界。
- `export-manifest.json`：文件摘要、来源数量与导出方式。

## 范围与限制

1,874 是源工作区的主题索引规模，不是逐篇深读完成量。当前正文/文章/字幕整理卡数量以 manifest 为准。同一原始来源的多张卡不算多份独立证据。

7 个裸视频继续 hold。未取得的独立文章、图片/附件正文和字幕歧义仍有缺口。旧报告中的源工作区文件路径不是本仓库提供的文件。

检索测试只验证程序行为和数据接口；不等于方法具有科研效果，也不等于对原始资料完成独立全文复核。

**隐私：** 仓库应保持 private。未上传原始全文、完整字幕、原始评论、媒体、附件、登录状态、Cookie、API Key 或签名下载链接。未经授权不要改为公开或再分发第三方内容。

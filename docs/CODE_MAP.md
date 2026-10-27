# 代码地图

> 最后更新：2026-10-27

## 总体结构

```text
skill-discovery-methodology/
├─ .agents/skills/                 # 官方 find-skills 与 vod-collector 技能副本
├─ .vod/feedbacks/                 # 本地脱敏 VoD 问题单
├─ docs/                           # 项目备忘、代码地图和设计
├─ reports/                        # 实时索引检索证据
├─ scripts/search_skills_local.py  # Windows 兼容只读搜索入口
├─ METHODOLOGY.md                  # 标准工作流
├─ README.md                       # 运行方式和交付物索引
└─ THIRD_PARTY_NOTICES.md          # 官方技能来源与许可证
```

## 模块职责

- `.agents/skills`：保留官方技能，便于复现实验。
- `scripts/search_skills_local.py`：读取 GitCode 实时索引、扩展关键词、评分并输出结果。
- `.vod/feedbacks`：保存 VoD collector 生成并脱敏的问题单。
- `reports`：保存两轮检索的审计记录。

## 逐文件核心内容

### `scripts/search_skills_local.py`

- 用途：在不依赖 Python HTTPS 兼容性的前提下搜索官方技能索引。
- 关键入口：`main()`、`search_skills()`、`score_skill()`。
- 数据流：curl 获取 Base64 JSON → 解码 → 中英文扩展 → 评分排序 → 文本/JSON。
- 注意：每次实时请求，不落盘缓存；不使用账号凭证。

# 华为云技能发现与开发者反馈方法论

这是华为 ICT 大赛云赛道 1.9 练习作品。项目使用华为云官方技能
`huawei-cloud-find-skills` 实时检索技能索引，再用
`huawei-cloud-vod-collector` 把能力缺口整理成脱敏的 VoD 问题单。

## 本次结果

- 通用计算查询技能：`huawei-cloud-computing-query`
- 已覆盖：ECS、BMS、IMS、AS
- CCE 查询：由 `container/cce` 分类下的专用技能处理
- 发现的问题：通用计算技能没有显式提示 CCE 的跨分类路由
- 本地问题单：`.vod/feedbacks/VOD-20261027-0001.md`
- 问题单状态：`open`，仅本地留档，未向外部仓库提交

## 安全边界

- 只读取 GitCode 公开技能索引，不读取账号数据
- 不创建云资源，不产生云服务费用
- 不在项目文件中保存 Token、AK/SK、密码或个人信息
- 关闭官方技能的可选质量遥测

## 运行

环境：Windows 11、Python 3.14.6、curl。

```powershell
python -X utf8 scripts/search_skills_local.py -k "ECS BMS IMS AS" --limit 10
python -X utf8 scripts/search_skills_local.py -k "CCE" --limit 10
```

脚本每次请求 GitCode 的 `index.json` 与 `cn-en-map.json`，不使用本地索引缓存。

## 交付物

- [技能检索记录](reports/skill-search-2026-10-27.md)
- [方法论](METHODOLOGY.md)
- [VoD 问题单](.vod/feedbacks/VOD-20261027-0001.md)
- [项目备忘](docs/PROJECT_MEMO.md)
- [代码地图](docs/CODE_MAP.md)
- [第三方声明](THIRD_PARTY_NOTICES.md)

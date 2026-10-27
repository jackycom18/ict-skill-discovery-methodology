# 项目：华为云技能发现与 VoD 反馈方法论

> 最后更新：2026-10-27

## 项目总览

- 目标：完成 ICT 云赛道 1.9，检索 ECS/BMS/IMS/AS/CCE 对应技能并沉淀 VoD 方法论。
- 技术栈：Python 标准库、curl、官方华为云技能 Markdown/脚本。
- 运行：`python -X utf8 scripts/search_skills_local.py -k "CCE"`
- 入口：`scripts/search_skills_local.py`

## 环境配置

- 系统：Windows 11
- Python：3.14.6，系统解释器
- curl：系统 PATH 中的 `curl.exe`
- 第三方 Python 包：未安装；检索脚本只使用标准库
- 官方 VoD collector 的可选 `pyyaml` 未用于本次本地运行
- 网络：GitCode 公开索引通过 `curl --noproxy "*"` 获取

## 当前状态

- 已完成：官方技能副本、Windows 兼容检索脚本、两轮实时检索、VOD-20261027-0001、方法论和提交文档。
- 正在处理：最终校验、提交、推送公开仓库、向比赛平台提交作品。
- 下一步：检查远端仓库和平台返回结果，记录 submissionId。
- 风险：GitHub raw 详情接口在本机超时，技能详情结论仅依据实时索引元数据。

## 需求与约定

- 只使用免费资源，不创建云资源。
- 所有文件位于 `C:\Users\Xzj13\Desktop\pro`。
- 不提交任何密钥、Token、AK/SK 或个人信息。
- 本地 VOD 状态为 `open`；未经授权不向 GitCode 写入 Issue。
- 代码函数注释必须包含“功能 / 输入 / 输出”。

## 待办

- [x] 完成 Windows 兼容技能检索
- [x] 完成 ECS/BMS/IMS/AS 与 CCE 对照
- [x] 生成本地脱敏 VoD
- [x] 编写方法论和证据报告
- [ ] 创建并推送公开仓库
- [ ] 在 ICT 省资格赛平台提交

## 版本历史

- 2026-10-27：定义方法论和只读安全边界。
- 2026-10-27：新增 Windows 兼容检索脚本并验证实时索引。
- 2026-10-27：完成技能缺口判断、VoD、报告和文档。

# 华为云技能检索记录

- 检索日期：2026-10-27
- 索引生成时间：2026-10-27T09:00:02Z
- 索引技能总数：170
- 数据源：GitCode `developer-skill/skills-group-contribution`
- 网络方式：curl 绕过本机不兼容的系统代理
- 云资源费用：0

## 第一次检索：计算资源

命令：

```powershell
python -X utf8 scripts/search_skills_local.py -k "ECS BMS IMS AS" --limit 10
```

关键命中：

| 评分 | 技能 | 分类/服务 | 覆盖 |
|---:|---|---|---|
| 64 | `huawei-cloud-computing-query` | `computing/ops` | ECS、BMS、IMS、AS |

该技能描述明确说明仅覆盖弹性云服务器、裸金属、镜像和弹性伸缩查询，没有声明 CCE 查询能力。

## 第二次检索：容器资源

命令：

```powershell
python -X utf8 scripts/search_skills_local.py -k "CCE" --limit 8
```

关键命中：

| 评分 | 技能 | 分类/服务 | 主要能力 |
|---:|---|---|---|
| 138 | `huawei-cloud-cce-metric-analyzer` | `container/cce` | CCE 指标分析 |
| 98 | `huawei-cloud-cce-cluster-management` | `container/cce` | 集群、节点、节点池和插件查询/管理 |
| 78 | `huawei-cloud-cce-chaos-experiment` | `container/cce` | CCE 故障演练 |
| 65 | `huawei-cloud-cce-cluster-migrator` | `container/cce` | Kubernetes 迁移到 CCE |
| 26 | `huawei-cloud-cce-kubernetes-event-analyzer` | `container/cce` | CCE Kubernetes 事件查询 |

## 结论

1. CCE 能力在官方索引中存在，并非完全缺失。
2. CCE 被归入 `container/cce`，没有并入通用计算查询技能。
3. 使用 `ECS BMS IMS AS CCE` 做一次联合检索时，通用技能与容器专用技能之间的路由关系不够直观。
4. 因此生成本地 VoD 建议：在 `huawei-cloud-computing-query` 的描述中提示 CCE 专用技能入口。

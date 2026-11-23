# 中文营养食物库

本仓库仅发布公共食物成分数据，不含个人饮食记录、体重或密钥。App 离线使用完整目录，通过 Pages 检查版本，通过固定提交的 jsDelivr 地址下载。

编辑 source/foods.jsonl 时保留原 id；营养值修改只改变 revision，不重新生成 id。每行均保留原始来源标识。新食物分配新 id，旧记录不复用。

运行 python tools/build_catalog.py，提交后手动运行 Publish food catalog 工作流。工作流验证固定 commit 的 CDN 完整下载后才发布 Pages 通知。release_seq 严格递增；回滚也创建更高序号。

数据来源与许可边界见 NOTICE 和 LICENSE。

## 分类更新

`source/categories.json` 控制侧栏分类的名称、顺序，以及食物的分类归属。`overrides` 按食物 ID 人工修正，优先于原始分类和名称规则；无法确认的食物归入“其他”。修改后运行构建和发布工作流，无需重新发布 App。请保留现有分类 ID。

分类与完整目录一起发布，App 验证 SHA-256 和分类引用后整体切换并缓存；离线沿用最近有效版本。旧版 App 会忽略新增字段。分类调整不改变食物 ID、营养值和分量。

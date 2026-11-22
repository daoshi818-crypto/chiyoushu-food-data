# 中文营养食物库

本仓库仅发布公共食物成分数据，不含个人饮食记录、体重或密钥。App 离线使用完整目录，通过 Pages 检查版本，通过固定提交的 jsDelivr 地址下载。

编辑 source/foods.jsonl 时保留原 id；营养值修改只改变 revision，不重新生成 id。每行均保留原始来源标识。新食物分配新 id，旧记录不复用。

运行 python tools/build_catalog.py，提交后手动运行 Publish food catalog 工作流。工作流验证固定 commit 的 CDN 完整下载后才发布 Pages 通知。release_seq 严格递增；回滚也创建更高序号。

数据来源与许可边界见 NOTICE 和 LICENSE。

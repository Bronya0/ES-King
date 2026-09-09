<p align="center">
  <img src="app/build/appicon.png" alt="图片标题" width="200">
</p>
<h1 align="center">ES-King </h1>
<h4 align="center"><strong>简体中文</strong> | <a href="https://github.com/Bronya0/ES-King/blob/wails/readme-en.md">English</a></h4>

<div align="center">

![License](https://img.shields.io/github/license/Bronya0/ES-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/ES-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/ES-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/ES-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/ES-King)

<strong>一个现代、实用、轻量的ES GUI客户端，支持多平台，安装包不到10mb。</strong>


</div>

让ES更好用，make es great again! 

该桌面软件用于操作、查询ES，适配各大桌面系统（除了win7），通信方式为REST API，一般无ES版本兼容问题。通过集成大量监控指标、索引操作、优化过的便捷查询界面，提升ES的使用体验和效率。

如需提出需求、bug和改进建议，请提issue。

点个star支持作者辛苦开源 谢谢❤❤

加群和作者一起交流： <a target="_blank" href="https://qm.qq.com/cgi-bin/qm/qr?k=pDqlVFyLMYEEw8DPJlRSBN27lF8qHV2v&jump_from=webapi&authKey=Wle/K0ARM1YQWlpn6vvfiZuMedy2tT9BI73mUvXVvCuktvi0fNfmNR19Jhyrf2Nz">研发技术交流群：964440643</a>

**同款Kafka客户端，已有上万人下载**：[Kafka-King](https://github.com/Bronya0/Kafka-King)

**作者另一款开源编码 AI Agent**：[ally-agent](https://github.com/Bronya0/ally-agent)

**使用&开发文档（AI生成）**：[https://zread.ai/Bronya0/ES-King](https://zread.ai/Bronya0/ES-King)


# 功能清单
- **集群状态与指标监控**：
  - 详尽的集群与节点信息：节点列表、角色、堆内存占用、总内存占用、CPU占用、磁盘空间、网络流量、5分钟负载
  - 节点级缓存统计：字段数据缓存、段缓存、查询缓存、请求缓存、段总数指标
  - 分片指标概览：活跃分片总数、初始化中分片、未分配分片、延迟分配分片、活跃分片百分比
- **索引管理与操作**：
  - 索引搜索、别名管理（支持添加 Filter/Routing、移除别名）、批量导出 CSV
  - 索引生命周期维护：新建索引、删除、打开/关闭、Flush、Refresh、清理缓存、段合并 (Force Merge)
  - Mapping 与 Settings 在线查看与动态更新
  - 数据迁移：支持基于 Reindex API 异步复制与迁移数据
  - 数据备份：支持将索引数据按 DSL 过滤并快速下载备份至本地 JSON 文件
- **文档管理 (Docs)**：
  - 文档检索：支持基于查询 DSL 分页浏览文档、排序与字段快速筛选
  - 文档操作：单条文档实时查看、在线 JSON 编辑、删除
  - 批量操作：支持按查询批量删除 (_delete_by_query)、支持本地 JSON / CSV 文件批量导入及 _bulk 批量写入
  - 字段分析：支持指定字段的高频 Top 值分布及基数 (cardinality) 统计分析
- **集群诊断与运维 (Diagnostics)**：
  - 分片列表 (Shards)：查看全量分片状态、未分配原因与所在节点
  - 分片分配解释 (Allocation Explain)：一键深度诊断分片未分配/不可移动的具体成因与官方指引
  - 线程池监控 (Thread Pool)：实时查看通用、搜索、写入等线程池活跃数、排队队列与拒绝情况
  - 热点线程 (Hot Threads)：抓取并查看节点当前 CPU 占用最高的热点线程堆栈
  - 挂起任务 (Pending Tasks)：监控主节点当前正在排队与被阻塞的任务
- **模板与生命周期策略 (Templates & ILM)**：
  - 索引模板 (Index Templates) 与组件模板 (Component Templates) 的查看、创建、编辑与删除
  - 支持直接基于已有模板一键快速创建索引
  - 索引生命周期策略 (ILM) 查看、创建与删除
- **快照与备份管理 (Snapshot & SLM)**：
  - 仓库管理：支持创建、验证、删除多种存储类型的快照仓库（fs、s3、hdfs、azure、gcs）
  - 快照操作：创建快照、指定索引过滤、快照恢复（支持按模式重命名索引、恢复全局状态、进度实时监控）
  - 自动备份策略 (SLM)：配置 Cron 调度、时间命名模板与自动保留/清理过期策略
- **分词调试 (Analysis)**：
  - 提供分词测试器，支持指定索引分词器或自定义 Analyzer 实时查看分词 Token 序列及属性
- **REST 控制台全面升级**：
  - 多 Tab 并行：支持同时开启多个查询标签页，切换自如
  - 查询收藏：常用查询 DSL 一键收藏与快速调用
  - 表格与树状图：查询结果支持在 JSON 树状结构与数据表格 (Table) 视图间自由切换
  - 常用示例：内置经典 DSL 模板，一键快速插入编辑器
  - 自动记录历史查询记录，支持一键恢复与清理
- **连接管理与配置安全**：
  - 连接卡片交互反馈（悬浮动效、当前已连接状态徽章）
  - 连接配置导入与导出（支持安全导出/无密码导出，导入自动同名更新合并）
  - 连接隔离：切换集群时重建客户端，彻底避免 BasicAuth / TLS / 自定义 CA 证书残留
- **多语言国际化 (i18n)**：
  - 完整支持简体中文 (zh-CN)、English (en)、日本語 (ja)

# 下载
[下载地址](https://github.com/Bronya0/ES-King/releases)，点击【Assets】，选择自己办公电脑的平台下载，支持windows、macos、linux。


# 截图
![2025-04-25_16-26-00](https://github.com/user-attachments/assets/45284be3-bc18-49f2-bc77-95729735a31a)

![](docs/snap/1.png)
![](docs/snap/3.png)
![](docs/snap/4.png)
![](docs/snap/5.png)

# 捐赠
有条件可以请作者喝杯咖啡，支持项目发展，感谢💕

![image](https://github.com/user-attachments/assets/da6d46da-4e24-41e3-843d-495c6cd32065)



# 参与开发
安装golang、node.js、npm，运行 go install github.com/wailsapp/wails/v2/cmd/wails@latest 安装 Wails CLI。
```
cd app
wails dev
```

# 星
[![Stargazers over time](https://starchart.cc/Bronya0/ES-King.svg)](https://starchart.cc/Bronya0/ES-King)


# 感谢
- wails：https://wails.io/docs/gettingstarted/installation
- naive ui：https://www.naiveui.com/

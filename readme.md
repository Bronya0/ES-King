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
- 详尽的集群信息：节点信息、堆内存占用、总内存占用、cpu占用、磁盘占用、网络流量、节点角色、集群健康、5分钟负载、每个节点的字段缓存、段缓存、查询缓存、请求缓存、段总数指标
- 指标查看：活跃的分片总数、初始化中的分片数量、延迟未分配的分片数量量（可能因为分配策略等待条件未满足）、活跃分片占比 (可能冻结、关闭、故障等)
- 索引指标、文档指标、内存指标、节点指标、存储指标、段指标……
- 支持集群查看
- 支持索引搜索、管理，导出csv
- 支持索引操作：索引管理、抽样查看10条文档内容、索引别名、索引设置查看、索引刷新、索引段合并、删除索引、关闭or打开索引、flush索引、清理索引缓存……
- 自带rest窗口（当然你喜欢也可以自己用postman），自动存储历史查询，一键恢复，查询结果支持搜索导出；支持es dsl的关键字悬浮提示
- 支持索引备份下载到本地

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

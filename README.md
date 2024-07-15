<div align=center><img src="assets/icon.ico"></div>
<h1 align="center">ES-King </h1>

<div align="center">

![License](https://img.shields.io/github/license/Bronya0/ES-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/ES-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/ES-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/ES-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/ES-King)

<strong>一个现代、实用的ES GUI客户端，支持多平台。</strong>


</div>

![](docs/snap/1.png)

多种配色可选，例如猛男粉:
![](docs/snap/2.png)

同款已经开发好的Kafka客户端，已有一千多人下载：[Kafka-King](https://github.com/Bronya0/Kafka-King)

如需提出需求、bug和改进建议，请提issue。

点个star支持作者辛苦开源吧 谢谢❤❤

加群和作者一起交流： <a target="_blank" href="https://qm.qq.com/cgi-bin/qm/qr?k=pDqlVFyLMYEEw8DPJlRSBN27lF8qHV2v&jump_from=webapi&authKey=Wle/K0ARM1YQWlpn6vvfiZuMedy2tT9BI73mUvXVvCuktvi0fNfmNR19Jhyrf2Nz">研发技术交流群：964440643</a>


# 下载
[下载地址](https://github.com/Bronya0/ES-King/releases)，点击【Assets】，选择自己的平台下载，支持windows、macos、linux。

# 功能清单
- 详尽的集群信息：节点信息、堆内存占用、总内存占用、cpu占用、磁盘占用、网络流量、节点角色、集群健康、5分钟负载、每个节点的字段缓存、段缓存、查询缓存、请求缓存、段总数指标都有
- 页面查看ES集群后台Task列表，开始时间、持续时间、Task内容、设涉及IP
- 分片指标查看：分片信息活跃的分片总数文(主分片和副本分片、活跃的主分片数量重新分配中的分片数量量、初始化中的分片数量(正在被创建但尚未开始服务请求、未分配的分片数量量（节点故障或配置问题、延迟未分配的分片数量量（可能因为分配策略等待条件未满足）、活跃分片占比 (可能冻结、关闭、故障等)
- 索引指标、文档指标、内存指标、节点指标、存储指标、段指标……
- 支持索引操作：索引管理、索引别名、索引映射查看、索引设置查看、索引刷新、索引段合并、索引分片、索引刷新、删除索引、关闭or打开索引、flush索引、清理索引缓存……点点点就行了
- 自带2个rest窗口（当然你喜欢也可以自己用postman），一键补全常用DSL，自动记录历史100个查询,一键恢复，再也不用重新输入。敲关键字自动补全完成dsl，支持将结果导出为json或者excel……
- ……

# 构建
```
pip install -r requirements.txt
运行 main.py
或
flet pack main.py -i assets/icon.ico -n ES-king --add-data=assets/*:assets --product-name ES-king
```

# 星
[![Stargazers over time](https://starchart.cc/Bronya0/ES-King.svg)](https://starchart.cc/Bronya0/ES-King)


# 感谢
- flet-dev：https://github.com/flet-dev/flet

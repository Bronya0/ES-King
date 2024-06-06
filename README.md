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

# 下载
[下载地址](https://github.com/Bronya0/ES-King/releases)，点击【Assets】，选择自己的平台下载，支持windows、macos、linux。

（mac m1/m2芯片请下载arm64版本）

（windows用户通常下载amd64版本即可）

# 构建
```
pip install -r requirements.txt
运行 main.py
或
flet pack main.py -i assets/icon.ico -n ES-king --add-data=assets/*:assets --product-name ES-king
```


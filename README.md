<div align=center><img src="assets/icon.ico"></div>
<h1 align="center">ES-King </h1>

<div align="center">

![License](https://img.shields.io/github/license/Bronya0/ES-King)
![GitHub release](https://img.shields.io/github/release/Bronya0/ES-King)
![GitHub All Releases](https://img.shields.io/github/downloads/Bronya0/ES-King/total)
![GitHub stars](https://img.shields.io/github/stars/Bronya0/ES-King)
![GitHub forks](https://img.shields.io/github/forks/Bronya0/ES-King)

<strong>一个现代、ES GUI客户端，使用flet构建。当前正在开发中，敬请期待</strong>



</div>

![](docs/snap/1.png)

同款已经开发好的Kafka客户端，已有一千多人下载：[Kafka-King](https://github.com/Bronya0/Kafka-King)


# 构建
```
pip install -r requirements.txt
flet pack main.py -i assets/icon.ico -n ES-king --add-data=assets/*:assets --product-name ES-king
```
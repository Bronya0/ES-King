#!/usr/bin/env python
# -*-coding:utf-8 -*-
from service.common import BROKER, TOPIC, MONITOR, SETTINGS, SIMULATE, SUGGEST, HELP, INFO
from views.broker import Broker
from views.help import Help
from views.info import Info
from views.monitor import Monitor
from views.settings import Settings
from views.simulate import Simulate
from views.suggest import Suggest
from views.topic import Topic


def get_view_instance(selected_index):
    """
    切连接的时候，返回重新new的对象，否则只返回单例对象
    """
    return {
        INFO: Info,
        BROKER: Broker,
        TOPIC: Topic,
        SIMULATE: Simulate,
        MONITOR: Monitor,
        SETTINGS: Settings,
        SUGGEST: Suggest,
        HELP: Help,
    }[selected_index]


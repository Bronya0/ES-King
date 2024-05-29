#!/usr/bin/env python
# -*-coding:utf-8 -*-
from service.common import BROKER, INDEX, MONITOR, SETTINGS, REST, SUGGEST, HELP, INFO
from views.broker import Broker
from views.help import Help
from views.index import Index
from views.info import Info
from views.rest import Rest
from views.settings import Settings
from views.suggest import Suggest


def get_view_instance(selected_index):
    """
    切连接的时候，返回重新new的对象，否则只返回单例对象
    """
    return {
        INFO: Info,
        BROKER: Broker,
        INDEX: Index,
        REST: Rest,
        SETTINGS: Settings,
        SUGGEST: Suggest,
        HELP: Help,
    }[selected_index]


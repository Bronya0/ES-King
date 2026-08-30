<!--
  - Copyright 2025 Bronya0 <tangssst@163.com>.
  - Author Github: https://github.com/Bronya0
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     https://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <n-config-provider
      :theme="Theme"
      :hljs="hljs"
      :locale="naiveLocale"
      :date-locale="naiveDateLocale"
  >
    <!--https://www.naiveui.com/zh-CN/os-theme/components/layout-->
    <n-message-provider container-style=" word-break: break-all;">
      <n-notification-provider placement="bottom-right" container-style="text-align: left;">
        <n-dialog-provider>
          <n-loading-bar-provider>

            <n-layout has-sider position="absolute" style="height: 100vh;" :class="headerClass">
              <!--header-->
              <n-layout-header bordered style="height: 42px; bottom: 0; padding: 0; ">
                <Header />
              </n-layout-header>
              <!--side + content-->
              <n-layout has-sider position="absolute" style="top: 42px; bottom: 0;">
                <n-layout-sider
                    bordered
                    collapse-mode="width"
                    :collapsed-width="60"
                    :collapsed="true"
                    style="--wails-draggable:drag"
                >
                  <Aside
                      :collapsed-width="60"
                      :value="activeItem.key"
                      :options="sideMenuOptions"
                  />

                </n-layout-sider>
                <n-layout-content style="padding: 0 16px;">
                  <keep-alive>
                    <component :is="activeItem.component"></component>
                  </keep-alive>

                </n-layout-content>
              </n-layout>
            </n-layout>
          </n-loading-bar-provider>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import {computed, onMounted, ref, shallowRef, watch} from 'vue'
import { useI18n } from 'vue-i18n'
import {
  darkTheme,
  lightTheme,
  zhCN,
  dateZhCN,
  enUS,
  dateEnUS,
  jaJP,
  dateJaJP,
  NConfigProvider,
  NLayout,
  NLayoutContent,
  NLayoutHeader,
  NMessageProvider,
} from 'naive-ui'
import Header from './components/Header.vue'
import Settings from './components/Settings.vue'
import Health from './components/Health.vue'
import Core from './components/Core.vue'
import Nodes from './components/Nodes.vue'
import Index from './components/Index.vue'
import Docs from './components/Docs.vue'
import Rest from './components/Rest.vue'
import Conn from './components/Conn.vue'
import Task from './components/Task.vue'
import Snapshot from './components/Snapshot.vue'
import Templates from './components/Templates.vue'
import Diag from './components/Diag.vue'
import Analyze from './components/Analyze.vue'
import About from './components/About.vue'
import {GetConfig, SaveTheme} from "../wailsjs/go/config/AppConfig";
import {renderIcon} from "./utils/common";
import Aside from "./components/Aside.vue";
import emitter from "./utils/eventBus";
import {
  FavoriteTwotone,
  HiveOutlined,
  SettingsSuggestOutlined, TaskAltFilled,
  ApiOutlined, LibraryBooksOutlined, AllOutOutlined, BarChartOutlined, AddAPhotoTwotone, InfoOutlined,
  DescriptionOutlined, MonitorHeartOutlined, AutoAwesomeMotionOutlined, ManageSearchOutlined
} from '@vicons/material'
import hljs from 'highlight.js/lib/core'
import json from 'highlight.js/lib/languages/json'

const { t, locale } = useI18n()

let headerClass = shallowRef('lightTheme')
let Theme = shallowRef(lightTheme)

// Naive UI locale 映射表
const naiveLocaleMap = {
  'zh-CN': { locale: zhCN, dateLocale: dateZhCN },
  'en':    { locale: enUS,  dateLocale: dateEnUS },
  'ja':    { locale: jaJP,  dateLocale: dateJaJP },
}

const naiveLocale = computed(() => naiveLocaleMap[locale.value]?.locale || zhCN)
const naiveDateLocale = computed(() => naiveLocaleMap[locale.value]?.dateLocale || dateZhCN)

hljs.registerLanguage('json', json)

onMounted(async () => {
  // 从后端加载配置
  const loadedConfig = await GetConfig()
  // 设置主题
  themeChange(loadedConfig.theme)
  // 语言切换
  if (loadedConfig.language && ['zh-CN', 'en', 'ja'].includes(loadedConfig.language)) {
    locale.value = loadedConfig.language
  }

  // =====================注册事件监听=====================
  // 主题切换
  emitter.on('update_theme', themeChange)
  // 菜单切换
  emitter.on('menu_select', handleMenuSelect)
  // 语言切换
  emitter.on('change_language', (lang) => {
    if (['zh-CN', 'en', 'ja'].includes(lang)) {
      locale.value = lang
    }
  })
})

// 侧边栏菜单 - 使用 computed 响应语言变化
const sideMenuOptions = computed(() => [
  {
    label: t('menu.cluster'),
    key: '集群',
    icon: renderIcon(HiveOutlined),
    component: Conn,
  },
  {
    label: t('menu.nodes'),
    key: '节点',
    icon: renderIcon(AllOutOutlined),
    component: Nodes,
  },
  {
    label: t('menu.index'),
    key: '索引',
    icon: renderIcon(LibraryBooksOutlined),
    component: Index,
  },
  {
    label: t('menu.docs'),
    key: '文档',
    icon: renderIcon(DescriptionOutlined),
    component: Docs,
  },
  {
    label: t('menu.rest'),
    key: 'REST',
    icon: renderIcon(ApiOutlined),
    component: Rest,
  },
  {
    label: t('menu.analyze'),
    key: '分词',
    icon: renderIcon(ManageSearchOutlined),
    component: Analyze,
  },
  {
    label: t('menu.diag'),
    key: '诊断',
    icon: renderIcon(MonitorHeartOutlined),
    component: Diag,
  },
  {
    label: t('menu.task'),
    key: 'Task',
    icon: renderIcon(TaskAltFilled),
    component: Task,
  },
  {
    label: t('menu.health'),
    key: '健康',
    icon: renderIcon(FavoriteTwotone),
    component: Health,
  },
  {
    label: t('menu.metrics'),
    key: '指标',
    icon: renderIcon(BarChartOutlined),
    component: Core,
  },
  {
    label: t('menu.snapshot'),
    key: '快照',
    icon: renderIcon(AddAPhotoTwotone),
    component: Snapshot,
  },
  {
    label: t('menu.templates'),
    key: '模板',
    icon: renderIcon(AutoAwesomeMotionOutlined),
    component: Templates,
  },
  {
    label: t('menu.settings'),
    key: '设置',
    icon: renderIcon(SettingsSuggestOutlined),
    component: Settings
  },
  {
    label: t('menu.about'),
    key: "about",
    icon: renderIcon(InfoOutlined),
    component: About
  },
])

const activeItem = shallowRef(sideMenuOptions.value[0])

// 监听语言变化更新 activeItem 的 label
watch(sideMenuOptions, (newOptions) => {
  const currentKey = activeItem.value?.key
  if (currentKey) {
    const found = newOptions.find(item => item.key === currentKey)
    if (found) {
      activeItem.value = found
    }
  }
})

// 切换菜单
function handleMenuSelect(key) {
  // 根据key寻找item
  activeItem.value = sideMenuOptions.value.find(item => item.key === key)
}

// 主题切换
function themeChange(newTheme) {
  Theme.value = newTheme === lightTheme.name ? lightTheme : darkTheme
  headerClass = newTheme === lightTheme.name ? "lightTheme" : "darkTheme"
}

</script>

<style>
body {
  margin: 0;
  font-family: sans-serif;

}

.lightTheme .n-layout-header {
  background-color: #f7f7fa;
}

.lightTheme .n-layout-sider {
  background-color: #f7f7fa !important;
}
</style>

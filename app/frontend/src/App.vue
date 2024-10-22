<template>
  <n-config-provider
      :theme="Theme"
      :hljs="hljs"
  >
    <!--https://www.naiveui.com/zh-CN/os-theme/components/layout-->
    <n-message-provider container-style=" word-break: break-all;">
      <n-notification-provider placement="bottom-right" container-style="text-align: left;">
        <n-loading-bar-provider>

          <n-layout has-sider position="absolute" style="height: 100vh;" :class="headerClass">
            <!--header-->
            <n-layout-header bordered style="height: 42px; bottom: 0; padding: 0; ">
              <Header
                  :value="activeItem.label"
                  :options="menuOptions"
              />
            </n-layout-header>
            <!--side + content-->
            <n-layout has-sider position="absolute" style="top: 42px; bottom: 0;">
              <n-layout-sider
                  bordered
                  collapse-mode="width"
                  :collapsed-width="60"
                  :width="130"
                  :collapsed="collapsed"
                  show-trigger
                  @collapse="collapsed = true"
                  @expand="collapsed = false"
                  style="--wails-draggable:drag"
              >
                <Aside
                    :collapsed-width="60"
                    :collapsed="collapsed"
                    :icon-size="24"
                    :value="activeItem.label"
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
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import {onMounted, ref, shallowRef} from 'vue'
import {
  darkTheme,
  lightTheme,
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
import Rest from './components/Rest.vue'
import Conn from './components/Conn.vue'
import Task from './components/Task.vue'
import Issue from './components/Issue.vue'
import Snapshot from './components/Snapshot.vue'
import {GetConfig, SaveTheme} from "../wailsjs/go/config/AppConfig";
import {WindowSetSize} from "../wailsjs/runtime";
import {renderIcon} from "./utils/common";
import Aside from "./components/Aside.vue";
import emitter from "./utils/eventBus";
import {
  FavoriteTwotone,
  HiveOutlined,
  SettingsSuggestOutlined,TaskAltFilled,
  AutoGraphOutlined, ApiOutlined, LibraryBooksOutlined, AllOutOutlined, BarChartOutlined, AddAPhotoTwotone
} from '@vicons/material'
import hljs from 'highlight.js/lib/core'
import json from 'highlight.js/lib/languages/json'


let headerClass = shallowRef('lightTheme')
const collapsed = ref(true)

hljs.registerLanguage('json', json)

onMounted(async () => {
  // 从后端加载配置
  const loadedConfig = await GetConfig()
  if (loadedConfig) {
    await WindowSetSize(loadedConfig.width, loadedConfig.height)
    if (loadedConfig.theme === 'light') {
      Theme.value = lightTheme
      headerClass = "lightTheme"
    } else {
      Theme.value = darkTheme
      headerClass = "darkTheme"
    }
  }

  // =====================注册事件监听=====================
  // 主题切换
  emitter.on('update_theme', themeChange)
  // 菜单切换
  emitter.on('menu_select', handleMenuSelect)
})
// 左侧菜单
const sideMenuOptions = [
  {
    label: '集群',
    key: '集群',
    icon: renderIcon(HiveOutlined),
    component: Conn,
  },
  {
    label: '节点',
    key: '节点',
    icon: renderIcon(AllOutOutlined),
    component: Nodes,
  },
  {
    label: '索引',
    key: '索引',
    icon: renderIcon(LibraryBooksOutlined),
    component: Index,
  },
  {
    label: 'REST',
    key: 'REST',
    icon: renderIcon(ApiOutlined),
    component: Rest,
  },
  {
    label: 'Task',
    key: 'Task',
    icon: renderIcon(TaskAltFilled),
    component: Task,
  },
  {
    label: '健康',
    key: '健康',
    icon: renderIcon(FavoriteTwotone),
    component: Health,
  },
  {
    label: '指标',
    key: '指标',
    icon: renderIcon(BarChartOutlined),
    component: Core,
  },
  {
    label: '快照',
    key: '快照',
    icon: renderIcon(AddAPhotoTwotone),
    component: Snapshot,
  },
  {
    label: '建议',
    key: '建议',
    icon: renderIcon(AutoGraphOutlined),
    component: Issue,
  },
  {
    label: '设置',
    key: '设置',
    icon: renderIcon(SettingsSuggestOutlined),
    component: Settings
  },

]


// 顶部菜单
const menuOptions = []


const activeItem = shallowRef(sideMenuOptions[0])

// 切换菜单
function handleMenuSelect(key) {
  // 根据key寻找item
  activeItem.value = sideMenuOptions.find(item => item.key === key)
}

let Theme = shallowRef(lightTheme)

// 主题切换
function themeChange(newTheme) {
  console.log(newTheme.name)
  Theme.value = newTheme
  headerClass = newTheme === lightTheme ? "lightTheme" : "darkTheme"
  SaveTheme(newTheme.name)
}

// 自定义主题
// /**
//  * @type import('naive-ui').GlobalThemeOverrides
//  */
// const themeOverrides = {
//   common: {
//     bodyColor: '#FDFCFF'
//   }
// }

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
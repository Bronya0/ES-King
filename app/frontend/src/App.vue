<template>
  <n-config-provider
      :theme="Theme"
  >
    <!--https://www.naiveui.com/zh-CN/os-theme/components/layout-->
    <n-message-provider>
      <n-notification-provider placement="bottom-right">
        <n-layout has-sider position="absolute" style="height: 100vh;" :class="headerClass">
          <!--header-->
          <n-layout-header bordered style="height: 42px; bottom: 0; padding: 0; ">
            <Header
                :value="activeItem.label"
                :options="menuOptions"
                @update:value="handleMenuSelect"
                @update_theme="themeChange"
            />
          </n-layout-header>
          <!--side + content-->
          <n-layout has-sider position="absolute" style="top: 42px; bottom: 0;">
            <n-layout-sider
                bordered
                collapsed
                collapse-mode="width"
                :collapsed-width="60"
                style="--wails-draggable:drag"
            >
              <Aside
                  :collapsed-width="60"
                  :value="activeItem.label"
                  @update:value="handleMenuSelect"
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
  SettingsSuggestOutlined,
  AutoGraphOutlined, ApiOutlined, LibraryBooksOutlined, AllOutOutlined, BarChartOutlined, AddAPhotoTwotone
} from '@vicons/material'

let headerClass = shallowRef('lightTheme')

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

  emitter.on('update_theme', themeChange)
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
    label: '建议',
    key: '建议',
    icon: renderIcon(AutoGraphOutlined),
    component: Issue,
  },
  {
    label: '快照',
    key: '快照',
    icon: renderIcon(AddAPhotoTwotone),
    component: Snapshot,
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
function handleMenuSelect(key, item) {
  activeItem.value = item;
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
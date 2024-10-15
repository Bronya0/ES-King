
// 渲染图标给菜单
import {h} from "vue";
import {NIcon} from "naive-ui";
import {BrowserOpenURL} from "../../wailsjs/runtime";

// 渲染图标
export function renderIcon(icon) {
  return () => h(NIcon, null, {default: () => h(icon)});
}

// 打开链接
export function openUrl(url) {
  BrowserOpenURL(url)
}

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

// 压扁json
export function flattenObject(obj, parentKey = '') {
  let flatResult = {};

  for (let key in obj) {
    if (obj.hasOwnProperty(key)) {
      let newKey = parentKey ? `${parentKey}.${key}` : key;

      if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
        // 如果当前值也是一个对象，则递归调用
        Object.assign(flatResult, flattenObject(obj[key], newKey));
      } else {
        // 否则直接赋值
        flatResult[newKey] = obj[key];
      }
    }
  }

  return flatResult;
}
// 格式化的 JSON 字符串
export function formattedJson(value) {
  if (!value) return ''
  return JSON.stringify(value, null, 1)
}
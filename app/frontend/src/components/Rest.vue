<template>
  <h2 style="width: 42px;">REST</h2>

  <n-flex vertical size="large">
    <n-flex>
      <n-select v-model:value="method" :options="methodOptions" style="width: 120px;"/>
      <n-input v-model:value="path" placeholder="输入url path，以/开头" autosize
               style="min-width: 300px;text-align: left"/>
      <n-button @click="sendRequest" :loading="send_loading" :render-icon="renderIcon(SendSharp)">Send</n-button>
      <n-button @click="exportJson" :render-icon="renderIcon(ArrowDownwardOutlined)">导出结果</n-button>
    </n-flex>
    <n-grid x-gap="20" :cols="2">
      <n-grid-item>
        <div id="json_editor" class="editarea" @paste="toTree"></div>
      </n-grid-item>
      <n-grid-item>
        <div id="json_view" class="editarea"></div>
      </n-grid-item>
    </n-grid>
  </n-flex>

</template>

<script setup>

import {
  NSpace, NTabs, NTabPane, NSelect, NInput, NButton,
  NGrid, NGridItem, NCard, NCode, useMessage, lightTheme, darkTheme
} from 'naive-ui'
import {onMounted, ref} from "vue";
import JSONEditor from 'jsoneditor';
import '../assets/css/jsoneditor.min.css'
import {
  Search
} from "../../wailsjs/go/service/ESService";
import {SendSharp, ArrowDownwardOutlined} from "@vicons/material";
import {renderIcon} from "../utils/common";
import 'ace-builds/src-noconflict/theme-tomorrow_night';
import 'ace-builds/src-noconflict/theme-monokai';
import 'jsoneditor/src/js/ace/theme-jsoneditor';
import {GetConfig, SaveTheme} from "../../wailsjs/go/config/AppConfig";
import emitter from "../utils/eventBus";

const message = useMessage()
const method = ref('GET')
const path = ref('')
const editor = ref(null);
const response = ref(null)
const send_loading = ref(false)

const methodOptions = [
  {label: 'GET', value: 'GET'},
  {label: 'POST', value: 'POST'},
  {label: 'PUT', value: 'PUT'},
  {label: 'HEAD', value: 'HEAD'},
  {label: 'PATCH', value: 'PATCH'},
  {label: 'OPTIONS', value: 'OPTIONS'},
  {label: 'DELETE', value: 'DELETE'}
]


onMounted(async () => {

  emitter.on('selectNode', selectNode)
  emitter.on('update_theme', themeChange)

  const loadedConfig = await GetConfig()
  let theme = 'ace/theme/jsoneditor'
  if (loadedConfig) {
    if (loadedConfig.theme !== 'light') {
      theme = 'ace/theme/monokai'
    }
    editor.value = new JSONEditor(document.getElementById('json_editor'), {
      mode: 'code',
      theme: theme,
      mainMenuBar: false,
      statusBar: false,
    });
    response.value = new JSONEditor(document.getElementById('json_view'), {
      mode: 'code',
      theme: theme,
      mainMenuBar: false,
      statusBar: false,
    });
    editor.value.setText(null)
    response.value.setText('{"tip": "响应结果，支持搜索"}')
  }


});

function themeChange(newTheme) {
  const new_editor_theme = newTheme.name === 'dark' ? 'ace/theme/monokai' : 'ace/theme/jsoneditor'
  editor.value.aceEditor.setTheme(new_editor_theme)
  response.value.aceEditor.setTheme(new_editor_theme)

}

const selectNode = (node) => {
  console.log("clear")
  response.value.setText('{"tip": "响应结果，支持搜索"}')
}

const sendRequest = async () => {
  send_loading.value = true
  // 清空response
  response.value.set({})
  if (!path.value.startsWith('/')) {
    path.value = '/' + path.value;
  }
  try {
    const res = await Search(method.value, path.value, editor.value.getText())
    if (res.err !== "") {
      message.error(res.err)
    } else {
      response.value.set(res.result)
    }
  } catch (e) {
    message.error(e)
  }
  send_loading.value = false

}
const toTree = () => {
  editor.value.format();
}


function exportJson() {
  const blob = new Blob([response.value.getText()], {type: 'application/json'})
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'response.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

</script>

<style scoped>
.editarea, .json_view {
  height: 70dvh;
}
</style>
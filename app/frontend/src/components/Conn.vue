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
  <div>
    <n-flex vertical>
      <n-flex align="center">
        <h2>{{ t('conn.title') }}</h2>
        <n-text>{{ t('common.total', { count: esNodes.length }) }}</n-text>
        <n-button @click="addNewNode" :render-icon="renderIcon(AddFilled)">{{ t('conn.addCluster') }}</n-button>
        <n-button @click="triggerImport" :render-icon="renderIcon(FileUploadOutlined)">{{ t('conn.importConn') }}</n-button>
        <n-button @click="exportConn" :render-icon="renderIcon(FileDownloadOutlined)">{{ t('conn.exportConn') }}</n-button>
        <input ref="fileInputRef" type="file" accept="application/json,.json" style="display: none"
               @change="onImportFileChange"/>
      </n-flex>
      <n-spin :show="spin_loading" :description="t('app.connecting')">

        <n-grid :x-gap="12" :y-gap="12" :cols="4">
          <n-gi v-for="node in esNodes" :key="node.id">
            <n-card :title="node.name" @click="selectNode(node)" hoverable class="conn_card"
                    :class="{ conn_card_selected: selectedNodeId === node.id }">

              <template #header-extra>
                <n-space>
                  <n-tag v-if="selectedNodeId === node.id" type="success" size="small" round>
                    {{ t('conn.connected') }}
                  </n-tag>
                  <n-button @click.stop="editNode(node)" size="small">
                    {{ t('common.edit') }}
                  </n-button>
                  <n-popconfirm @positive-click="deleteNode(node.id)" :negative-text="t('common.cancel')" :positive-text="t('common.confirm')">
                    <template #trigger>
                      <n-button @click.stop size="small">
                        {{ t('common.delete') }}
                      </n-button>
                    </template>
                    {{ t('conn.deleteConfirm') }}
                  </n-popconfirm>
                </n-space>
              </template>
              <n-descriptions :column="1" label-placement="left">
                <n-descriptions-item :label="t('conn.host')">
                  {{ node.host }}
                </n-descriptions-item>
              </n-descriptions>
            </n-card>
          </n-gi>
        </n-grid>
      </n-spin>
    </n-flex>

    <n-drawer v-model:show="showEditDrawer" style="width: 38.2%" placement="right">
      <n-drawer-content :title="drawerTitle">
        <n-form
            ref="formRef"
            :model="currentNode"
            :rules="{
              name: {required: true, message: t('conn.inputNickname'), trigger: 'blur'},
              host: {required: true, message: t('conn.inputHost'), trigger: 'blur'},
            }"
            label-placement="top"
            style="text-align: left;"
        >
          <n-form-item :label="t('conn.nickname')" path="name">
            <n-input v-model:value="currentNode.name" :placeholder="t('conn.inputNickname')"/>
          </n-form-item>
          <n-form-item :label="t('conn.host')" path="host">
            <n-input v-model:value="currentNode.host" :placeholder="t('conn.inputHost')"/>
          </n-form-item>
          <n-form-item :label="t('conn.username')" path="username">
            <n-input v-model:value="currentNode.username" :placeholder="t('conn.inputUsername')"/>
          </n-form-item>
          <n-form-item :label="t('conn.password')" path="password">
            <n-input
                v-model:value="currentNode.password"
                type="password"
                :placeholder="t('conn.inputPassword')"
            />
          </n-form-item>

          <n-form-item :label="t('conn.useSSL')" path="useSSL">
            <n-switch :round="false" v-model:value="currentNode.useSSL"/>
          </n-form-item>

          <n-form-item :label="t('conn.skipSSLVerify')" path="skipSSLVerify">
            <n-switch :round="false" v-model:value="currentNode.skipSSLVerify"/>
          </n-form-item>

          <n-form-item :label="t('conn.caCert')" path="caCert">
            <n-input v-model:value="currentNode.caCert" type="textarea" :placeholder="t('conn.inputCaCert')"/>
          </n-form-item>

        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="test_connect" :loading="test_connect_loading">{{ t('conn.testConnection') }}</n-button>
            <n-button @click="showEditDrawer = false">{{ t('common.cancel') }}</n-button>
            <n-button type="primary" @click="saveNode">{{ t('common.save') }}</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import {computed, onMounted, ref} from 'vue'
import {useDialog, useMessage} from 'naive-ui'
import {download_file, renderIcon} from "../utils/common";
import {AddFilled, FileDownloadOutlined, FileUploadOutlined} from "@vicons/material";
import emitter from "../utils/eventBus";
import {SetConnect, TestClient} from "../../wailsjs/go/service/ESService";
import {GetConfig, SaveConfig} from "../../wailsjs/go/config/AppConfig";

const { t } = useI18n()

const message = useMessage()

const dialog = useDialog()

const esNodes = ref([])

const selectedNodeId = ref(null)

const showEditDrawer = ref(false)

const defaultNode = () => ({
  name: '',
  host: '',
  username: '',
  password: '',
  useSSL: false,
  skipSSLVerify: false,
  caCert: ''
})

const currentNode = ref(defaultNode())
const isEditing = ref(false)
const spin_loading = ref(false)
const test_connect_loading = ref(false)

const drawerTitle = computed(() => isEditing.value ? t('conn.editTitle') : t('conn.addTitle'))

const formRef = ref(null)

const fileInputRef = ref(null)

onMounted(() => {
  refreshNodeList()
})

const refreshNodeList = async () => {
  spin_loading.value = true
  const config = await GetConfig()
  esNodes.value = config.connects.filter(node => node.name !== null && node.name !== "")
  spin_loading.value = false
}

function editNode(node) {
  currentNode.value = {...node}
  isEditing.value = true
  showEditDrawer.value = true
}

const addNewNode = async () => {
  currentNode.value = defaultNode()
  isEditing.value = false
  showEditDrawer.value = true
}

const saveNode = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {

      const config = await GetConfig()
      // edit
      if (isEditing.value) {
        const index = esNodes.value.findIndex(node => node.id === currentNode.value.id)
        if (index !== -1) {
          esNodes.value[index] = {...currentNode.value}
        }
      } else {
        // add
        const newId = Math.max(...esNodes.value.map(node => node.id), 0) + 1
        esNodes.value.push({...currentNode.value, id: newId})
      }

      // 保存
      config.connects = esNodes.value
      const err = await SaveConfig(config)
      if (err !== "") {
        message.error(t('common.saveFailed', { msg: err }))
        return
      }
      showEditDrawer.value = false

      await refreshNodeList()
      message.success(t('common.saveSuccess'))
    } else {
      message.error(t('common.fillRequired'))
    }
  })
}

const deleteNode = async (id) => {
  esNodes.value = esNodes.value.filter(node => node.id !== id)
  const config = await GetConfig()
  config.connects = esNodes.value
  const err = await SaveConfig(config)
  if (err !== "") {
    message.error(t('common.saveFailed', { msg: err }))
    await refreshNodeList()
    return
  }
  if (selectedNodeId.value === id) {
    selectedNodeId.value = null
  }
  await refreshNodeList()
  message.success(t('common.saveSuccess'))
}

// ==================== 连接配置导出/导入 ====================

const exportConn = () => {
  if (!esNodes.value.length) {
    message.warning(t('conn.exportEmpty'))
    return
  }
  dialog.warning({
    title: t('conn.exportTitle'),
    content: t('conn.exportPwdAsk'),
    positiveText: t('conn.exportWithPassword'),
    negativeText: t('conn.exportWithoutPassword'),
    onPositiveClick: () => doExport(true),
    onNegativeClick: () => doExport(false),
  })
}

const doExport = (includePassword) => {
  const connects = esNodes.value.map(node => {
    const item = {
      name: node.name,
      host: node.host,
      useSSL: !!node.useSSL,
      skipSSLVerify: !!node.skipSSLVerify,
      caCert: node.caCert || '',
    }
    if (node.username) {
      item.username = node.username
    }
    if (includePassword && node.password) {
      item.password = node.password
    }
    return item
  })
  const payload = {
    app: 'ES-King',
    type: 'es-king-connections',
    version: 1,
    exportedAt: new Date().toISOString(),
    connects,
  }
  const fileName = `es-king-connections-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.json`
  download_file(JSON.stringify(payload, null, 2), fileName, 'application/json;charset=utf-8;')
  message.success(t('conn.exportSuccess', { count: connects.length }))
}

const triggerImport = () => {
  fileInputRef.value?.click()
}

const readAsText = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader()
  reader.onload = () => resolve(reader.result)
  reader.onerror = () => reject(reader.error)
  reader.readAsText(file, 'utf-8')
})

const onImportFileChange = async (e) => {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) {
    return
  }

  let list
  try {
    const data = JSON.parse(await readAsText(file))
    list = Array.isArray(data) ? data : (Array.isArray(data?.connects) ? data.connects : null)
  } catch (err) {
    list = null
  }
  if (!list) {
    message.error(t('conn.importInvalid'))
    return
  }

  const valid = list.filter(node => node && typeof node === 'object'
      && typeof node.name === 'string' && node.name.trim() !== ''
      && typeof node.host === 'string' && node.host.trim() !== '')
  if (!valid.length) {
    message.warning(t('conn.importEmpty'))
    return
  }

  const normalize = (node) => ({
    name: node.name.trim(),
    host: node.host.trim(),
    username: typeof node.username === 'string' ? node.username : '',
    password: typeof node.password === 'string' ? node.password : '',
    useSSL: !!node.useSSL,
    skipSSLVerify: !!node.skipSSLVerify,
    caCert: typeof node.caCert === 'string' ? node.caCert : '',
  })

  // 同名连接直接更新覆盖；空字段保留原值（如"不包含密码"导出的文件不会清掉已保存的密码）
  const byName = new Map(esNodes.value.map(node => [node.name, node]))
  const toAdd = []
  let updated = 0
  for (const raw of valid) {
    const node = normalize(raw)
    const exist = byName.get(node.name)
    if (exist) {
      exist.host = node.host
      if (node.username) {
        exist.username = node.username
      }
      if (node.password) {
        exist.password = node.password
      }
      if (node.caCert) {
        exist.caCert = node.caCert
      }
      if ('useSSL' in raw) {
        exist.useSSL = node.useSSL
      }
      if ('skipSSLVerify' in raw) {
        exist.skipSSLVerify = node.skipSSLVerify
      }
      updated += 1
    } else {
      byName.set(node.name, node)
      toAdd.push(node)
    }
  }

  let nextId = Math.max(...esNodes.value.map(node => node.id), 0)
  for (const node of toAdd) {
    nextId += 1
    esNodes.value.push({...node, id: nextId})
  }

  const config = await GetConfig()
  config.connects = esNodes.value
  const err = await SaveConfig(config)
  if (err !== "") {
    message.error(t('common.saveFailed', { msg: err }))
    await refreshNodeList()
    return
  }
  await refreshNodeList()
  if (toAdd.length) {
    message.success(t('conn.importSuccess', { count: toAdd.length, updated }))
  } else {
    message.success(t('conn.importNoNew', { count: updated }))
  }
}

const test_connect = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {

      test_connect_loading.value = true
      try {
        const node = currentNode.value
        const res = await TestClient(node.host, node.username, node.password, node.caCert, node.useSSL, node.skipSSLVerify)
        if (res !== "") {
          message.error(t('conn.connectFailed', { msg: res }))
        } else {
          message.success(t('conn.connectSuccess'))
        }
      } catch (e) {
        message.error(e.message)
      }
      test_connect_loading.value = false

    } else {
      message.error(t('common.fillRequired'))
    }
  })
}
const selectNode = async (node) => {
  spin_loading.value = true

  try {
    const res = await TestClient(node.host, node.username, node.password, node.caCert, node.useSSL, node.skipSSLVerify)
    if (res !== "") {
      message.error(t('conn.connectFailed', { msg: res }))
    } else {
      await SetConnect(node.name, node.host, node.username, node.password, node.caCert, node.useSSL, node.skipSSLVerify)
      selectedNodeId.value = node.id
      message.success(t('conn.connectSuccess'))
      emitter.emit('menu_select', "节点")
      emitter.emit('selectNode', node)
    }
  } catch (e) {
    message.error(e.message)
  }
  spin_loading.value = false

}
</script>

<style>

.lightTheme .conn_card {
  background-color: #fafafc
}

/* 连接卡片可点击的视觉反馈 */
.conn_card {
  cursor: pointer;
  transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
}

.conn_card:hover {
  border-color: #36ad6a;
  box-shadow: 0 4px 14px rgba(24, 160, 88, .25);
  transform: translateY(-2px);
}

.conn_card:active {
  transform: translateY(0);
}

/* 当前已连接的集群卡片 */
.conn_card.conn_card_selected,
.conn_card.conn_card_selected:hover {
  border-color: #18a058;
  box-shadow: 0 0 0 1px #18a058 inset, 0 4px 14px rgba(24, 160, 88, .3);
}

.lightTheme .conn_card.conn_card_selected {
  background-color: rgba(24, 160, 88, .05);
}
</style>

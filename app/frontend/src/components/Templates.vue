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
  <n-flex vertical>
    <n-flex align="center">
      <h2>{{ t('templates.title') }}</h2>
      <n-text>{{ t('templates.desc') }}</n-text>
    </n-flex>

    <n-tabs type="line" animated>
      <!-- ============ 索引模板 ============ -->
      <n-tab-pane name="indexTemplate" :tab="t('templates.tabIndexTemplate')">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getTemplates">{{ t('common.refresh') }}</n-button>
            <n-button :render-icon="renderIcon(AddFilled)" @click="openCreateTpl">{{ t('templates.createTemplate') }}</n-button>
          </n-flex>
          <n-spin :show="tplLoading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="tplColumns"
                :data="tplData"
                :max-height="500"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>
      </n-tab-pane>

      <!-- ============ 组件模板 ============ -->
      <n-tab-pane name="componentTemplate" :tab="t('templates.tabComponentTemplate')">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getComponentTemplates">
              {{ t('common.refresh') }}
            </n-button>
          </n-flex>
          <n-spin :show="compLoading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="compColumns"
                :data="compData"
                :max-height="500"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>
      </n-tab-pane>
    </n-tabs>

    <!-- 模板详情 -->
    <n-modal v-model:show="detail.show" preset="card" :title="detail.title" style="width: 720px; max-width: 90vw; text-align: left;">
      <n-scrollbar style="max-height: 65vh;">
        <n-code :code="detail.content" language="json" show-line-numbers word-wrap style="text-align: left;"/>
      </n-scrollbar>
      <template #footer>
        <n-flex justify="end">
          <n-button @click="detail.show = false">{{ t('common.close') }}</n-button>
        </n-flex>
      </template>
    </n-modal>

    <!-- 创建模板 -->
    <n-modal v-model:show="createForm.show" preset="card" :title="t('templates.createTemplate')" style="width: 640px; text-align: left;">
      <n-form label-placement="top">
        <n-form-item :label="t('templates.tplName')">
          <n-input v-model:value="createForm.name" placeholder="my-template"/>
        </n-form-item>
        <n-form-item :label="t('templates.tplBody')">
          <n-input v-model:value="createForm.body" type="textarea" :autosize="{minRows: 10, maxRows: 22}"
                   class="json-editor-input"
                   :placeholder='JSON.stringify({"index_patterns": ["logs-*"], "template": {"settings": {}, "mappings": {}}}, null, 2)'/>
        </n-form-item>
      </n-form>
      <template #footer>
        <n-flex justify="end">
          <n-button @click="createForm.show = false">{{ t('common.cancel') }}</n-button>
          <n-button type="primary" :loading="createForm.saving" @click="submitCreateTpl">{{ t('common.save') }}</n-button>
        </n-flex>
      </template>
    </n-modal>
  </n-flex>
</template>

<script setup>
import {useI18n} from 'vue-i18n'
import {computed, h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NTag, useDialog, useMessage} from 'naive-ui'
import {refColumns, renderIcon} from "../utils/common";
import {AddFilled, RefreshOutlined} from "@vicons/material";
import {
  CreateIndexTemplate,
  DeleteIndexTemplate,
  GetComponentTemplates,
  GetIndexTemplates,
} from "../../wailsjs/go/service/ESService";

const {t} = useI18n()
const message = useMessage()
const dialog = useDialog()

// ==================== 索引模板 ====================
const tplData = ref([])
const tplLoading = ref(false)

const getTemplates = async () => {
  tplLoading.value = true
  try {
    const res = await GetIndexTemplates()
    if (res.err !== "") {
      message.error(res.err)
    } else {
      tplData.value = res.results || []
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    tplLoading.value = false
  }
}

const detail = ref({
  show: false,
  title: '',
  content: '',
})

const viewTemplateDetail = (row) => {
  const body = {
    index_patterns: row.index_patterns,
    composed_of: row.composed_of,
    priority: row.priority,
    version: row.version,
    template: row._template,
  }
  detail.value = {
    show: true,
    title: row.name,
    content: JSON.stringify(body, null, 2),
  }
}

const createForm = ref({
  show: false,
  name: '',
  body: '',
  saving: false,
})

const openCreateTpl = () => {
  createForm.value.show = true
}

const submitCreateTpl = async () => {
  if (!createForm.value.name) {
    message.warning(t('templates.inputTplName'))
    return
  }
  createForm.value.saving = true
  try {
    const res = await CreateIndexTemplate(createForm.value.name, createForm.value.body)
    if (res.err !== "") {
      message.error(res.err)
    } else {
      message.success(t('templates.tplCreated'))
      createForm.value.show = false
      createForm.value.name = ''
      createForm.value.body = ''
      await getTemplates()
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    createForm.value.saving = false
  }
}

const deleteTemplate = (name) => {
  dialog.warning({
    title: t('common.warning'),
    content: t('templates.confirmDeleteTpl', {name}),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      const res = await DeleteIndexTemplate(name)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success(t('templates.tplDeleted'))
        await getTemplates()
      }
    }
  })
}

const renderPatternList = (patterns) => {
  if (!Array.isArray(patterns) || patterns.length === 0) return '-'
  return patterns.join(', ')
}

const tplColumns = computed(() => refColumns([
  {title: t('templates.colTplName'), key: 'name'},
  {
    title: t('templates.colPatterns'), key: 'index_patterns',
    render: (row) => renderPatternList(row.index_patterns),
  },
  {
    title: t('templates.colComposedOf'), key: 'composed_of',
    render: (row) => renderPatternList(row.composed_of),
  },
  {title: t('templates.colPriority'), key: 'priority', width: 90},
  {
    title: t('common.operation'), key: 'actions', width: 160,
    render: (row) => h('div', {style: 'display: flex; gap: 8px;'}, [
      h(NButton, {size: 'small', quaternary: true, type: 'info', onClick: () => viewTemplateDetail(row)},
          {default: () => t('common.details')}),
      h(NButton, {size: 'small', quaternary: true, type: 'error', onClick: () => deleteTemplate(row.name)},
          {default: () => t('common.delete')}),
    ])
  },
]))

// ==================== 组件模板 ====================
const compData = ref([])
const compLoading = ref(false)

const getComponentTemplates = async () => {
  compLoading.value = true
  try {
    const res = await GetComponentTemplates()
    if (res.err !== "") {
      message.error(res.err)
    } else {
      compData.value = res.results || []
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    compLoading.value = false
  }
}

const viewComponentDetail = (row) => {
  detail.value = {
    show: true,
    title: row.name,
    content: JSON.stringify(row._template || {}, null, 2),
  }
}

const compColumns = computed(() => refColumns([
  {title: t('templates.colTplName'), key: 'name'},
  {
    title: 'version', key: 'version', width: 90,
    render: (row) => row.version ?? '-',
  },
  {
    title: t('common.operation'), key: 'actions', width: 100,
    render: (row) => h(NButton, {size: 'small', quaternary: true, type: 'info', onClick: () => viewComponentDetail(row)},
        {default: () => t('common.details')}),
  },
]))

// ==================== 生命周期 ====================
const selectNode = async () => {
  tplData.value = []
  compData.value = []
  await getTemplates()
  await getComponentTemplates()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  getTemplates()
  getComponentTemplates()
})
</script>

<style scoped>
.json-editor-input :deep(textarea) {
  text-align: left !important;
  font-family: Consolas, Monaco, monospace;
}
</style>

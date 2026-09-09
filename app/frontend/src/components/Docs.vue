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
      <h2>{{ t('docs.title') }}</h2>
      <n-text>{{ t('docs.desc') }}</n-text>
    </n-flex>

    <n-tabs type="line" v-model:value="activeTab">
      <!-- ============ 文档浏览 ============ -->
      <n-tab-pane name="browse" :tab="t('docs.tabBrowse')">
        <n-flex vertical>
          <n-flex align="center">
            <n-select
                v-model:value="browseIndex"
                :options="indexOptions"
                :loading="indexLoading"
                filterable
                clearable
                :placeholder="t('docs.selectIndex')"
                style="width: 260px; min-width: 240px; flex-shrink: 0;"
                @update:value="resetBrowse"
            />
            <n-tooltip trigger="hover">
              <template #trigger>
                <n-button :loading="indexLoading" :render-icon="renderIcon(RefreshOutlined)" @click="loadIndexes" />
              </template>
              {{ t('docs.refreshIndexes') }}
            </n-tooltip>
            <n-input
                v-model:value="queryDsl"
                type="textarea"
                :autosize="{minRows: 1, maxRows: 6}"
                :placeholder='t("docs.queryPlaceholder")'
                style="min-width: 280px; flex: 1;"
                @keydown.enter="newSearch"
            />
            <n-button :loading="loading" :render-icon="renderIcon(SearchFilled)" @click="newSearch">
              {{ t('common.search') }}
            </n-button>
            <n-button :render-icon="renderIcon(AddFilled)" @click="openAddDoc">{{ t('docs.addDoc') }}</n-button>
            <n-button :render-icon="renderIcon(DriveFileMoveTwotone)" @click="openImportTab">
              {{ t('docs.import') }}
            </n-button>
            <n-button type="error" ghost :render-icon="renderIcon(DeleteFilled)" @click="confirmDeleteByQuery">
              {{ t('docs.deleteByQuery') }}
            </n-button>
          </n-flex>

          <n-spin :show="loading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="docColumns"
                :data="docs"
                :max-height="480"
                size="small"
                striped
            />
          </n-spin>

          <n-flex align="center">
            <n-button size="small" :disabled="from <= 0" @click="prevPage">{{ t('docs.prevPage') }}</n-button>
            <n-text>{{ t('docs.pageInfo', {from: total === 0 ? 0 : from + 1, to: from + docs.length, total}) }}</n-text>
            <n-button size="small" :disabled="from + pageSize >= total || docs.length === 0" @click="nextPage">
              {{ t('docs.nextPage') }}
            </n-button>
            <n-select v-model:value="pageSize" :options="pageSizeOptions" style="width: 100px" size="small"
                      @update:value="resetBrowse"/>
          </n-flex>
        </n-flex>
      </n-tab-pane>

      <!-- ============ 字段统计 ============ -->
      <n-tab-pane name="fieldStats" :tab="t('docs.tabFieldStats')">
        <n-flex vertical>
          <n-flex align="center">
            <n-select
                v-model:value="statsIndex"
                :options="indexOptions"
                :loading="indexLoading"
                filterable
                clearable
                :placeholder="t('docs.selectIndex')"
                style="width: 260px; min-width: 240px; flex-shrink: 0;"
            />
            <n-tooltip trigger="hover">
              <template #trigger>
                <n-button :loading="indexLoading" :render-icon="renderIcon(RefreshOutlined)" @click="loadIndexes" />
              </template>
              {{ t('docs.refreshIndexes') }}
            </n-tooltip>
            <n-input v-model:value="statsField" :placeholder="t('docs.fieldName')" style="width: 220px; flex-shrink: 0;"
                     @keydown.enter="queryFieldStats"/>
            <n-input-number v-model:value="statsSize" :min="1" :max="1000" style="width: 140px; flex-shrink: 0;"/>
            <n-button :loading="statsLoading" :render-icon="renderIcon(SearchFilled)" @click="queryFieldStats">
              {{ t('common.search') }}
            </n-button>
          </n-flex>
          <n-text v-if="cardinality !== null">{{ t('docs.cardinality', {count: formatNumber(cardinality)}) }}</n-text>
          <n-spin :show="statsLoading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="statsColumns"
                :data="statsData"
                :max-height="480"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>
      </n-tab-pane>

      <!-- ============ 导入 ============ -->
      <n-tab-pane name="import" :tab="t('docs.tabImport')">
        <n-flex vertical>
          <n-flex align="center">
            <n-select
                v-model:value="importIndex"
                :options="indexOptions"
                :loading="indexLoading"
                filterable
                clearable
                :placeholder="t('docs.selectIndex')"
                style="width: 260px; min-width: 240px; flex-shrink: 0;"
            />
            <n-tooltip trigger="hover">
              <template #trigger>
                <n-button :loading="indexLoading" :render-icon="renderIcon(RefreshOutlined)" @click="loadIndexes" />
              </template>
              {{ t('docs.refreshIndexes') }}
            </n-tooltip>
            <n-radio-group v-model:value="importFormat">
              <n-radio-button value="json">JSON</n-radio-button>
              <n-radio-button value="csv">CSV</n-radio-button>
            </n-radio-group>
            <input
                ref="fileInput"
                type="file"
                accept=".json,.csv,.txt"
                style="display: none;"
                @change="handleFileSelect"
            />
            <n-button :render-icon="renderIcon(DriveFileMoveTwotone)" @click="fileInput?.click()">
              {{ t('docs.selectFile') }}
            </n-button>
            <n-button quaternary @click="fillSampleData">
              {{ t('docs.fillSample') }}
            </n-button>
            <n-button quaternary @click="importData = ''">
              {{ t('docs.clear') }}
            </n-button>
          </n-flex>
          <n-flex align="center" justify="space-between">
            <n-text depth="3">{{ importFormat === 'csv' ? t('docs.csvHint') : t('docs.jsonHint') }}</n-text>
            <n-tag v-if="parsedDocCount > 0" type="success" size="small" round>
              {{ t('docs.recordsReady', { count: parsedDocCount }) }}
            </n-tag>
            <n-tag v-else-if="importData.trim() && parseErrorMessage" type="error" size="small" round>
              {{ parseErrorMessage }}
            </n-tag>
          </n-flex>
          <n-input
              v-model:value="importData"
              type="textarea"
              :autosize="{minRows: 12, maxRows: 24}"
              :placeholder="importFormat === 'csv' ? t('docs.csvPlaceholder') : t('docs.jsonPlaceholder')"
              class="json-editor-input"
              style="min-height: 260px;"
          />
          <n-flex align="center">
            <n-button
                type="primary"
                :loading="importLoading"
                :disabled="!importIndex || !importData.trim()"
                :render-icon="renderIcon(UploadFilled)"
                @click="importDocs"
            >
              {{ t('docs.startImport') }}
            </n-button>
            <n-text depth="3" v-if="!importIndex">
              {{ t('docs.selectIndexFirst') }}
            </n-text>
          </n-flex>
        </n-flex>
      </n-tab-pane>
    </n-tabs>

    <!-- 查看/编辑文档 -->
    <n-modal v-model:show="docDetail.show" preset="card" :title="docDetail.title" style="width: 680px; max-width: 90vw; text-align: left;">
      <template v-if="!docDetail.editing">
        <n-scrollbar style="max-height: 65vh;">
          <n-code :code="docDetail.content" language="json" show-line-numbers word-wrap style="text-align: left;"/>
        </n-scrollbar>
        <n-flex justify="end" style="margin-top: 12px;">
          <n-button @click="docDetail.show = false">{{ t('common.close') }}</n-button>
        </n-flex>
      </template>
      <template v-else>
        <n-input v-model:value="docDetail.content" type="textarea" :autosize="{minRows: 10, maxRows: 22}"
                 class="json-editor-input"/>
        <n-flex justify="end" style="margin-top: 12px;">
          <n-button @click="docDetail.show = false">{{ t('common.cancel') }}</n-button>
          <n-button type="primary" :loading="docDetail.saving" @click="saveDoc">{{ t('common.save') }}</n-button>
        </n-flex>
      </template>
    </n-modal>

    <!-- 添加文档 -->
    <n-modal v-model:show="addDoc.show" preset="card" :title="t('docs.addDoc')" style="width: 640px; text-align: left;">
      <n-input v-model:value="addDoc.doc" type="textarea" :autosize="{minRows: 10, maxRows: 22}"
               :placeholder='JSON.stringify({"field1": "value1"}, null, 2)' class="json-editor-input"/>
      <n-flex justify="end" style="margin-top: 12px;">
        <n-button @click="addDoc.show = false">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" :loading="addDoc.saving" @click="submitAddDoc">{{ t('common.save') }}</n-button>
      </n-flex>
    </n-modal>
  </n-flex>
</template>

<script setup>
import {useI18n} from 'vue-i18n'
import {computed, h, onActivated, onMounted, onUnmounted, ref, watch} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDropdown, NIcon, NRadioButton, NRadioGroup, NTag, NTooltip, useDialog, useMessage} from 'naive-ui'
import {formatNumber, isValidJson, refColumns, renderIcon} from "../utils/common";
import {
  AddFilled, DeleteFilled, DriveFileMoveTwotone, MoreVertFilled, RefreshOutlined, SearchFilled, UploadFilled
} from "@vicons/material";
import {
  AddDocument,
  BulkImport,
  DeleteByQuery,
  DeleteDoc,
  GetDoc,
  GetFieldTopValues,
  GetIndexes,
  SearchDocs,
  UpdateDoc,
} from "../../wailsjs/go/service/ESService";

const {t} = useI18n()
const message = useMessage()
const dialog = useDialog()

const activeTab = ref('browse')

// ==================== 索引下拉 ====================
const loadCachedIndexes = () => {
  try {
    const raw = localStorage.getItem('es_king_indexes')
    if (raw) {
      const arr = JSON.parse(raw)
      if (Array.isArray(arr) && arr.length > 0) {
        return arr.map(idx => ({label: idx, value: idx}))
      }
    }
  } catch (e) {}
  return []
}

const indexOptions = ref(loadCachedIndexes())
const indexLoading = ref(false)

const loadIndexes = async () => {
  indexLoading.value = true
  try {
    const res = await GetIndexes("")
    if (res.err !== "") {
      message.error(res.err)
      return
    }
    const idxs = (res.results || []).map(item => item.index).filter(Boolean)
    indexOptions.value = idxs.map(idx => ({label: idx, value: idx}))
    try {
      const key = 'es_king_indexes'
      const stored = localStorage.getItem(key)
      let values = stored ? JSON.parse(stored) : []
      for (const v of idxs) {
        if (!values.includes(v)) {
          values.push(v)
        }
      }
      localStorage.setItem(key, JSON.stringify(values.slice(-1000)))
    } catch (e) {}
  } catch (e) {
    message.error(e.message)
  } finally {
    indexLoading.value = false
  }
}

// ==================== 文档浏览 ====================
const browseIndex = ref(null)
const queryDsl = ref("")
const docs = ref([])
const total = ref(0)
const from = ref(0)
const pageSize = ref(10)
const loading = ref(false)

const pageSizeOptions = [10, 20, 50, 100].map(v => ({label: String(v), value: v}))

const resetBrowse = () => {
  from.value = 0
  docs.value = []
  total.value = 0
  if (browseIndex.value) {
    searchDocs()
  }
}

const prevPage = () => {
  from.value = Math.max(0, from.value - pageSize.value)
  searchDocs()
}

const nextPage = () => {
  from.value = from.value + pageSize.value
  searchDocs()
}

// 新搜索从第一页开始，翻页保留偏移量
const newSearch = () => {
  from.value = 0
  searchDocs()
}

const searchDocs = async () => {
  if (!browseIndex.value) {
    message.warning(t('docs.selectIndexFirst'))
    return
  }
  if (queryDsl.value && !isValidJson(queryDsl.value)) {
    message.error(t('docs.invalidQuery'))
    return
  }
  loading.value = true
  try {
    const res = await SearchDocs(browseIndex.value, queryDsl.value, from.value, pageSize.value)
    if (res.err !== "") {
      message.error(res.err)
      return
    }
    const result = res.result || {}
    docs.value = (result.hits && result.hits.hits) || []
    total.value = (result.hits && result.hits.total && result.hits.total.value) || 0
  } catch (e) {
    message.error(e.message)
  } finally {
    loading.value = false
  }
}

const renderCellValue = (value) => {
  if (value === null || value === undefined) return ''
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

// 动态列：取所有文档 _source 顶层字段并集
const docColumns = computed(() => {
  const keyCount = {}
  for (const hit of docs.value) {
    const source = hit._source || {}
    for (const key of Object.keys(source)) {
      keyCount[key] = (keyCount[key] || 0) + 1
    }
  }
  const keys = Object.keys(keyCount)
      .sort((a, b) => keyCount[b] - keyCount[a] || a.localeCompare(b))
      .slice(0, 15)
  const cols = [
    {
      title: '_id',
      key: '_id',
      width: 160,
      render: (row) => h(NTag, {size: 'small', type: 'info'}, {default: () => row._id}),
    },
    ...keys.map(key => ({
      title: key,
      key: `source.${key}`,
      render: (row) => renderCellValue((row._source || {})[key]),
    })),
  ]
  cols.push({
    title: t('common.operation'),
    key: 'actions',
    width: 90,
    render: (row) => h(
        NDropdown,
        {
          trigger: 'click',
          options: [
            {label: t('common.details'), key: 'view'},
            {label: t('common.edit'), key: 'edit'},
            {label: t('common.delete'), key: 'delete'},
          ],
          onSelect: (opKey) => handleDocAction(opKey, row),
        },
        {
          default: () => h(
              NButton,
              {strong: true, secondary: true, size: 'small'},
              {default: () => t('common.operation'), icon: () => h(NIcon, null, {default: () => h(MoreVertFilled)})}
          )
        }
    )
  })
  return refColumns(cols)
})

const docDetail = ref({
  show: false,
  title: '',
  content: '',
  editing: false,
  saving: false,
  docId: '',
})

const handleDocAction = async (opKey, row) => {
  if (opKey === 'view' || opKey === 'edit') {
    if (opKey === 'view') {
      const res = await GetDoc(browseIndex.value, row._id)
      if (res.err !== "") {
        message.error(res.err)
        return
      }
      docDetail.value = {
        show: true, editing: false, saving: false,
        title: `${browseIndex.value} / ${row._id}`,
        content: JSON.stringify(res.result, null, 2),
        docId: row._id,
      }
    } else {
      docDetail.value = {
        show: true, editing: true, saving: false,
        title: `${browseIndex.value} / ${row._id}`,
        content: JSON.stringify(row._source || {}, null, 2),
        docId: row._id,
      }
    }
  } else if (opKey === 'delete') {
    dialog.warning({
      title: t('common.warning'),
      content: t('docs.confirmDeleteDoc', {id: row._id}),
      positiveText: t('common.confirm'),
      negativeText: t('common.cancel'),
      onPositiveClick: async () => {
        const res = await DeleteDoc(browseIndex.value, row._id)
        if (res.err !== "") {
          message.error(res.err)
        } else {
          message.success(t('docs.docDeleted', {id: row._id}))
          await searchDocs()
        }
      }
    })
  }
}

const saveDoc = async () => {
  if (!isValidJson(docDetail.value.content)) {
    message.error(t('docs.invalidDocJson'))
    return
  }
  docDetail.value.saving = true
  try {
    const res = await UpdateDoc(browseIndex.value, docDetail.value.docId, docDetail.value.content)
    if (res.err !== "") {
      message.error(res.err)
    } else {
      message.success(t('docs.docUpdated'))
      docDetail.value.show = false
      await searchDocs()
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    docDetail.value.saving = false
  }
}

const addDoc = ref({
  show: false,
  doc: '',
  saving: false,
})

const openAddDoc = () => {
  if (!browseIndex.value) {
    message.warning(t('docs.selectIndexFirst'))
    return
  }
  addDoc.value.show = true
}

const submitAddDoc = async () => {
  if (!isValidJson(addDoc.value.doc)) {
    message.error(t('docs.invalidDocJson'))
    return
  }
  addDoc.value.saving = true
  try {
    const res = await AddDocument(browseIndex.value, addDoc.value.doc)
    if (res.err !== "") {
      message.error(res.err)
    } else {
      message.success(t('index.docAdded', {id: res.result['_id']}))
      addDoc.value.show = false
      addDoc.value.doc = ''
      await searchDocs()
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    addDoc.value.saving = false
  }
}

const confirmDeleteByQuery = () => {
  if (!browseIndex.value) {
    message.warning(t('docs.selectIndexFirst'))
    return
  }
  if (!queryDsl.value) {
    message.warning(t('docs.deleteByQueryNeedQuery'))
    return
  }
  dialog.error({
    title: t('common.warning'),
    content: t('docs.confirmDeleteByQuery', {index: browseIndex.value}),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      const res = await DeleteByQuery(browseIndex.value, queryDsl.value)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success(t('docs.deleteByQuerySubmitted'))
      }
    }
  })
}

// ==================== 字段统计 ====================
const statsIndex = ref(null)
const statsField = ref("")
const statsSize = ref(10)
const statsData = ref([])
const statsLoading = ref(false)
const cardinality = ref(null)

const statsColumns = computed(() => refColumns([
  {title: t('docs.colValue'), key: 'key'},
  {
    title: t('docs.colDocCount'), key: 'doc_count',
    sorter: (a, b) => a.doc_count - b.doc_count,
  },
]))

const queryFieldStats = async () => {
  if (!statsIndex.value) {
    message.warning(t('docs.selectIndexFirst'))
    return
  }
  if (!statsField.value) {
    message.warning(t('docs.inputFieldFirst'))
    return
  }
  statsLoading.value = true
  cardinality.value = null
  try {
    const res = await GetFieldTopValues(statsIndex.value, statsField.value, statsSize.value)
    if (res.err !== "") {
      message.error(res.err)
      return
    }
    const aggs = (res.result && res.result.aggregations) || {}
    const buckets = (aggs.top_values && aggs.top_values.buckets) || []
    statsData.value = buckets.map(b => ({
      key: typeof b.key === 'object' ? JSON.stringify(b.key) : String(b.key),
      doc_count: b.doc_count,
    }))
    if (aggs.unique_count) {
      cardinality.value = aggs.unique_count.value
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    statsLoading.value = false
  }
}

// ==================== 导入 ====================
const importIndex = ref(null)
const importFormat = ref('json')
const importData = ref("")
const importLoading = ref(false)
const fileInput = ref(null)

const handleFileSelect = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  const isCsv = file.name.toLowerCase().endsWith('.csv')
  const reader = new FileReader()
  reader.onload = (event) => {
    importData.value = event.target?.result || ''
    if (isCsv) {
      importFormat.value = 'csv'
    } else if (file.name.toLowerCase().endsWith('.json')) {
      importFormat.value = 'json'
    }
    message.success(t('docs.fileLoaded', { name: file.name }))
  }
  reader.onerror = () => {
    message.error(t('docs.fileReadError'))
  }
  reader.readAsText(file)
  e.target.value = ''
}

const fillSampleData = () => {
  if (importFormat.value === 'csv') {
    importData.value = `title,category,views,publish_date
Elasticsearch Guide,database,1500,2026-01-15
Naive UI Tutorial,frontend,820,2026-02-20
Go Wails Desktop App,golang,2300,2026-03-01`
  } else {
    importData.value = JSON.stringify([
      {
        "title": "Elasticsearch Guide",
        "category": "database",
        "views": 1500,
        "publish_date": "2026-01-15"
      },
      {
        "title": "Naive UI Tutorial",
        "category": "frontend",
        "views": 820,
        "publish_date": "2026-02-20"
      },
      {
        "title": "Go Wails Desktop App",
        "category": "golang",
        "views": 2300,
        "publish_date": "2026-03-01"
      }
    ], null, 2)
  }
}

// 简易 CSV 解析：支持双引号转义（引号内可含逗号/换行）
const parseCsv = (text) => {
  const rows = []
  let row = []
  let field = ''
  let inQuotes = false
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]
    if (inQuotes) {
      if (ch === '"') {
        if (text[i + 1] === '"') {
          field += '"'
          i++
        } else {
          inQuotes = false
        }
      } else {
        field += ch
      }
    } else if (ch === '"') {
      inQuotes = true
    } else if (ch === ',') {
      row.push(field)
      field = ''
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++
      row.push(field)
      field = ''
      if (row.some(v => v !== '')) rows.push(row)
      row = []
    } else {
      field += ch
    }
  }
  row.push(field)
  if (row.some(v => v !== '')) rows.push(row)
  return rows
}

const csvToDocs = (text) => {
  const rows = parseCsv(text.trim())
  if (rows.length < 2) {
    throw new Error(t('docs.csvNeedHeader'))
  }
  const headers = rows[0].map(h => h.trim())
  return rows.slice(1).map(row => {
    const doc = {}
    headers.forEach((h, i) => {
      if (h !== "") {
        doc[h] = row[i] ?? ''
      }
    })
    return doc
  })
}

const parsedDocCount = computed(() => {
  const raw = importData.value.trim()
  if (!raw) return 0
  if (importFormat.value === 'json') {
    try {
      const parsed = JSON.parse(raw)
      return Array.isArray(parsed) ? parsed.length : 0
    } catch {
      return 0
    }
  } else {
    try {
      const rows = parseCsv(raw)
      return rows.length > 1 ? rows.length - 1 : 0
    } catch {
      return 0
    }
  }
})

const parseErrorMessage = computed(() => {
  const raw = importData.value.trim()
  if (!raw) return ''
  if (importFormat.value === 'json') {
    try {
      const parsed = JSON.parse(raw)
      if (!Array.isArray(parsed)) {
        return t('docs.needJsonArray')
      }
      return ''
    } catch (e) {
      return e.message
    }
  } else {
    try {
      const rows = parseCsv(raw)
      if (rows.length < 2) {
        return t('docs.csvNeedHeader')
      }
      return ''
    } catch (e) {
      return e.message
    }
  }
})

const importDocs = async () => {
  if (!importIndex.value) {
    message.warning(t('docs.selectIndexFirst'))
    return
  }
  let docsArray
  try {
    if (importFormat.value === 'csv') {
      docsArray = csvToDocs(importData.value)
    } else {
      docsArray = JSON.parse(importData.value)
      if (!Array.isArray(docsArray)) {
        message.error(t('docs.needJsonArray'))
        return
      }
    }
  } catch (e) {
    message.error(t('docs.parseFailed', {msg: e.message}))
    return
  }
  importLoading.value = true
  try {
    const res = await BulkImport(importIndex.value, JSON.stringify(docsArray))
    if (res.err !== "") {
      message.error(res.err)
      return
    }
    const summary = res.result || {}
    if (summary.failed > 0) {
      message.warning(t('docs.importPartial', {success: summary.success, failed: summary.failed, msg: summary.first_error || ''}))
    } else {
      message.success(t('docs.importSuccess', {count: summary.total}))
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    importLoading.value = false
  }
}

const openImportTab = () => {
  if (browseIndex.value) {
    importIndex.value = browseIndex.value
  } else if (!importIndex.value && indexOptions.value.length > 0) {
    importIndex.value = indexOptions.value[0].value
  }
  activeTab.value = 'import'
}

watch(activeTab, (tab) => {
  if (tab === 'import') {
    if (!importIndex.value) {
      importIndex.value = browseIndex.value || (indexOptions.value[0]?.value ?? null)
    }
  }
  if (tab === 'fieldStats') {
    if (!statsIndex.value) {
      statsIndex.value = browseIndex.value || (indexOptions.value[0]?.value ?? null)
    }
  }
})

// ==================== 生命周期 ====================
const selectNode = async () => {
  docs.value = []
  total.value = 0
  browseIndex.value = null
  statsIndex.value = null
  importIndex.value = null
  await loadIndexes()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  loadIndexes()
})

onActivated(() => {
  if (indexOptions.value.length === 0) {
    loadIndexes()
  }
})

onUnmounted(() => {
  emitter.off('selectNode', selectNode)
})
</script>

<style scoped>
.json-editor-input :deep(textarea) {
  text-align: left !important;
  font-family: Consolas, Monaco, monospace;
}
</style>

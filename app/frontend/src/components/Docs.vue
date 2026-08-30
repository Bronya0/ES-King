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

    <n-tabs type="line" animated v-model:value="activeTab">
      <!-- ============ 文档浏览 ============ -->
      <n-tab-pane name="browse" :tab="t('docs.tabBrowse')">
        <n-flex vertical>
          <n-flex align="center">
            <n-select
                v-model:value="browseIndex"
                :options="indexOptions"
                filterable
                :placeholder="t('docs.selectIndex')"
                style="min-width: 220px"
                @update:value="resetBrowse"
            />
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="loadIndexes"></n-button>
          </n-flex>
          <n-flex align="center">
            <n-input
                v-model:value="queryDsl"
                type="textarea"
                :autosize="{minRows: 1, maxRows: 6}"
                :placeholder='t("docs.queryPlaceholder")'
                style="min-width: 40%"
                @keydown.enter="newSearch"
            />
            <n-button :loading="loading" :render-icon="renderIcon(SearchFilled)" @click="newSearch">
              {{ t('common.search') }}
            </n-button>
            <n-button :render-icon="renderIcon(AddFilled)" @click="openAddDoc">{{ t('docs.addDoc') }}</n-button>
            <n-button :render-icon="renderIcon(DriveFileMoveTwotone)" @click="activeTab = 'import'">
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
                filterable
                :placeholder="t('docs.selectIndex')"
                style="min-width: 220px"
            />
            <n-input v-model:value="statsField" :placeholder="t('docs.fieldName')" style="width: 220px"
                     @keydown.enter="queryFieldStats"/>
            <n-input-number v-model:value="statsSize" :min="1" :max="1000" style="width: 140px"/>
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
                filterable
                :placeholder="t('docs.selectIndex')"
                style="min-width: 220px"
            />
            <n-radio-group v-model:value="importFormat">
              <n-radio value="json">JSON</n-radio>
              <n-radio value="csv">CSV</n-radio>
            </n-radio-group>
          </n-flex>
          <n-text depth="3">{{ importFormat === 'csv' ? t('docs.csvHint') : t('docs.jsonHint') }}</n-text>
          <n-input
              v-model:value="importData"
              type="textarea"
              :autosize="{minRows: 10, maxRows: 18}"
              :placeholder="importFormat === 'csv' ? t('docs.csvPlaceholder') : t('docs.jsonPlaceholder')"
          />
          <n-flex>
            <n-button type="primary" :loading="importLoading" :render-icon="renderIcon(UploadFilled)"
                      @click="importDocs">
              {{ t('docs.startImport') }}
            </n-button>
          </n-flex>
        </n-flex>
      </n-tab-pane>
    </n-tabs>

    <!-- 查看/编辑文档 -->
    <n-modal v-model:show="docDetail.show" preset="card" :title="docDetail.title" style="width: 640px;">
      <n-code v-if="!docDetail.editing" :code="docDetail.content" language="json" show-line-numbers/>
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
    <n-modal v-model:show="addDoc.show" preset="card" :title="t('docs.addDoc')" style="width: 640px;">
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
import {computed, h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDropdown, NIcon, NTag, useDialog, useMessage} from 'naive-ui'
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
const indexOptions = ref([])

const loadIndexes = async () => {
  const res = await GetIndexes("")
  if (res.err !== "") {
    return
  }
  indexOptions.value = (res.results || []).map(item => ({label: item.index, value: item.index}))
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

// ==================== 生命周期 ====================
const selectNode = () => {
  indexOptions.value = []
  docs.value = []
  total.value = 0
  browseIndex.value = null
  statsIndex.value = null
  importIndex.value = null
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  loadIndexes()
})
</script>

<style scoped>
.json-editor-input :deep(textarea) {
  font-family: Consolas, Monaco, monospace;
}
</style>

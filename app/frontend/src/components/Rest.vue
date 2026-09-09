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
      <h2>{{ t('rest.title') }}</h2>
      <n-text>{{ t('rest.desc') }}</n-text>
    </n-flex>

    <!-- 查询Tab -->
    <n-tabs
        v-model:value="activeTabId"
        type="editable-card"
        size="small"
        addable
        :closable="tabs.length > 1"
        @update:value="handleTabSwitch"
        @add="addTab"
        @close="closeTab"
    >
      <n-tab-pane v-for="tab in tabs" :key="tab.id" :name="tab.id" :tab="tab.label"/>
    </n-tabs>

    <n-flex align="center">
      <n-select v-model:value="method" :options="methodOptions" style="width: 120px;"/>

      <n-auto-complete
          v-model:value="urlPath"
          :options="urlCompletions"
          :placeholder="t('rest.enterApi')"
          clearable
          style="min-width: 320px; flex: 1;"
          @update:value="handleUrlInput"
          @keydown.enter="sendRequest"
      />

      <n-button :loading="send_loading" :render-icon="renderIcon(SendSharp)" @click="sendRequest">{{ t('rest.send') }}</n-button>
      <n-button :render-icon="renderIcon(HistoryOutlined)" @click="showHistoryDrawer = true">{{ t('rest.history') }}</n-button>
      <n-button :render-icon="renderIcon(MenuBookTwotone)" @click="showDrawer = true">{{ t('rest.examples') }}</n-button>
      <n-button :render-icon="renderIcon(StarOutlined)" @click="openSaveFavorite">{{ t('rest.saveFavorite') }}</n-button>
      <n-button :render-icon="renderIcon(BookmarksFilled)" @click="showFavoriteDrawer = true">{{ t('rest.favorites') }}</n-button>
      <n-button :render-icon="renderIcon(TableRowsOutlined)" :type="showTableView ? 'primary' : 'default'"
                @click="showTableView = !showTableView">{{ t('rest.tableView') }}
      </n-button>
      <n-button :render-icon="renderIcon(ArrowDownwardOutlined)" @click="exportJson">{{ t('rest.exportResult') }}</n-button>
    </n-flex>
    <n-grid :cols="2" x-gap="20">
      <n-grid-item>
        <div id="json_editor" class="editarea"
             style="white-space: pre-wrap; white-space-collapse: preserve; border: 0 !important;"
             @paste="toTree"></div>
      </n-grid-item>
      <n-grid-item>
        <div v-show="!showTableView" id="json_view" class="editarea"></div>
        <div v-show="showTableView" class="editarea">
          <n-data-table
              :bordered="false"
              :columns="tableColumns"
              :data="tableData"
              :max-height="620"
              virtual-scroll
              size="small"
              striped
          />
        </div>
      </n-grid-item>
    </n-grid>
  </n-flex>

  <n-drawer v-model:show="showDrawer" placement="right" style="width: 38.2%">
    <n-drawer-content style="text-align: left;" :title="t('rest.queryExamples')">
      <n-flex vertical>
        <n-collapse>
          <n-collapse-item v-for="(example, idx) in exampleList" :key="example.key" :name="String(idx + 1)">
            <template #header>
              <n-flex align="center" justify="space-between">
                <span>{{ idx + 1 }}. {{ example.title }}</span>
                <n-button size="tiny" type="primary" secondary @click.stop="insertExample(example.code)">
                  {{ t('rest.insert') }}
                </n-button>
              </n-flex>
            </template>
            <n-code :code="example.code" language="json" word-wrap style="text-align: left;"/>
          </n-collapse-item>
        </n-collapse>
      </n-flex>
    </n-drawer-content>
  </n-drawer>

  <!-- 历史记录抽屉 -->
  <n-drawer v-model:show="showHistoryDrawer" style="width: 38.2%">
    <n-drawer-content :title="t('rest.history')">
      <n-input
          v-model:value="searchText"
          clearable
          :placeholder="t('rest.searchHistory')"
          style="margin-bottom: 12px"
      >
        <template #prefix>
          <n-icon>
            <SearchFilled/>
          </n-icon>
        </template>
      </n-input>

      <n-list>
        <n-pagination
            v-model:page="currentPage"
            :item-count="filteredHistory?.length"
            :page-size="pageSize"
        />

        <n-list-item v-for="item in currentPageData" :key="item.timestamp"
                     style="cursor: pointer;" @click="handleHistoryClick(item.method, item.path, item.dsl)">
          <n-tooltip placement="left" style="max-height: 618px;overflow-y: auto" trigger="hover">
            <template #trigger>
              <div style="display: flex;font-size: 14px; justify-content: space-between;">
                <n-tag :type="getMethodTagType(item.method)">
                  {{ item.method }}
                </n-tag>
                <n-text>{{ item.path }}</n-text>
                <n-text depth="3">
                  {{ formatTimestamp(item.timestamp) }}
                </n-text>
              </div>
            </template>
            <n-code v-if="item.dsl !== ''" :code="formatDSL(item.dsl)" language="json" word-wrap style="text-align: left;"/>

          </n-tooltip>
        </n-list-item>

      </n-list>
    </n-drawer-content>
  </n-drawer>

  <!-- 收藏查询抽屉 -->
  <n-drawer v-model:show="showFavoriteDrawer" style="width: 38.2%">
    <n-drawer-content :title="t('rest.favorites')">
      <n-empty v-if="favorites.length === 0" :description="t('rest.noFavorites')"/>
      <n-list v-else>
        <n-list-item v-for="(item, idx) in favorites" :key="idx">
          <n-flex vertical>
            <n-flex align="center" justify="space-between">
              <n-tag :type="getMethodTagType(item.method)" size="small">{{ item.method }}</n-tag>
              <n-text>{{ item.name }}</n-text>
              <n-flex>
                <n-button size="small" quaternary type="info" @click="applyFavorite(item)">{{ t('rest.apply') }}</n-button>
                <n-button size="small" quaternary type="error" @click="removeFavorite(idx)">{{ t('common.delete') }}</n-button>
              </n-flex>
            </n-flex>
            <n-text depth="3" style="font-size: 12px;">{{ item.path }}</n-text>
          </n-flex>
        </n-list-item>
      </n-list>
    </n-drawer-content>
  </n-drawer>

  <!-- 保存收藏弹窗 -->
  <n-modal v-model:show="saveFavoriteModal.show" preset="card" :title="t('rest.saveFavorite')" style="width: 460px; text-align: left;">
    <n-input v-model:value="saveFavoriteModal.name" :placeholder="t('rest.favoriteName')" @keydown.enter="confirmSaveFavorite"/>
    <template #footer>
      <n-flex justify="end">
        <n-button @click="saveFavoriteModal.show = false">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" @click="confirmSaveFavorite">{{ t('common.save') }}</n-button>
      </n-flex>
    </template>
  </n-modal>
</template>

<script setup>

import { useI18n } from 'vue-i18n'
import {NGrid, NGridItem, NInput, NSelect, useMessage} from 'naive-ui'
import {computed, nextTick, onMounted, ref} from "vue";
import {Search} from "../../wailsjs/go/service/ESService";
import {
  ArrowDownwardOutlined, BookmarksFilled, HistoryOutlined, MenuBookTwotone, SearchFilled, SendSharp,
  StarOutlined, TableRowsOutlined
} from "@vicons/material";
import {flattenObject, formatTimestamp, renderIcon} from "../utils/common";
import {GetConfig, GetHistory, SaveHistory} from "../../wailsjs/go/config/AppConfig";
import emitter from "../utils/eventBus";

import JSONEditor from 'jsoneditor';
import '../assets/css/jsoneditor.min.css'
import 'jsoneditor/src/js/ace/theme-jsoneditor';
import 'ace-builds/src-noconflict/mode-text'
import 'ace-builds/src-noconflict/ext-language_tools'
import 'ace-builds/src-noconflict/theme-textmate'
import 'ace-builds/src-noconflict/theme-monokai'
import ace from 'ace-builds';

const { t } = useI18n()

const message = useMessage()
const method = ref('POST')
const searchText = ref('')
const history = ref([])
const editor = ref()
const response = ref()
const send_loading = ref(false)
const showDrawer = ref(false)
const showHistoryDrawer = ref(false)
const showFavoriteDrawer = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const showTableView = ref(false)
const lastResponseText = ref('')

// ==================== 多Tab ====================
let tabSeq = 1
const tabs = ref([{id: 1, label: 'Tab 1', method: 'POST', path: '', dsl: '', response: ''}])
const activeTabId = ref(1)
const urlPath = ref('')

const defaultEndpoints = [
  '_search', '_cluster/health', '_cluster/state', '_cluster/stats',
  '_cat/indices', '_cat/nodes', '_cat/shards', '_cat/allocation',
  '_cat/count', '_cat/health', '_nodes/stats', '_tasks', '_flush',
  '_refresh', '_mapping', '_settings', '_stats', '_bulk', '_update',
  '_msearch', '_aliases', '_rollover', '_reindex', '_forcemerge',
  '_count', '_analyze'
]

const urlCompletions = computed(() => {
  const cur = (urlPath.value || '').trim()
  let list = [...defaultEndpoints]
  try {
    const stored = localStorage.getItem('es_king_indexes')
    if (stored) {
      const idxList = JSON.parse(stored)
      for (const idx of idxList) {
        list.push(idx)
        list.push(`${idx}/_search`)
        list.push(`${idx}/_mapping`)
        list.push(`${idx}/_settings`)
        list.push(`${idx}/_count`)
      }
    }
  } catch (e) {}

  if (!cur) {
    return list.slice(0, 20).map(v => {
      const val = '/' + v.replace(/^\//, '')
      return {label: val, value: val}
    })
  }

  const query = cur.replace(/^\//, '').toLowerCase()
  const matched = list.filter(item => item.toLowerCase().includes(query))
  return matched.slice(0, 25).map(v => {
    const val = cur.startsWith('/') ? '/' + v.replace(/^\//, '') : v
    return {label: val, value: val}
  })
})

const handleUrlInput = (val) => {
  urlPath.value = val
  const tab = tabs.value.find(item => item.id === activeTabId.value)
  if (tab) {
    tab.path = val
    if (val && val.trim()) {
      tab.label = val.trim().split('?')[0].slice(0, 18)
    } else {
      tab.label = `Tab ${tab.id}`
    }
  }
}

const addTab = () => {
  persistToTab(activeTabId.value)
  tabSeq += 1
  tabs.value.push({
    id: tabSeq,
    label: `Tab ${tabSeq}`,
    method: 'POST',
    path: '',
    dsl: '',
    response: '',
  })
  handleTabSwitch(tabSeq)
}

const closeTab = (tabId) => {
  const idx = tabs.value.findIndex(item => item.id === tabId)
  if (idx === -1) return
  tabs.value.splice(idx, 1)
  if (tabs.value.length === 0) {
    tabSeq = 1
    tabs.value.push({
      id: 1,
      label: 'Tab 1',
      method: 'POST',
      path: '',
      dsl: '',
      response: '',
    })
    handleTabSwitch(1)
    return
  }
  if (activeTabId.value === tabId) {
    const next = tabs.value[Math.min(idx, tabs.value.length - 1)]
    handleTabSwitch(next.id)
  }
}

const handleTabSwitch = (tabId) => {
  if (tabId === activeTabId.value) return
  persistToTab(activeTabId.value)
  activeTabId.value = tabId
  const tab = tabs.value.find(item => item.id === tabId)
  if (!tab) return
  method.value = tab.method || 'POST'
  urlPath.value = tab.path || ''
  if (editor.value) {
    editor.value.setText(tab.dsl || '')
  }
  if (response.value) {
    if (tab.response) {
      try {
        response.value.set(JSON.parse(tab.response))
      } catch {
        response.value.setText(tab.response)
      }
    } else {
      response.value.setText(t('rest.responseResult'))
    }
  }
  lastResponseText.value = tab.response || ''
}

// 把当前编辑器内容保存进对应tab
const persistToTab = (tabId) => {
  const tab = tabs.value.find(item => item.id === tabId)
  if (!tab) return
  tab.method = method.value
  tab.path = urlPath.value || ''
  tab.dsl = editor.value ? editor.value.getText() : (tab.dsl || '')
  tab.response = lastResponseText.value || ''
}

// ==================== 收藏查询 ====================
const FAVORITE_KEY = 'es_king_saved_queries'
const favorites = ref([])

const readFavorites = () => {
  try {
    favorites.value = JSON.parse(localStorage.getItem(FAVORITE_KEY)) || []
  } catch {
    favorites.value = []
  }
}

const writeFavorites = () => {
  localStorage.setItem(FAVORITE_KEY, JSON.stringify(favorites.value))
}

const saveFavoriteModal = ref({
  show: false,
  name: '',
})

const openSaveFavorite = () => {
  saveFavoriteModal.value = {show: true, name: ''}
}

const confirmSaveFavorite = () => {
  const name = saveFavoriteModal.value.name?.trim()
  if (!name) {
    message.warning(t('rest.inputFavoriteName'))
    return
  }
  favorites.value.unshift({
    name,
    method: method.value,
    path: urlPath.value || '',
    dsl: editor.value?.getText() || '',
  })
  writeFavorites()
  saveFavoriteModal.value.show = false
  message.success(t('common.saveSuccess'))
}

const applyFavorite = (item) => {
  method.value = item.method
  handleUrlInput(item.path)
  editor.value?.setText(item.dsl)
  showFavoriteDrawer.value = false
}

const removeFavorite = (idx) => {
  favorites.value.splice(idx, 1)
  writeFavorites()
}

// ==================== 结果表格视图 ====================
const tableData = computed(() => {
  if (!showTableView.value || !lastResponseText.value) return []
  try {
    const parsed = JSON.parse(lastResponseText.value)
    const hits = parsed?.hits?.hits
    if (!Array.isArray(hits)) return []
    return hits.map(hit => ({
      _id: hit._id,
      _index: hit._index,
      ...flattenObject(hit._source || {}),
    }))
  } catch {
    return []
  }
})

const tableColumns = computed(() => {
  const keyCount = {}
  for (const row of tableData.value.slice(0, 50)) {
    for (const key of Object.keys(row)) {
      keyCount[key] = (keyCount[key] || 0) + 1
    }
  }
  return Object.keys(keyCount)
      .sort((a, b) => keyCount[b] - keyCount[a] || a.localeCompare(b))
      .slice(0, 20)
      .map(key => ({
        title: key,
        key,
        ellipsis: {tooltip: {scrollable: true}},
        render: (row) => {
          const value = row[key]
          if (value === null || value === undefined) return ''
          if (typeof value === 'object') return JSON.stringify(value)
          return String(value)
        },
      }))
})

const methodOptions = [
  {label: 'GET', value: 'GET'},
  {label: 'POST', value: 'POST'},
  {label: 'PUT', value: 'PUT'},
  {label: 'HEAD', value: 'HEAD'},
  {label: 'PATCH', value: 'PATCH'},
  {label: 'OPTIONS', value: 'OPTIONS'},
  {label: 'DELETE', value: 'DELETE'}
]
const keywords = [
  {word: 'query', meta: 'keyword'},
  {word: 'bool', meta: 'keyword'},
  {word: 'filter', meta: 'keyword'},
  {word: 'must', meta: 'keyword'},
  {word: 'should', meta: 'keyword'},
  {word: 'must_not', meta: 'keyword'},
  {word: 'term', meta: 'keyword'},
  {word: 'terms', meta: 'keyword'},
  {word: 'match', meta: 'keyword'},
  {word: 'match_phrase', meta: 'keyword'},
  {word: 'multi_match', meta: 'keyword'},
  {word: 'range', meta: 'keyword'},
  {word: 'exists', meta: 'keyword'},
  {word: 'prefix', meta: 'keyword'},
  {word: 'wildcard', meta: 'keyword'},
  {word: 'regexp', meta: 'keyword'},
  {word: 'aggs', meta: 'keyword'},
  {word: 'aggregations', meta: 'keyword'},
  {word: 'terms', meta: 'aggregation'},
  {word: 'sum', meta: 'aggregation'},
  {word: 'avg', meta: 'aggregation'},
  {word: 'min', meta: 'aggregation'},
  {word: 'max', meta: 'aggregation'},
  {word: 'stats', meta: 'aggregation'},
  {word: 'cardinality', meta: 'aggregation'},
  {word: 'histogram', meta: 'aggregation'},
  {word: 'date_histogram', meta: 'aggregation'},
  {word: 'top_hits', meta: 'aggregation'},
  {word: 'size', meta: 'keyword'},
  {word: 'from', meta: 'keyword'},
  {word: 'sort', meta: 'keyword'},
  {word: 'track_total_hits', meta: 'keyword'},
  {word: '_source', meta: 'keyword'},
  {word: 'fields', meta: 'keyword'},
  {word: 'script', meta: 'keyword'},
  {word: 'gte', meta: 'range'},
  {word: 'lte', meta: 'range'},
  {word: 'gt', meta: 'range'},
  {word: 'lt', meta: 'range'},
  {word: 'boost', meta: 'keyword'},
  {word: 'minimum_should_match', meta: 'keyword'},
  {word: 'nested', meta: 'keyword'},
  {word: 'path', meta: 'keyword'},
  {word: 'score_mode', meta: 'keyword'},
  {word: 'bucket', meta: 'aggregation'},
  {word: 'order', meta: 'keyword'},
  {word: 'asc', meta: 'sort'},
  {word: 'desc', meta: 'sort'}
];

const selectNode = (node) => {
  response.value.setText(t('rest.responseResult'))
  lastResponseText.value = ''
  send_loading.value = false
}

onMounted(async () => {

  emitter.on('selectNode', selectNode)
  emitter.on('update_theme', themeChange)
  readFavorites()

  const loadedConfig = await GetConfig()
  let theme = 'ace/theme/jsoneditor'
  if (loadedConfig) {
    if (loadedConfig.theme !== 'light') {
      theme = 'ace/theme/monokai'
    }
    editor.value = new JSONEditor(document.getElementById('json_editor'), {
      mode: 'code',
      ace: ace,
      theme: theme,
      mainMenuBar: false,
      statusBar: false,
      showPrintMargin: false,
      placeholder: t('rest.requestBody')
    });
    response.value = new JSONEditor(document.getElementById('json_view'), {
      mode: 'code',
      ace: ace,
      theme: theme,
      mainMenuBar: false,
      statusBar: false,
      showPrintMargin: false,
    });
    editor.value.setText(null)
    editor.value.aceEditor.setOptions({
      enableBasicAutocompletion: true,
      enableLiveAutocompletion: true
    })

    const customCompleter = {
      getCompletions: (editor, session, pos, prefix, callback) => {
        const suggestions = keywords
            .filter(k => k.word.startsWith(prefix))
            .map(k => ({
              caption: k.word,
              value: k.word,
              meta: k.meta
            }));
        callback(null, suggestions);
      }
    };

    editor.value.aceEditor.completers = [customCompleter];

    response.value.setText(t('rest.responseResult'))
  }
  await read_history()
});

const read_history = async () => {
  try {
    history.value = await GetHistory()
  } catch (e) {
    message.error(e.message)
  }
}

const write_history = async () => {
  try {
    history.value.unshift({
      timestamp: Date.now(),
      method: method.value,
      path: urlPath.value || '',
      dsl: editor.value ? editor.value.getText() : ''
    })
    if (history.value.length > 100) {
      history.value = history.value.slice(0, 100)
    }
    const res = await SaveHistory(history.value)
    if (res !== "") {
      message.error(t('rest.saveFailed', { msg: res }))
    }
  } catch (e) {
    message.error(e.message)
  }
}

function handleHistoryClick(m, p, d) {
  method.value = m
  handleUrlInput(p)
  editor.value?.setText(d)
  showHistoryDrawer.value = false
}

function themeChange(newTheme) {
  const new_editor_theme = newTheme.name === 'dark' ? 'ace/theme/monokai' : 'ace/theme/textmate'
  editor.value?.aceEditor?.setTheme(new_editor_theme)
  response.value?.aceEditor?.setTheme(new_editor_theme)
}

const formatDSL = (dsl) => {
  try {
    return JSON.stringify(JSON.parse(dsl), null, 2)
  } catch {
    return dsl
  }
}

const sendRequest = async () => {
  send_loading.value = true
  if (response.value) response.value.set({})
  let path = (urlPath.value || '').trim()
  if (path && !path.startsWith('/')) {
    path = '/' + path
    handleUrlInput(path)
  }
  try {
    const dsl = editor.value ? editor.value.getText() : ''
    const res = await Search(method.value, path, dsl)
    if (res.err !== "") {
      try {
        response.value.set(JSON.parse(res.err))
      } catch {
        response.value.set(res.err)
      }
      lastResponseText.value = ''
    } else {
      response.value.set(res.result)
      lastResponseText.value = JSON.stringify(res.result)
      await write_history()
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    persistToTab(activeTabId.value)
    send_loading.value = false
  }
}

const insertExample = (code) => {
  editor.value.setText(code)
  showDrawer.value = false
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

const filteredHistory = computed(() => {
  if (!searchText.value) {
    return history.value
  } else {
    return history.value.filter(item => {
      return item.method.includes(searchText.value) ||
          item.path.includes(searchText.value) ||
          item.dsl.includes(searchText.value)
    })
  }
})

const currentPageData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredHistory.value.slice(start, end)
})

const getMethodTagType = (method) => {
  const types = {
    'GET': 'success',
    'POST': 'info',
    'PUT': 'warning',
    'DELETE': 'error'
  }
  return types[method] || 'default'
}

const dslExamples = {
  term: JSON.stringify({
    "query": {
      "term": {
        "status": "active"
      }
    },
    "size": 10,
    "track_total_hits": true
  }, null, 2),

  terms: JSON.stringify({
    "query": {
      "terms": {
        "user_id": [1, 2, 3, 4]
      }
    },
    "size": 10
  }, null, 2),

  match: JSON.stringify({
    "query": {
      "match": {
        "description": "quick brown fox"
      }
    },
    "size": 20
  }, null, 2),

  matchPhrase: JSON.stringify({
    "query": {
      "match_phrase": {
        "description": {
          "query": "quick brown fox",
          "slop": 1
        }
      }
    }
  }, null, 2),

  range: JSON.stringify({
    "query": {
      "range": {
        "age": {
          "gte": 20,
          "lte": 30
        }
      }
    }
  }, null, 2),

  bool: JSON.stringify({
    "query": {
      "bool": {
        "must": [
          {"term": {"status": "active"}}
        ],
        "must_not": [
          {"term": {"type": "deleted"}}
        ],
        "should": [
          {"term": {"category": "electronics"}},
          {"term": {"category": "computers"}}
        ],
        "minimum_should_match": 1
      }
    }
  }, null, 2),

  termsAggs: JSON.stringify({
    "aggs": {
      "status_counts": {
        "terms": {
          "field": "status",
          "missing": "N/A",
          "size": 10
        }
      }
    },
    "size": 0
  }, null, 2),

  dateHistogram: JSON.stringify({
    "aggs": {
      "sales_over_time": {
        "date_histogram": {
          "field": "created_at",
          "calendar_interval": "1d",
          "format": "yyyy-MM-dd"
        }
      }
    },
    "size": 0
  }, null, 2),

  nested: JSON.stringify({
    "query": {
      "nested": {
        "path": "comments",
        "query": {
          "bool": {
            "must": [
              {"match": {"comments.text": "great"}},
              {"term": {"comments.rating": 5}}
            ]
          }
        }
      }
    }
  }, null, 2),

  exists: JSON.stringify({
    "query": {
      "exists": {
        "field": "email"
      }
    }
  }, null, 2),

  multiMatch: JSON.stringify({
    "query": {
      "multi_match": {
        "query": "quick brown fox",
        "fields": ["title", "description^2"],
        "type": "best_fields"
      }
    }
  }, null, 2),

  wildcard: JSON.stringify({
    "query": {
      "wildcard": {
        "email": "*@gmail.com"
      }
    }
  }, null, 2),

  metrics: JSON.stringify({
    "aggs": {
      "avg_price": {"avg": {"field": "price"}},
      "max_price": {"max": {"field": "price"}},
      "min_price": {"min": {"field": "price"}},
      "sum_quantity": {"sum": {"field": "quantity"}}
    },
    "size": 0
  }, null, 2),

  cardinality: JSON.stringify({
    "aggs": {
      "unique_users": {
        "cardinality": {
          "field": "user_id",
          "precision_threshold": 100
        }
      }
    },
    "size": 0
  }, null, 2),

  script: JSON.stringify({
    "query": {
      "script_score": {
        "query": {"match_all": {}},
        "script": {
          "source": "doc['price'].value * doc['rating'].value",
          "lang": "painless"
        }
      }
    }
  }, null, 2)
}

// 示例列表（带i18n标题，供抽屉渲染与一键插入）
const exampleList = computed(() => [
  {key: 'term', title: t('rest.exampleTerm'), code: dslExamples.term},
  {key: 'terms', title: t('rest.exampleTerms'), code: dslExamples.terms},
  {key: 'match', title: t('rest.exampleMatch'), code: dslExamples.match},
  {key: 'matchPhrase', title: t('rest.exampleMatchPhrase'), code: dslExamples.matchPhrase},
  {key: 'range', title: t('rest.exampleRange'), code: dslExamples.range},
  {key: 'bool', title: t('rest.exampleBool'), code: dslExamples.bool},
  {key: 'termsAggs', title: t('rest.exampleTermsAggs'), code: dslExamples.termsAggs},
  {key: 'dateHistogram', title: t('rest.exampleDateHistogram'), code: dslExamples.dateHistogram},
  {key: 'nested', title: t('rest.exampleNested'), code: dslExamples.nested},
  {key: 'exists', title: t('rest.exampleExists'), code: dslExamples.exists},
  {key: 'multiMatch', title: t('rest.exampleMultiMatch'), code: dslExamples.multiMatch},
  {key: 'wildcard', title: t('rest.exampleWildcard'), code: dslExamples.wildcard},
  {key: 'metrics', title: t('rest.exampleMetrics'), code: dslExamples.metrics},
  {key: 'cardinality', title: t('rest.exampleCardinality'), code: dslExamples.cardinality},
  {key: 'script', title: t('rest.exampleScript'), code: dslExamples.script},
])

</script>

<style>
.editarea, .json_view {
  height: 72dvh;
}

.ace_editor:not(.ace_focus) .ace_cursor {
  opacity: 0 !important;
}

.ace_editor .ace_placeholder {
  position: absolute;
  z-index: 10;
}
</style>

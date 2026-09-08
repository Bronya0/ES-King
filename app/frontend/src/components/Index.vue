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
      <h2>{{ t('index.title') }}</h2>
      <n-text>{{ t('index.total', { count: data.length }) }}</n-text>
    </n-flex>
    <n-flex align="center">
      <n-input v-model:value="search_text" autosize :placeholder="t('index.fuzzySearch')" style="min-width: 20%"
               @keydown.enter="search"/>

      <n-button :render-icon="renderIcon(SearchFilled)" @click="search"></n-button>
      <n-button :render-icon="renderIcon(AddFilled)" @click="openCreateIndex">{{ t('index.addIndex') }}</n-button>
      <n-button :render-icon="renderIcon(DriveFileMoveTwotone)" @click="downloadAllDataCsv">{{ t('common.exportCsv') }}</n-button>
      <n-button :render-icon="renderIcon(AnnouncementOutlined)" @click="queryAlias">{{ t('index.readAlias') }}</n-button>
      <n-button :loading="downloadIndexConfig.loading" :render-icon="renderIcon(DriveFileMoveTwotone)"
                @click="downloadIndexConfig.show = true">
        {{ t('index.indexBackup') }}
      </n-button>

    </n-flex>

    <n-spin :show="loading" :description="t('app.connecting')">
      <n-data-table
          ref="tableRef"
          v-model:checked-row-keys="selectedRowKeys"
          :bordered="false"
          :columns="refColumns(columns)"
          :data="data"
          :pagination="pagination"
          :row-key="rowKey"
          size="small"
          striped
      />
    </n-spin>
    <n-flex align="center">
      <n-dropdown :options="bulk_options">
        <n-button>{{ t('index.batchAction') }}</n-button>
      </n-dropdown>
      <n-text> {{ t('index.selectedRows', { count: selectedRowKeys.length }) }}</n-text>
    </n-flex>

    <n-drawer v-model:show="downloadIndexConfig.show" style="width: 38.2%">
      <n-drawer-content style="text-align: left;" :title="t('index.indexBackup')">
        <n-flex vertical>
          <n-p>{{ t('index.backupDesc') }}</n-p>
          {{ t('index.backupIndexName') }}
          <n-input v-model:value="downloadIndexConfig.indexName"/>
          {{ t('index.backupDsl') }}
          <n-input v-model:value="downloadIndexConfig.dsl" style="min-height: 300px; max-height: 800px;"
                   type="textarea"/>
          {{ t('index.backupCode') }}
          <n-input v-model:value="downloadIndexConfig.code"/>
          <n-flex align="center">
            <n-button @click="downloadIndexConfig.show = false">{{ t('common.cancel') }}</n-button>
            <n-button :loading="downloadIndexConfig.loading" type="primary" @click="downloadIndex">{{ t('common.startDownload') }}</n-button>
          </n-flex>
          {{ downloadIndexConfig.msg }}
        </n-flex>
      </n-drawer-content>
    </n-drawer>


    <n-drawer v-model:show="drawerVisible" style="width: 38.2%">
      <n-drawer-content :title="drawer_title" style="text-align: left;">
        <n-code :code="json_data" language="json" show-line-numbers/>
      </n-drawer-content>
    </n-drawer>

    <n-drawer v-model:show="CreateIndexDrawerVisible" style="width: 38.2%">
      <n-drawer-content style="text-align: left;" :title="t('index.createIndex')">
        <n-form
            ref="formRef"
            :model="indexConfig"
            :rules="{
              name: {required: true, message: t('index.validateName'), trigger: 'blur'},
              numberOfShards: {required: true, type: 'number', message: t('index.validateShards'), trigger: 'blur'},
              numberOfReplicas: {required: true, type: 'number', message: t('index.validateReplicas'), trigger: 'blur'},
            }"
            label-placement="top"
            style="text-align: left;"
        >
          <n-form-item :label="t('index.fromTemplate')" path="template">
            <n-select v-model:value="indexConfig.template" :options="templateOptions" clearable
                      :placeholder="t('index.templateOptional')"/>
          </n-form-item>
          <n-form-item :label="t('index.indexName')" path="name">
            <n-input v-model:value="indexConfig.name"/>
          </n-form-item>
          <n-form-item :label="t('index.primaryShards')" path="numberOfShards">
            <n-input-number v-model:value="indexConfig.numberOfShards"/>
          </n-form-item>
          <n-form-item :label="t('index.replicas')" path="numberOfReplicas">
            <n-input-number v-model:value="indexConfig.numberOfReplicas"/>
          </n-form-item>
          <n-p>{{ t('index.mapping') }}</n-p>
          <n-form-item path="mapping">
            <n-input v-model:value="indexConfig.mapping" :placeholder='JSON.stringify({"properties":{"created_at":{"type":"date","format":"yyyy-MM-dd HH:mm:ss"}}}, null, 2)' style="min-height: 300px; max-height: 800px;"
                     type="textarea"/>
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="CreateIndexDrawerVisible = false">{{ t('common.cancel') }}</n-button>
            <n-button :loading="addIndexLoading" type="primary" @click="addIndex">{{ t('common.save') }}</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>

    <n-drawer v-model:show="addDocDrawerVisible" style="width: 38.2%">
      <n-drawer-content style="text-align: left;" :title="t('index.addDocument')">
        <n-form
            :model="docConfig"
            :rules="{
              doc: {required: true, message: t('index.validateDoc'), trigger: 'blur'},
            }"
            label-placement="top"
            style="text-align: left;"
        >
          <n-form-item :label="t('index.docContent')" path="doc">
            <n-input v-model:value="docConfig.doc" :placeholder='JSON.stringify({"field1": "value1", "field2": "value2"}, null, 2)' style="min-height: 300px; max-height: 800px;"
                     type="textarea"/>
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="addDocDrawerVisible = false">{{ t('common.cancel') }}</n-button>
            <n-button :loading="addDocLoading" type="primary" @click="addDocumentFunc">{{ t('common.save') }}</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>

    <!-- 别名管理 -->
    <n-modal v-model:show="aliasModal.show" preset="card" :title="t('index.manageAlias') + ' - ' + aliasModal.index"
             style="width: 560px;">
      <n-spin :show="aliasModal.loading">
        <n-empty v-if="aliasModal.aliases.length === 0" :description="t('index.noAlias')"/>
        <n-list v-else>
          <n-list-item v-for="alias in aliasModal.aliases" :key="alias">
            <n-flex align="center" justify="space-between">
              <n-tag type="info">{{ alias }}</n-tag>
              <n-button size="small" quaternary type="error" @click="removeAlias(alias)">{{ t('common.delete') }}</n-button>
            </n-flex>
          </n-list-item>
        </n-list>
      </n-spin>
      <n-divider/>
      <n-form label-placement="top">
        <n-form-item :label="t('index.newAlias')">
          <n-input v-model:value="aliasModal.newAlias" placeholder="my-alias" @keydown.enter="addAlias"/>
        </n-form-item>
        <n-form-item :label="t('index.aliasExtra')">
          <n-input v-model:value="aliasModal.extra" type="textarea" :autosize="{minRows: 1, maxRows: 5}"
                   class="json-editor-input"
                   :placeholder='JSON.stringify({"filter": {"term": {"env": "prod"}}, "routing": "1"}, null, 2)'/>
        </n-form-item>
      </n-form>
      <n-flex justify="end">
        <n-button @click="aliasModal.show = false">{{ t('common.close') }}</n-button>
        <n-button type="primary" :loading="aliasModal.adding" @click="addAlias">{{ t('index.addAlias') }}</n-button>
      </n-flex>
    </n-modal>

    <!-- Reindex -->
    <n-modal v-model:show="reindexModal.show" preset="card" :title="t('index.reindex')" style="width: 560px;">
      <n-form label-placement="top">
        <n-form-item :label="t('index.sourceIndex')">
          <n-input :value="reindexModal.source" disabled/>
        </n-form-item>
        <n-form-item :label="t('index.destIndex')">
          <n-input v-model:value="reindexModal.dest" :placeholder="t('index.destIndexPlaceholder')"/>
        </n-form-item>
        <n-form-item :label="t('index.reindexQuery')">
          <n-input v-model:value="reindexModal.query" type="textarea" :autosize="{minRows: 3, maxRows: 10}"
                   class="json-editor-input" :placeholder='JSON.stringify({"term": {"status": "active"}}, null, 2)'/>
        </n-form-item>
      </n-form>
      <n-text depth="3">{{ t('index.reindexHint') }}</n-text>
      <n-flex justify="end" style="margin-top: 12px;">
        <n-button @click="reindexModal.show = false">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" :loading="reindexModal.loading" @click="doReindex">{{ t('common.execute') }}</n-button>
      </n-flex>
    </n-modal>

    <!-- Mapping 编辑 -->
    <n-modal v-model:show="mappingModal.show" preset="card"
             :title="t('index.editMapping') + ' - ' + mappingModal.index" style="width: 640px;">
      <n-alert type="warning" :show-icon="true" style="margin-bottom: 12px;">{{ t('index.mappingEditWarning') }}</n-alert>
      <n-input v-model:value="mappingModal.content" type="textarea" :autosize="{minRows: 12, maxRows: 24}"
               class="json-editor-input"/>
      <n-flex justify="end" style="margin-top: 12px;">
        <n-button @click="mappingModal.show = false">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" :loading="mappingModal.saving" @click="saveMapping">{{ t('common.save') }}</n-button>
      </n-flex>
    </n-modal>

    <!-- Settings 编辑 -->
    <n-modal v-model:show="settingsModal.show" preset="card"
             :title="t('index.editSettings') + ' - ' + settingsModal.index" style="width: 640px;">
      <n-alert type="info" :show-icon="true" style="margin-bottom: 12px;">{{ t('index.settingsEditWarning') }}</n-alert>
      <n-input v-model:value="settingsModal.content" type="textarea" :autosize="{minRows: 12, maxRows: 24}"
               class="json-editor-input"/>
      <n-flex justify="end" style="margin-top: 12px;">
        <n-button @click="settingsModal.show = false">{{ t('common.cancel') }}</n-button>
        <n-button type="primary" :loading="settingsModal.saving" @click="saveSettings">{{ t('common.save') }}</n-button>
      </n-flex>
    </n-modal>
  </n-flex>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import {h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDataTable, NDropdown, NIcon, NTag, NText, useDialog, useMessage} from 'naive-ui'
import {
  createCsvContent,
  download_file,
  formatBytes,
  formattedJson,
  isValidJson,
  refColumns,
  renderIcon
} from "../utils/common";
import {AddFilled, AnnouncementOutlined, DriveFileMoveTwotone, MoreVertFilled, SearchFilled} from "@vicons/material";
import {
  AddDocument,
  AddIndexAlias,
  CacheClear,
  CreateIndex,
  CreateIndexFromTemplate,
  DeleteIndex,
  DownloadESIndex,
  Flush,
  GetDoc10,
  GetIndexAliases,
  GetIndexes,
  GetIndexInfo,
  GetIndexTemplates,
  MergeSegments,
  OpenCloseIndex,
  Refresh,
  RemoveIndexAlias,
  Reindex,
  UpdateIndexMappings,
  UpdateIndexSettings,
} from "../../wailsjs/go/service/ESService";

const { t } = useI18n()

const drawerVisible = ref(false)
const CreateIndexDrawerVisible = ref(false)
const json_data = ref({})
const drawer_title = ref("")
const loading = ref(false)
const tableRef = ref();
const formRef = ref();
const indexConfig = ref({
  name: "",
  numberOfShards: 1,
  numberOfReplicas: 0,
  mapping: "",
  template: null,
});
const data = ref([])
const message = useMessage()
const dialog = useDialog()

const search_text = ref("")
const selectedRowKeys = ref([]);
const rowKey = (row) => row.index
let aliases = {};

const downloadIndexConfig = ref({
  indexName: "",
  dsl: "",
  loading: false,
  show: false,
  code: null,
  msg: null,
});

const downloadIndex = async () => {
  const indexName = downloadIndexConfig.value.indexName;
  const dsl = downloadIndexConfig.value.dsl;

  if (!indexName) {
    message.error(t('index.fillIndexName'));
    return;
  }
  if (downloadIndexConfig.value.code !== "964440643") {
    message.error(t('index.codeError'));
    return;
  }
  const file_path = `/${indexName}-${Math.floor(Date.now() / 1000)}.json`

  downloadIndexConfig.value.loading = true;
  try {
    const res = await DownloadESIndex(indexName, dsl, file_path);
    if (res.err !== "") {
      message.error(res.err);
      downloadIndexConfig.value.msg = res.err;
    } else {
      const savedPath = res.result || file_path;
      const downloadMsg = t('index.backupSuccess') + " " + savedPath;
      message.success(downloadMsg);
      downloadIndexConfig.value.msg = downloadMsg;
      downloadIndexConfig.value.show = false;
    }
  } catch (e) {
    message.error(e.message);
    downloadIndexConfig.value.msg = e;
  } finally {
    downloadIndexConfig.value.loading = false;
  }
};

const selectNode = (node) => {
  data.value = []
  selectedRowKeys.value = []
  aliases = []
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
})

const search = async () => {
  loading.value = true
  try {
    await getData(search_text.value)
  } catch (e) {
    message.error(e.message)
  }
  loading.value = false
}

const cacheData = (indexes) => {
  const key = 'es_king_indexes';
  let values = []
  const stored = localStorage.getItem(key);
  if (stored) {
    values = JSON.parse(stored)
    for (let v of indexes) {
      if (!values.includes(v)) {
        values.push(v);
      }
    }
  }
  if (values) {
    localStorage.setItem(key, JSON.stringify(values.slice(-1000)))
  }
}

const getData = async (value) => {
  const res = await GetIndexes(value)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    data.value = res.results
    cacheData(res.results.map(item => item.index))
  }
}

const pageKey = 'esKing:index:pageKey'
const pagination = ref({
  page: 1,
  pageSize: parseInt(localStorage.getItem(pageKey)) || 10,
  showSizePicker: true,
  pageSizes: [5, 10, 15, 20, 25, 30, 40],
  onChange: (page) => {
    pagination.value.page = page
  },
  onUpdatePageSize: (pageSize) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
    localStorage.setItem(pageKey, pageSize.toString())
  },
  itemCount: data.value.length
})

const getType = (value) => {
  const type = {
    "green": "success",
    "yellow": "warning",
    "open": "success",
    "close": "error",
  }
  return type[value] || 'error'
}

const columns = [
  {
    type: "selection",
  },
  {
    title: t('index.colIndexName'),
    key: 'index',
    width: 200,
    render: (row) => h(NText, {
          type: 'info',
          style: {cursor: 'pointer'},
          onClick: () => viewIndexDocs(row)
        },
        {default: () => row['index']}
    )
  },
  {title: t('index.colAlias'), key: 'alias',   },
  {
    title: t('index.colHealth'),
    key: 'health',
    render: (row) => h(NTag, {type: getType(row['health'])}, {default: () => row['health']}),
  },
  {
    title: t('index.colStatus'),
    key: 'status',
    render: (row) => h(NTag, {type: getType(row['status'])}, {default: () => row['status']}),
  },
  {
    title: t('index.colPrimary'),
    key: 'pri',
    sorter: (a, b) => Number(a['pri']) - Number(b['pri'])
  },
  {
    title: t('index.colReplica'),
    key: 'rep',
    sorter: (a, b) => Number(a['rep']) - Number(b['rep'])
  },
  {
    title: t('index.colDocCount'),
    key: 'docs.count',
    sorter: (a, b) => Number(a['docs.count']) - Number(b['docs.count'])
  },
  {
    title: t('index.colDeleted'),
    key: 'docs.deleted',
    sorter: (a, b) => Number(a['docs.deleted']) - Number(b['docs.deleted'])
  },
  {
    title: t('index.colStore'),
    key: 'store.size',
    sorter: (a, b) => Number(a['store.size']) - Number(b['store.size']),
    render(row) {
      return h('span', formatBytes(row['store.size']))
    }
  },
  {
    title: t('index.colActions'),
    key: 'actions',
    render: (row) => {
      const options = [
        {label: t('index.actAddDoc'), key: 'addDocument'},
        {label: t('index.actViewDetails'), key: 'viewDetails'},
        {label: t('index.actViewAlias'), key: 'viewAlias'},
        {label: t('index.actViewDocs'), key: 'viewDocs'},
        {label: t('index.actManageAlias'), key: 'manageAlias'},
        {label: t('index.actEditMapping'), key: 'editMapping'},
        {label: t('index.actEditSettings'), key: 'editSettings'},
        {label: t('index.actReindex'), key: 'reindex'},
        {label: t('index.actMerge'), key: 'mergeSegments'},
        {label: t('index.actDelete'), key: 'deleteIndex'},
        {label: row.status === 'close' ? t('index.actOpen') : t('index.actClose'), key: 'openCloseIndex'},
        {label: t('index.actRefresh'), key: 'refresh'},
        {label: t('index.actFlush'), key: 'flush'},
        {label: t('index.actClearCache'), key: 'clearCache'},
      ]
      return h(
          NDropdown,
          {
            trigger: 'click',
            options,
            onSelect: (key) => handleMenuSelect(key, row)
          },
          {
            default: () => h(
                NButton,
                {
                  strong: true,
                  secondary: true,
                },
                {default: () => t('common.operation'), icon: () => h(NIcon, null, {default: () => h(MoreVertFilled)})}
            )
          }
      )
    }
  }
]

const handleMenuSelect = async (key, row) => {
  const func = {
    "addDocument": addDocument,
    "viewDetails": viewIndexDetails,
    "viewAlias": viewIndexAlias,
    "viewDocs": viewIndexDocs,
    "manageAlias": manageAlias,
    "editMapping": editMapping,
    "editSettings": editSettings,
    "reindex": openReindex,
    "mergeSegments": mergeSegments,
    "deleteIndex": deleteIndex,
    "refresh": refreshIndex,
    "openCloseIndex": openCloseIndex,
    "flush": flushIndex,
    "clearCache": clearCache,
  }
  loading.value = true
  try {
    await func[key](row)
  } catch (e) {
    message.error(e.message)
  }
  loading.value = false
}

const addDocDrawerVisible = ref(false);
const addDocLoading = ref(false);
const docConfig = ref({
  index: "",
  doc: "",
});

const addDocument = async (row) => {
  addDocDrawerVisible.value = true;
  docConfig.value.index = row.index;
}
const addDocumentFunc = async () => {
  if (!docConfig.value.doc) {
    message.error(t('index.validateDoc'))
    return
  }
  if (!isValidJson(docConfig.value.doc)) {
    message.error(t('common.fillRequired'))
    return
  }
  addDocLoading.value = true;
  try {
    const res = await AddDocument(docConfig.value.index, docConfig.value.doc);
    if (res.err !== "") {
      message.error(res.err);
    } else {
      message.success(t('index.docAdded', { id: res.result['_id'] }));
      await search();
    }
  } catch (e) {
    message.error(e.message);
  } finally {
    addDocLoading.value = false;
    addDocDrawerVisible.value = false;
    docConfig.value.index = "";
    docConfig.value.doc = "";
  }
}

const viewIndexDetails = async (row) => {
  const res = await GetIndexInfo(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
  }
}
const viewIndexAlias = async (row) => {
  const res = await GetIndexAliases([row.index])
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
  }
}
const viewIndexDocs = async (row) => {
  loading.value = true
  try {
    const res = await GetDoc10(row.index)
    if (res.err !== "") {
      message.error(res.err)
    } else {
      json_data.value = formattedJson(res.result)
      drawer_title.value = row.index
      drawerVisible.value = true
    }
  } catch (e) {
    message.error(e.message)
  }
  loading.value = false
}
const mergeSegments = async (row) => {
  dialog.info({
    title: t('common.warning'),
    content: t('index.confirmMerge', { name: row.index }),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      await mergeSegmentsFunc(row)
    }
  })
}
const mergeSegmentsFunc = async (row) => {
  const res = await MergeSegments(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
    message.success(t('index.mergeSubmitted'))
    await search()
  }
}
const deleteIndex = async (row) => {
  dialog.info({
    title: t('common.warning'),
    content: t('index.confirmDelete', { name: row.index }),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      await deleteIndexFunc(row)
    }
  })
}
const deleteIndexFunc = async (row) => {
  const res = await DeleteIndex(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
    await search()
  }
}
const openCloseIndex = async (row) => {
  const res = await OpenCloseIndex(row.index, row.status)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
    await search()
  }
}
const refreshIndex = async (row) => {
  const res = await Refresh(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
  }
}
const flushIndex = async (row) => {
  const res = await Flush(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
  }
}
const clearCache = async (row) => {
  const res = await CacheClear(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
    await search()
  }
}
const addIndexLoading = ref(false)

// 打开创建索引抽屉时加载模板列表
const openCreateIndex = async () => {
  indexConfig.value.template = null
  CreateIndexDrawerVisible.value = true
  const res = await GetIndexTemplates()
  if (res.err === "" && Array.isArray(res.results)) {
    templateOptions.value = res.results.map(tpl => {
      const patterns = Array.isArray(tpl.index_patterns) ? tpl.index_patterns.join(', ') : ''
      return {label: patterns ? `${tpl.name} (${patterns})` : tpl.name, value: tpl.name}
    })
  }
}

const templateOptions = ref([])

const addIndex = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      if (indexConfig.value.template) {
        await createIndexFromTemplate()
        return
      }
      if (indexConfig.value.mapping) {
        const err = isValidJson(indexConfig.value.mapping)
        if (!err) {
          message.error(t('index.invalidMapping'))
          return
        }
      }

      addIndexLoading.value = true
      try {
        const res = await CreateIndex(indexConfig.value.name, indexConfig.value.numberOfShards, indexConfig.value.numberOfReplicas, indexConfig.value.mapping)
        if (res.err !== "") {
          message.error(res.err)
        } else {
          message.success(t('index.indexCreated', { name: indexConfig.value.name }))
          await search()
        }
      } catch (e) {
        message.error(e.message)
      } finally {
        addIndexLoading.value = false
        CreateIndexDrawerVisible.value = false
      }
    } else {
      message.error(t('common.fillRequired'))
    }
  })
}

const createIndexFromTemplate = async () => {
  addIndexLoading.value = true
  try {
    const res = await CreateIndexFromTemplate(
        indexConfig.value.name,
        indexConfig.value.template,
        indexConfig.value.numberOfShards,
        indexConfig.value.numberOfReplicas
    )
    if (res.err !== "") {
      message.error(res.err)
    } else {
      message.success(t('index.indexCreated', {name: indexConfig.value.name}))
      await search()
      CreateIndexDrawerVisible.value = false
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    addIndexLoading.value = false
  }
}

const downloadAllDataCsv = async () => {
  const csvContent = createCsvContent(data.value, columns)
  download_file(csvContent, t('index.csvFileName'), 'text/csv;charset=utf-8;')
}

const queryAlias = async () => {
  loading.value = true
  let name_lst = []
  const start = (pagination.value.page - 1) * pagination.value.pageSize;
  const end = start + pagination.value.pageSize;
  let pagedData = data.value.slice(start, end);
  for (const k in pagedData) {
    name_lst.push(pagedData[k].index)
  }
  try {
    const res = await GetIndexAliases(name_lst)
    if (res.err !== "") {
      loading.value = false
      message.error(res.err)
      return
    }
    aliases = {...aliases, ...res.result}
    for (const k in data.value) {
      const alias = aliases[data.value[k].index]
      if (alias) {
        data.value[k].alias = alias
      }
    }
  } catch (e) {
    message.error(e.message)
  }
  loading.value = false
}

// ==================== 别名管理 ====================
const aliasModal = ref({
  show: false,
  index: '',
  aliases: [],
  newAlias: '',
  extra: '',
  loading: false,
  adding: false,
})

const manageAlias = async (row) => {
  aliasModal.value.show = true
  aliasModal.value.index = row.index
  aliasModal.value.newAlias = ''
  aliasModal.value.extra = ''
  aliasModal.value.loading = true
  try {
    const res = await GetIndexAliases([row.index])
    if (res.err !== "") {
      message.error(res.err)
      aliasModal.value.aliases = []
    } else {
      const joined = res.result[row.index] || ''
      aliasModal.value.aliases = joined ? joined.split(',') : []
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    aliasModal.value.loading = false
  }
}

const refreshAliasList = async () => {
  const res = await GetIndexAliases([aliasModal.value.index])
  if (res.err !== "") {
    message.error(res.err)
    return
  }
  const joined = res.result[aliasModal.value.index] || ''
  aliasModal.value.aliases = joined ? joined.split(',') : []
}

const addAlias = async () => {
  if (!aliasModal.value.newAlias) {
    message.warning(t('index.inputAlias'))
    return
  }
  if (aliasModal.value.extra && !isValidJson(aliasModal.value.extra)) {
    message.error(t('index.invalidAliasExtra'))
    return
  }
  aliasModal.value.adding = true
  try {
    const res = await AddIndexAlias(aliasModal.value.index, aliasModal.value.newAlias, aliasModal.value.extra)
    if (res.err !== "") {
      message.error(res.err)
    } else {
      message.success(t('index.aliasAdded'))
      aliasModal.value.newAlias = ''
      aliasModal.value.extra = ''
      await refreshAliasList()
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    aliasModal.value.adding = false
  }
}

const removeAlias = async (alias) => {
  dialog.warning({
    title: t('common.warning'),
    content: t('index.confirmRemoveAlias', {alias}),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      const res = await RemoveIndexAlias(aliasModal.value.index, alias)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success(t('index.aliasRemoved'))
        await refreshAliasList()
      }
    }
  })
}

// ==================== Reindex ====================
const reindexModal = ref({
  show: false,
  source: '',
  dest: '',
  query: '',
  loading: false,
})

const openReindex = (row) => {
  reindexModal.value = {show: true, source: row.index, dest: '', query: '', loading: false}
}

const doReindex = async () => {
  if (!reindexModal.value.dest) {
    message.warning(t('index.inputDestIndex'))
    return
  }
  if (reindexModal.value.query && !isValidJson(reindexModal.value.query)) {
    message.error(t('docs.invalidQuery'))
    return
  }
  reindexModal.value.loading = true
  try {
    const res = await Reindex(reindexModal.value.source, reindexModal.value.dest, reindexModal.value.query)
    if (res.err !== "") {
      message.error(res.err)
    } else {
      message.success(t('index.reindexSubmitted'))
      reindexModal.value.show = false
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    reindexModal.value.loading = false
  }
}

// ==================== Mapping / Settings 编辑 ====================
const mappingModal = ref({
  show: false,
  index: '',
  content: '',
  saving: false,
})

const editMapping = async (row) => {
  const res = await GetIndexInfo(row.index)
  if (res.err !== "") {
    message.error(res.err)
    return
  }
  const info = (res.result && res.result[row.index]) || {}
  const mappings = info.mappings || {}
  mappingModal.value = {
    show: true,
    index: row.index,
    content: JSON.stringify(mappings, null, 2),
    saving: false,
  }
}

const saveMapping = async () => {
  if (!isValidJson(mappingModal.value.content)) {
    message.error(t('index.invalidMapping'))
    return
  }
  mappingModal.value.saving = true
  try {
    const res = await UpdateIndexMappings(mappingModal.value.index, mappingModal.value.content)
    if (res.err !== "") {
      message.error(res.err)
    } else {
      message.success(t('index.mappingSaved'))
      mappingModal.value.show = false
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    mappingModal.value.saving = false
  }
}

const settingsModal = ref({
  show: false,
  index: '',
  content: '',
  saving: false,
})

const editSettings = async (row) => {
  const res = await GetIndexInfo(row.index)
  if (res.err !== "") {
    message.error(res.err)
    return
  }
  const info = (res.result && res.result[row.index]) || {}
  const settings = (info.settings && info.settings.index) || {}
  settingsModal.value = {
    show: true,
    index: row.index,
    content: JSON.stringify({index: settings}, null, 2),
    saving: false,
  }
}

const saveSettings = async () => {
  if (!isValidJson(settingsModal.value.content)) {
    message.error(t('index.invalidSettings'))
    return
  }
  settingsModal.value.saving = true
  try {
    const res = await UpdateIndexSettings(settingsModal.value.index, settingsModal.value.content)
    if (res.err !== "") {
      message.error(res.err)
    } else {
      message.success(t('index.settingsSaved'))
      settingsModal.value.show = false
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    settingsModal.value.saving = false
  }
}

const bulk_delete = async () => {
  loading.value = true
  let success_count = 0
  for (const Key in selectedRowKeys.value) {
    const res = await DeleteIndex(selectedRowKeys.value[Key])
    if (res.err !== "") {
      message.error(res.err)
      break
    } else {
      success_count += 1
    }
  }
  selectedRowKeys.value = []
  message.success(t('index.downloadSuccess', { count: success_count }))
  loading.value = false
  await search()
}
const bulk_options = [
  {
    label: t('common.delete'),
    key: 'bulk_delete',
    props: {
      onClick: async () => {
        dialog.info({
          title: t('common.warning'),
          content: t('index.confirmBatchDelete', { names: selectedRowKeys.value }),
          positiveText: t('common.confirm'),
          negativeText: t('common.cancel'),
          onPositiveClick: async () => {
            await bulk_delete()
          }
        })
      }
    }
  },
]
</script>

<style scoped>

</style>

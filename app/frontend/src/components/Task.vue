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
      <h2>{{ t('task.title') }}</h2>
      <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getData">{{ t('common.refresh') }}</n-button>
    </n-flex>
    <n-flex align="center">
      <n-input v-model:value="taskIdFilter" :placeholder="t('task.filterTaskId')" style="width: 160px;" clearable />
      <n-input v-model:value="nodeFilter" :placeholder="t('task.filterNode')" style="width: 160px;" clearable />
      <n-input v-model:value="actionFilter" :placeholder="t('task.filterAction')" style="width: 160px;" clearable />
      <n-button @click="applyFilters">{{ t('task.query') }}</n-button>
      <n-button :render-icon="renderIcon(DriveFileMoveTwotone)" @click="downloadAllDataCsv">{{ t('task.exportCsv') }}</n-button>
    </n-flex>

    <n-spin :show="loading" :description="t('app.connecting')">
      <n-data-table
          v-model:checked-row-keys="selectedRowKeys"
          :bordered="false"
          :columns="refColumns(columns)"
          :data="filteredData"
          :max-height="600"
          :pagination="pagination"
          :row-key="rowKey"
          size="small"
          striped
      />
    </n-spin>
  </n-flex>

  <n-drawer v-model:show="drawerVisible" style="width: 38.2%">
    <n-drawer-content style="text-align: left;" :title="t('common.result')">
      <n-code :code="json_data" language="json" show-line-numbers word-wrap style="text-align: left;"/>
    </n-drawer-content>
  </n-drawer>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import {computed, h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDataTable, NIcon, NTag, useMessage} from 'naive-ui'
import {createCsvContent, download_file, formatDate, formattedJson, refColumns, renderIcon} from "../utils/common";
import {DriveFileMoveTwotone, DeleteOutlined, RefreshOutlined} from "@vicons/material";
import {
  GetTasks, CancelTasks
} from "../../wailsjs/go/service/ESService";

const { t } = useI18n()

const drawerVisible = ref(false)
const json_data = ref()

const loading = ref(false)
const data = ref([])
const message = useMessage()
const selectedRowKeys = ref([]);
const rowKey = (row) => row['task_id']

const selectNode = async (node) => {
  drawerVisible.value = false
  json_data.value = null
  loading.value = false
  data.value = []
  selectedRowKeys.value = []

  await getData()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  getData()
})

const taskIdFilter = ref('')
const nodeFilter = ref('')
const actionFilter = ref('')
const filteredData = ref([])

const applyFilters = () => {
  filteredData.value = data.value.filter(item => {
    const matchesTaskId = !taskIdFilter.value || item.task_id.toLowerCase().includes(taskIdFilter.value.toLowerCase())
    const matchesNode = !nodeFilter.value || item.node_name.toLowerCase().includes(nodeFilter.value.toLowerCase())
    const matchesAction = !actionFilter.value || item.action.toLowerCase().includes(actionFilter.value.toLowerCase())
    return matchesTaskId && matchesNode && matchesAction
  })
}

const getData = async () => {
  const res = await GetTasks()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    data.value = res.results
    applyFilters()
  }
}

const CancelTask = async (row) => {
  loading.value = true
  const res = await CancelTasks(row['task_id'])
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawerVisible.value = true
  }

  loading.value = false
  await getData()
}

const pagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [5, 10, 20, 30, 40],
  onChange: (page) => {
    pagination.value.page = page
  },
  onUpdatePageSize: (pageSize) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
  },
  itemCount: data.value.length
})

const columns = computed(() => [
  {
    title: t('task.colTaskId'),
    key: 'task_id',
    width: 80,
  },
  {
    title: t('task.colParentTaskId'),
    key: 'parent_task_id',
    width: 80,
  },
  {
    title: t('task.colNode'),
    key: 'node_name',
    width: 60,
  },
  {title: t('task.colIp'), key: 'node_ip', width: 60,},
  {title: t('task.colType'), key: 'type', width: 60,},
  {
    title: t('task.colAction'),
    key: 'action',
    width: 120,
    render: (row) => h(NTag, {type: "info"}, {default: () => row['action']}),
  },
  {
    title: t('task.colStartTime'),
    key: 'start_time_in_millis',
    width: 60,
    render(row) {
      const date = new Date(row['start_time_in_millis']);
      return h('span', null, formatDate(date));
    },
  },
  {
    title: t('task.colRunTime'),
    key: 'running_time_in_nanos',
    width: 60,
  },
  {
    title: t('task.colCancellable'),
    key: 'cancellable',
    width: 60,
    render: (row) => h(NTag,
        {type: row['cancellable'] ? "error" : "info"},
        {default: () => row['cancellable'] ? t('task.yes') : t('task.no')}
    ),
  },
  {
    title: t('task.colActions'),
    key: 'actions',
    width: 60,
    render: (row) => {
      return h(
          NButton,
          {
            strong: true,
            secondary: true,
            onClick: () => CancelTask(row),
            disabled: !row['cancellable'],
          },
          {
            default: () => t('task.terminate'), icon: () => h(NIcon, null, {default: () => h(DeleteOutlined)})
          }
      )
    }
  }
])

const downloadAllDataCsv = async () => {
  const csvContent = createCsvContent(data.value, columns.value)
  download_file(csvContent, t('task.csvFileName'), 'text/csv;charset=utf-8;')
}
</script>

<style scoped>
:deep(.n-code),
:deep(.n-code pre),
:deep(.n-code code) {
  text-align: left !important;
  white-space: pre-wrap !important;
  word-break: break-all !important;
}
</style>

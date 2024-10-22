<template>
  <n-flex vertical>

    <n-flex align="center">
      <h2 style="width: 100px;">Task线程</h2>
      <n-button @click="getData" text :render-icon="renderIcon(RefreshOutlined)">refresh</n-button>
    </n-flex>
    <n-flex align="center">
      <n-button @click="downloadAllDataCsv" :render-icon="renderIcon(DriveFileMoveTwotone)">导出为csv</n-button>

    </n-flex>

    <n-spin :show="loading" description="Connecting...">
      <n-data-table
          :columns="columns"
          :data="data"
          :pagination="pagination"
          size="small"
          :bordered="false"
          :max-height="600"
          striped
          :row-key="rowKey"
          v-model:checked-row-keys="selectedRowKeys"
      />
    </n-spin>
  </n-flex>
</template>
<script setup>
import {h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDataTable, NDropdown, NIcon, NTag, NText, useMessage} from 'naive-ui'
import {createCsvContent, download_file, formatDate, renderIcon} from "../utils/common";
import {DriveFileMoveTwotone, DeleteOutlined, RefreshOutlined} from "@vicons/material";
import {
  GetTasks,CancelTasks
} from "../../wailsjs/go/service/ESService";

const loading = ref(false)
const data = ref([])
const message = useMessage()
const selectedRowKeys = ref([]);
const rowKey = (row) => row['task_id']

const selectNode = async (node) => {
  await getData()
}

onMounted(async () => {
  emitter.on('selectNode', selectNode)
  await getData()
})


const getData = async () => {
  const res = await GetTasks()
  console.log(res)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    console.log(res)
    data.value = res.results
  }

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


const columns = [
  {title: '任务id', key: 'task_id', sorter: 'default', width: 80, resizable: true, ellipsis: {tooltip: true},},
  {title: '父任务id', key: 'parent_task_id', sorter: 'default', width: 80, resizable: true, ellipsis: {tooltip: true},},
  {title: '任务节点', key: 'node_name', sorter: 'default', width: 60, ellipsis: {tooltip: true}},
  {title: 'IP', key: 'node_ip', sorter: 'default', width: 60, ellipsis: {tooltip: true}},
  {title: '类型', key: 'type', sorter: 'default', width: 60, ellipsis: {tooltip: true}},
  {title: '任务行为', key: 'action', sorter: 'default', width: 120, ellipsis: {tooltip: true},
    render: (row) => h(NTag, {type: "info"},{default: () => row['action']}),
  },
  {title: '开始时间', key: 'start_time_in_millis', sorter: 'default', width: 60, ellipsis: {tooltip: true},
    render(row) {
      // 将毫秒时间戳转换为 Date 对象
      const date = new Date(row['start_time_in_millis']);
      // 格式化日期时间
      return h('span', null, formatDate(date));
    },
  },
  {title: '运行时间', key: 'running_time_in_nanos', sorter: 'default', width: 60, ellipsis: {tooltip: true},
  },
    // 在 Vue 的模板中，布尔值会被转换为空字符串！！！
  {title: '是否可取消', key: 'cancellable', sorter: 'default', width: 60, ellipsis: {tooltip: true},
    render: (row) => h(NTag,
        { type: row['cancellable'] ? "error" : "info" },
        { default: () => row['cancellable'] ? '是' : '否' }
    ),
  },
  {
    title: '操作',
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
            default: () => '终止', icon: () => h(NIcon, null, { default: () => h(DeleteOutlined) })
          }
      )
    }
  }
]

const CancelTask = async (row) => {
  loading.value = true
  const res = await CancelTasks(row['task_id'])
  if (res.err !== "") {
    message.error(res.err)
  } else {
    message.success(res.result)
  }
  loading.value = false
  await getData()
}

// 下载所有数据的 CSV 文件
const downloadAllDataCsv = async () => {
  const csvContent = createCsvContent(data.value, columns)
  download_file(csvContent, '任务列表.csv', 'text/csv;charset=utf-8;')
}

</script>


<style scoped>

</style>
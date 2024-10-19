<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2 style="width: 42px;">节点</h2>
      <n-button @click="getData" text :render-icon="renderIcon(RefreshOutlined)">refresh</n-button>
      <n-text>共计{{ data.length }}个</n-text>
    </n-flex>
    <n-spin :show="loading" description="Connecting...">
      <n-data-table
          :columns="columns"
          :data="data"
          size="small"
          :bordered="false"
          :max-height="600"
          striped
      />
    </n-spin>
  </n-flex>
</template>
<script setup>
import {onMounted} from "vue";
import emitter from "../utils/eventBus";
import { h, ref, computed } from 'vue'
import {NDataTable, NProgress, NTag, NText, useMessage} from 'naive-ui'
import {renderIcon} from "../utils/common";
import {RefreshOutlined} from "@vicons/material";
import {GetNodes} from "../../wailsjs/go/service/ESService";

const selectNode = async (node) => {
  await getData()
}

onMounted(async () => {
  emitter.on('selectNode', selectNode)
  await getData()
})


const loading = ref(false)
const data = ref([])
const message = useMessage()

const getData = async () => {
  loading.value = true
  const res = await GetNodes()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    data.value = res.results
  }
  loading.value = false

}

const getProgressType = (value) => {
  const numValue = Number(value)
  if (numValue < 60) return 'success'
  if (numValue < 80) return 'warning'
  return 'error'
}

const renderProgress = (row, key) => {
  const value = Number(row[key])
  return h(NProgress, {
    type:"line",
    status: getProgressType(value),
    percentage: value,
    indicatorPlacement: 'inside',
    height: 18,
    borderRadius: 4
  })
}

const columns = [
  { title: 'IP', key: 'ip', sorter: 'default',width: 100,resizable: true },
  { title: '名称', key: 'name', sorter: 'default',width: 100,resizable: true },
  {
    title: '角色',
    key: 'node.role',
    sorter: 'default',
    render: (row) => h(NTag, { type: 'info' }, { default: () => row['node.role'] }),
    width: 100
  },
  {
    title: '主节点',
    key: 'master',
    sorter: 'default',
    render: (row) => h(NTag, { type: row.master === '*' ? 'success' : 'default' }, { default: () => row.master === '*' ? '是' : '否' }),
    width: 70
  },
  {
    title: '堆使用率',
    key: 'heap.percent',
    sorter: 'default',
    render: (row) => renderProgress(row, 'heap.percent'),
    width: 100
  },
  {
    title: '内存使用率',
    key: 'ram.percent',
    sorter: 'default',
    render: (row) => renderProgress(row, 'ram.percent'),
    width: 100
  },
  {
    title: '磁盘使用率',
    key: 'disk.used_percent',
    sorter: 'default',
    render: (row) => renderProgress(row, 'disk.used_percent'),
    width: 100
  },
  {
    title: 'CPU使用率',
    key: 'cpu',
    sorter: 'default',
    render: (row) => renderProgress(row, 'cpu'),
    width: 100
  },
  {
    title: '5m负载',
    key: 'load_5m',
    sorter: 'default',
    width: 60
  },
  {
    title: '内存使用',
    key: 'memory',
    render: (row) => h(NText, { depth: 3 }, { default: () => `字段: ${row.fielddataMemory} | 查询: ${row.queryCacheMemory} | 请求: ${row.requestCacheMemory} | 段: ${row.segmentsMemory}` }),
    width: 100,
    ellipsis: {  // 带提示的省略
      tooltip: true
    }
  },
  {
    title: '段总数',
    key: 'segments.count',
    sorter: 'default',
    width: 60,
    ellipsis: {  // 带提示的省略
      tooltip: true
    }
  }
]



</script>



<style scoped>

</style>
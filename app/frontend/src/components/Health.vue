<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2 style="width: 42px;">健康</h2>
      <n-button @click="getData" text :render-icon="renderIcon(RefreshOutlined)">refresh</n-button>

    </n-flex>
    <n-spin :show="loading" description="Connecting...">

      <n-table :bordered="false" :single-line="false">
        <thead>
        <tr>
          <th>健康指标</th>
          <th>值</th>
          <th>完整键</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(value, key) in data" :key="key">
          <td>{{ getLabel(key) }}</td>
          <td>
            <n-tooltip placement="left" trigger="hover">
              <template #trigger>
                <n-tag :type="getTagType(key, value)">
                  {{ value }}
                </n-tag>
              </template>
              {{ value }}
            </n-tooltip>
          </td>
          <td>{{ key }}</td>

        </tr>
        </tbody>
      </n-table>
    </n-spin>
  </n-flex>

</template>
<script setup>
import {onActivated, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {useMessage} from "naive-ui";
import {GetHealth} from "../../wailsjs/go/service/ESService";
import {renderIcon} from "../utils/common";
import {RefreshOutlined} from "@vicons/material";

const data = ref({})
const loading = ref(false)

const message = useMessage()

const selectNode = (node) => {
}
onMounted(async () => {
  emitter.on('selectNode', selectNode)
  await getData()
})

onActivated(async () => {
  // await getHealth()
})

const Clean = async () => {
  data.value = {}
}

const getData = async () => {
  loading.value = true
  const res = await GetHealth()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    data.value = res.result
  }
  console.log(data.value)
  loading.value = false

}

const getTagType = (key, value) => {
  if (['cluster_name'].includes(key)) {
    return 'success'
  }
  if (['unassigned_shards', 'delayed_unassigned_shards', 'initializing_shards'].includes(key)) {
    return 'warning'
  }

  if (key === 'timed_out') {
    return value === true ? 'error' : 'success'
  }
  if (key === 'status') {
    if (value === 'green') {
      return 'success'
    } else {
      return value === 'yellow' ? 'warning' : 'error'
    }
  }
  return 'default'
}

const getLabel = (key) => {
  const descriptions = {
    cluster_name: '集群名称',
    status: '集群健康状态（绿色、黄色、红色）',
    timed_out: '请求是否超时',
    number_of_nodes: '集群中的节点数',
    number_of_data_nodes: '集群中的数据节点数',
    active_primary_shards: '活跃的主分片数',
    active_shards: '活跃的总分片数',
    relocating_shards: '正在重新定位的分片数',
    initializing_shards: '正在初始化的分片数',
    unassigned_shards: '未分配的分片数',
    delayed_unassigned_shards: '延迟未分配的分片数',
    number_of_pending_tasks: '等待中的集群级任务数',
    number_of_in_flight_fetch: '正在进行的分片数据获取数',
    task_max_waiting_in_queue_millis: '任务在队列中的最长等待时间（毫秒）',
    active_shards_percent_as_number: '活跃分片百分比'
  }
  return descriptions[key] || '暂无说明'
}

</script>
<style scoped>

</style>
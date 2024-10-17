<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2 style="width: 42px;">健康</h2>
      <n-button @click="getHealth" type="primary">
        刷新
      </n-button>
    </n-flex>
    <n-spin :show="loading">
      <n-table :bordered="false" :single-line="false">
        <thead>
        <tr>
          <th>指标</th>
          <th>值</th>
          <th>说明</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(value, key) in clusterHealth" :key="key">
          <td>{{ key }}</td>
          <td>
            <n-tag :type="getTagType(key, value)">
              {{ value }}
            </n-tag>
          </td>
          <td>{{ getDescription(key) }}</td>
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

const clusterHealth = ref({})
const loading = ref(false)

const message = useMessage()


onMounted(async () => {
  // emitter.on('selectNode', selectNode)
})

onActivated(async () => {
  await getHealth()
})

const Clean = async () => {
  clusterHealth.value = {}
}

const getHealth = async () => {
  loading.value = true
  const res = await GetHealth()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    clusterHealth.value = res.result
  }
  console.log(clusterHealth.value)
  loading.value = false


}

const getTagType = (key, value) => {
  if (key === 'status') {
    switch (value) {
      case 'green':
        return 'success'
      case 'yellow':
        return 'warning'
      case 'red':
        return 'error'
      default:
        return 'default'
    }
  }
  return 'default'
}

const getDescription = (key) => {
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

// const selectNode = async (node) => {
//   await Clean()
//   await getHealth()
//
// }
</script>
<style scoped>

</style>
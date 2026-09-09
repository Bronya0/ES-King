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
      <h2>{{ t('health.title') }}</h2>
      <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getData">{{ t('common.refresh') }}</n-button>
    </n-flex>
    <n-spin :show="loading" :description="t('app.connecting')">
      <n-table :bordered="false" :single-line="false">
        <thead>
        <tr>
          <th>{{ t('health.metrics') }}</th>
          <th>{{ t('health.value') }}</th>
          <th>{{ t('health.fullKey') }}</th>
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
import { useI18n } from 'vue-i18n'
import {onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {useMessage} from "naive-ui";
import {GetHealth} from "../../wailsjs/go/service/ESService";
import {renderIcon} from "../utils/common";
import {RefreshOutlined} from "@vicons/material";

const { t } = useI18n()

const data = ref({})
const loading = ref(false)
const message = useMessage()

const selectNode = async (node) => {
  await getData()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  getData()
})

const getData = async () => {
  loading.value = true
  const res = await GetHealth()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    data.value = res.result
    emitter.emit('changeTitleType', getTagType("status", res.result['status']))
  }
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
    cluster_name: t('health.descriptions.cluster_name'),
    status: t('health.descriptions.status'),
    timed_out: t('health.descriptions.timed_out'),
    number_of_nodes: t('health.descriptions.number_of_nodes'),
    number_of_data_nodes: t('health.descriptions.number_of_data_nodes'),
    active_primary_shards: t('health.descriptions.active_primary_shards'),
    active_shards: t('health.descriptions.active_shards'),
    relocating_shards: t('health.descriptions.relocating_shards'),
    initializing_shards: t('health.descriptions.initializing_shards'),
    unassigned_shards: t('health.descriptions.unassigned_shards'),
    delayed_unassigned_shards: t('health.descriptions.delayed_unassigned_shards'),
    number_of_pending_tasks: t('health.descriptions.number_of_pending_tasks'),
    number_of_in_flight_fetch: t('health.descriptions.number_of_in_flight_fetch'),
    task_max_waiting_in_queue_millis: t('health.descriptions.task_max_waiting_in_queue_millis'),
    active_shards_percent_as_number: t('health.descriptions.active_shards_percent_as_number'),
  }
  return descriptions[key] || t('common.noDescription')
}

</script>
<style scoped>

</style>

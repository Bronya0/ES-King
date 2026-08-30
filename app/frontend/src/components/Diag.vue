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
      <h2>{{ t('diag.title') }}</h2>
      <n-text>{{ t('diag.desc') }}</n-text>
    </n-flex>

    <n-tabs type="line" animated v-model:value="activeTab">
      <!-- ============ 分片分布 ============ -->
      <n-tab-pane name="shards" :tab="t('diag.tabShards')">
        <n-flex vertical>
          <n-flex align="center">
            <n-input v-model:value="shardFilter" :placeholder="t('diag.filterIndex')" style="width: 240px" clearable
                     @keydown.enter="getShards"/>
            <n-select v-model:value="shardStateFilter" :options="stateFilterOptions" style="width: 160px" clearable
                      :placeholder="t('diag.filterState')"/>
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getShards">{{ t('common.refresh') }}</n-button>
            <n-button type="warning" ghost @click="explainFirstUnassigned">{{ t('diag.explainUnassigned') }}</n-button>
          </n-flex>
          <n-spin :show="shardLoading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="shardColumns"
                :data="filteredShards"
                :pagination="shardPagination"
                :max-height="480"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>
      </n-tab-pane>

      <!-- ============ 线程池 ============ -->
      <n-tab-pane name="threadPool" :tab="t('diag.tabThreadPool')">
        <n-flex vertical>
          <n-flex align="center">
            <n-input v-model:value="threadPoolFilter" :placeholder="t('diag.filterThreadPool')" style="width: 240px"
                     clearable @keydown.enter="getThreadPool"/>
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getThreadPool">{{ t('common.refresh') }}</n-button>
          </n-flex>
          <n-spin :show="threadPoolLoading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="threadPoolColumns"
                :data="filteredThreadPool"
                :pagination="threadPoolPagination"
                :max-height="480"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>
      </n-tab-pane>

      <!-- ============ 热点线程 ============ -->
      <n-tab-pane name="hotThreads" :tab="t('diag.tabHotThreads')">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :loading="hotThreadsLoading" :render-icon="renderIcon(RefreshOutlined)"
                      @click="getHotThreads">{{ t('common.refresh') }}
            </n-button>
          </n-flex>
          <n-spin :show="hotThreadsLoading" :description="t('app.loading')">
            <n-input
                v-model:value="hotThreadsText"
                type="textarea"
                readonly
                :autosize="{minRows: 20, maxRows: 30}"
                class="hot-threads-text"
            />
          </n-spin>
        </n-flex>
      </n-tab-pane>

      <!-- ============ 挂起任务 ============ -->
      <n-tab-pane name="pendingTasks" :tab="t('diag.tabPendingTasks')">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getPendingTasks">{{ t('common.refresh') }}</n-button>
          </n-flex>
          <n-spin :show="pendingLoading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="pendingColumns"
                :data="pendingData"
                :max-height="480"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>
      </n-tab-pane>
    </n-tabs>

    <!-- 分配解释 -->
    <n-modal v-model:show="explainModal.show" preset="card" :title="t('diag.explainTitle')" style="width: 720px;">
      <n-code :code="explainModal.content" language="json" show-line-numbers/>
    </n-modal>
  </n-flex>
</template>

<script setup>
import {useI18n} from 'vue-i18n'
import {computed, h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NTag, useMessage} from 'naive-ui'
import {formatBytes, formatMillis, refColumns, renderIcon} from "../utils/common";
import {RefreshOutlined} from "@vicons/material";
import {
  ExplainAllocation,
  GetHotThreads,
  GetPendingTasks,
  GetShards,
  GetThreadPool,
} from "../../wailsjs/go/service/ESService";

const {t} = useI18n()
const message = useMessage()

const activeTab = ref('shards')

// ==================== 分片 ====================
const shardData = ref([])
const shardLoading = ref(false)
const shardFilter = ref("")
const shardStateFilter = ref(null)

const stateFilterOptions = [
  {label: 'STARTED', value: 'STARTED'},
  {label: 'INITIALIZING', value: 'INITIALIZING'},
  {label: 'RELOCATING', value: 'RELOCATING'},
  {label: 'UNASSIGNED', value: 'UNASSIGNED'},
]

const filteredShards = computed(() => {
  return shardData.value.filter(row => {
    if (shardFilter.value && !(row.index || '').includes(shardFilter.value)) return false
    if (shardStateFilter.value && row.state !== shardStateFilter.value) return false
    return true
  })
})

const shardPagination = ref({
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: (page) => {
    shardPagination.value.page = page
  },
  onUpdatePageSize: (pageSize) => {
    shardPagination.value.pageSize = pageSize
    shardPagination.value.page = 1
  },
})

const getShards = async () => {
  shardLoading.value = true
  try {
    const res = await GetShards(shardFilter.value.trim())
    if (res.err !== "") {
      message.error(res.err)
    } else {
      shardData.value = res.results || []
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    shardLoading.value = false
  }
}

const explainModal = ref({
  show: false,
  content: '',
})

const showExplain = (content) => {
  explainModal.value.content = content
  explainModal.value.show = true
}

const explainShard = async (row) => {
  const res = await ExplainAllocation(row.index, parseInt(row.shard), row.prirep === 'p')
  if (res.err !== "") {
    try {
      showExplain(JSON.stringify(JSON.parse(res.err), null, 2))
    } catch {
      showExplain(res.err)
    }
    return
  }
  showExplain(JSON.stringify(res.result, null, 2))
}

const explainFirstUnassigned = () => {
  const target = shardData.value.find(row => row.state === 'UNASSIGNED')
  if (!target) {
    message.info(t('diag.noUnassigned'))
    return
  }
  explainShard(target)
}

const stateTagType = (state) => {
  if (state === 'STARTED') return 'success'
  if (state === 'INITIALIZING' || state === 'RELOCATING') return 'info'
  if (state === 'UNASSIGNED') return 'error'
  return 'default'
}

const shardColumns = computed(() => refColumns([
  {title: t('snapshot.colIndex'), key: 'index'},
  {title: t('snapshot.colShard'), key: 'shard', width: 80},
  {
    title: t('diag.colPrirep'), key: 'prirep', width: 90,
    render: (row) => h(NTag, {size: 'small', type: row.prirep === 'p' ? 'info' : 'default'},
        {default: () => row.prirep === 'p' ? 'primary' : 'replica'}),
  },
  {
    title: t('snapshot.colState'), key: 'state', width: 120,
    render: (row) => h(NTag, {size: 'small', type: stateTagType(row.state)}, {default: () => row.state}),
  },
  {title: t('index.colDocCount'), key: 'docs'},
  {
    title: t('index.colStore'), key: 'store',
    render: (row) => row.store ? formatBytes(row.store) : '',
  },
  {title: 'node', key: 'node'},
  {title: 'ip', key: 'ip', width: 130},
  {
    title: t('common.operation'), key: 'actions', width: 120,
    render: (row) => h('a', {
      style: 'cursor: pointer;',
      onClick: () => explainShard(row),
    }, {default: () => t('diag.explain')}),
  },
]))

// ==================== 线程池 ====================
const threadPoolData = ref([])
const threadPoolLoading = ref(false)
const threadPoolFilter = ref("")

const filteredThreadPool = computed(() => {
  return threadPoolData.value.filter(row => {
    if (threadPoolFilter.value &&
        !`${row.name || ''}`.includes(threadPoolFilter.value) &&
        !`${row.node_name || ''}`.includes(threadPoolFilter.value)) return false
    return true
  })
})

const threadPoolPagination = ref({
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: (page) => {
    threadPoolPagination.value.page = page
  },
  onUpdatePageSize: (pageSize) => {
    threadPoolPagination.value.pageSize = pageSize
    threadPoolPagination.value.page = 1
  },
})

const getThreadPool = async () => {
  threadPoolLoading.value = true
  try {
    const res = await GetThreadPool()
    if (res.err !== "") {
      message.error(res.err)
    } else {
      threadPoolData.value = res.results || []
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    threadPoolLoading.value = false
  }
}

const threadPoolColumns = computed(() => refColumns([
  {title: t('nodes.colName'), key: 'node_name'},
  {title: t('diag.colPoolName'), key: 'name'},
  {title: t('diag.colActive'), key: 'active'},
  {title: t('diag.colQueue'), key: 'queue'},
  {title: t('diag.colRejected'), key: 'rejected'},
  {title: t('diag.colSize'), key: 'size'},
  {title: t('diag.colType'), key: 'type'},
]))

// ==================== 热点线程 ====================
const hotThreadsText = ref('')
const hotThreadsLoading = ref(false)

const getHotThreads = async () => {
  hotThreadsLoading.value = true
  try {
    const res = await GetHotThreads()
    if (res.err !== "") {
      message.error(res.err)
    } else {
      hotThreadsText.value = res.result || ''
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    hotThreadsLoading.value = false
  }
}

// ==================== 挂起任务 ====================
const pendingData = ref([])
const pendingLoading = ref(false)

const pendingColumns = computed(() => refColumns([
  {title: t('diag.colInsertOrder'), key: 'insert_order'},
  {title: t('diag.colPriority'), key: 'priority'},
  {title: t('task.colAction'), key: 'source'},
  {
    title: t('diag.colTimeInQueue'), key: 'time_in_queue_millis',
    render: (row) => formatMillis(row.time_in_queue_millis),
  },
]))

const getPendingTasks = async () => {
  pendingLoading.value = true
  try {
    const res = await GetPendingTasks()
    if (res.err !== "") {
      message.error(res.err)
    } else {
      pendingData.value = res.results || []
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    pendingLoading.value = false
  }
}

// ==================== 生命周期 ====================
const selectNode = () => {
  shardData.value = []
  threadPoolData.value = []
  hotThreadsText.value = ''
  pendingData.value = []
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  getShards()
  getThreadPool()
})
</script>

<style scoped>
.hot-threads-text :deep(textarea) {
  font-family: Consolas, Monaco, monospace;
}
</style>

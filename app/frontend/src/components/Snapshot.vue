<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2>{{ t('snapshot.title') }}</h2>
    </n-flex>
    <n-tabs type="line" animated>
      <n-tab-pane name="repo" :tab="t('snapshot.tabRepo')">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getRepos">{{ t('common.refresh') }}</n-button>
            <n-button :render-icon="renderIcon(AddFilled)" @click="repoForm.show = true">{{ t('snapshot.createRepo') }}</n-button>
          </n-flex>
          <n-spin :show="repoLoading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="repoColumns"
                :data="repoData"
                :max-height="550"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>

        <n-modal v-model:show="repoForm.show" preset="dialog" :title="t('snapshot.createRepo')" :positive-text="t('common.confirm')" :negative-text="t('common.cancel')"
                 @positive-click="handleCreateRepo">
          <n-form label-placement="left" label-width="auto">
            <n-form-item :label="t('snapshot.repoName')">
              <n-input v-model:value="repoForm.name" placeholder="my_backup_repo"/>
            </n-form-item>
            <n-form-item :label="t('snapshot.repoType')">
              <n-select v-model:value="repoForm.type" :options="repoTypeOptions"/>
            </n-form-item>
            <n-form-item :label="t('snapshot.repoSettings')">
              <n-input v-model:value="repoForm.settings" type="textarea" :autosize="{minRows: 3, maxRows: 8}"
                       placeholder='例如: {"location": "/mount/backups/my_backup"}' />
            </n-form-item>
          </n-form>
        </n-modal>
      </n-tab-pane>

      <n-tab-pane name="snapshot" :tab="t('snapshot.tabSnapshot')">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getSnapshots">{{ t('common.refresh') }}</n-button>
            <n-button :render-icon="renderIcon(AddFilled)" @click="snapForm.show = true">{{ t('snapshot.createSnapshot') }}</n-button>
          </n-flex>
          <n-spin :show="snapLoading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="snapColumns"
                :data="snapData"
                :max-height="550"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>

        <n-modal v-model:show="snapForm.show" preset="dialog" :title="t('snapshot.createSnapshot')" :positive-text="t('common.confirm')" :negative-text="t('common.cancel')"
                 @positive-click="handleCreateSnapshot">
          <n-form label-placement="left" label-width="auto">
            <n-form-item :label="t('snapshot.repoName')">
              <n-select v-model:value="snapForm.repository" :options="repoSelectOptions"
                        :placeholder="t('snapshot.selectRepo')"/>
            </n-form-item>
            <n-form-item :label="t('snapshot.snapshotName')">
              <n-input v-model:value="snapForm.snapshot" placeholder="snapshot_2026"/>
            </n-form-item>
            <n-form-item :label="t('snapshot.indices')">
              <n-input v-model:value="snapForm.indices" :placeholder="t('snapshot.allIndices')"/>
            </n-form-item>
            <n-form-item :label="t('snapshot.includeGlobalState')">
              <n-switch v-model:value="snapForm.includeGlobalState"/>
            </n-form-item>
          </n-form>
          <n-text depth="3">{{ t('snapshot.asyncCreateHint') }}</n-text>
        </n-modal>

        <n-modal v-model:show="snapDetail.show" preset="card" :title="t('common.details')" style="width: 600px; max-width: 90vw; text-align: left;">
          <n-scrollbar style="max-height: 65vh;">
            <n-code :code="snapDetail.content" language="json" show-line-numbers word-wrap style="text-align: left;"/>
          </n-scrollbar>
          <template #footer>
            <n-flex justify="end">
              <n-button @click="snapDetail.show = false">{{ t('common.close') }}</n-button>
            </n-flex>
          </template>
        </n-modal>
      </n-tab-pane>

      <n-tab-pane name="restore" :tab="t('snapshot.tabRestore')">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getRestoreStatus">{{ t('common.refresh') }}
            </n-button>
          </n-flex>

          <n-card :title="t('snapshot.tabRestore')" size="small">
            <n-form label-placement="left" label-width="auto">
              <n-form-item :label="t('snapshot.repoName')">
                <n-select v-model:value="restoreForm.repository" :options="repoSelectOptions"
                          :placeholder="t('snapshot.selectRepo')" @update:value="onRestoreRepoChange"/>
              </n-form-item>
              <n-form-item :label="t('snapshot.snapshotName')">
                <n-select v-model:value="restoreForm.snapshot" :options="restoreSnapOptions"
                          :placeholder="t('snapshot.selectSnapshot')"/>
              </n-form-item>
              <n-form-item :label="t('snapshot.indices')">
                <n-input v-model:value="restoreForm.indices" :placeholder="t('snapshot.allIndices')"/>
              </n-form-item>
              <n-form-item label="重命名模式">
                <n-input v-model:value="restoreForm.renamePattern" placeholder="例如: index_(.+)"/>
              </n-form-item>
              <n-form-item label="重命名替换">
                <n-input v-model:value="restoreForm.renameReplacement" placeholder="例如: restored_index_$1"/>
              </n-form-item>
              <n-form-item :label="t('snapshot.includeGlobalState')">
                <n-switch v-model:value="restoreForm.includeGlobalState"/>
              </n-form-item>
            </n-form>
            <n-flex>
              <n-button type="warning" @click="handleRestore">{{ t('common.execute') }}</n-button>
            </n-flex>
            <n-text depth="3">
              {{ t('snapshot.restoreWarning') }}
            </n-text>
          </n-card>

          <n-card :title="t('common.result')" size="small" style="margin-top: 12px;">
            <n-spin :show="restoreStatusLoading">
              <n-data-table
                  :bordered="false"
                  :columns="restoreColumns"
                  :data="restoreStatusData"
                  :max-height="300"
                  size="small"
                  striped
              />
            </n-spin>
          </n-card>
        </n-flex>
      </n-tab-pane>

      <n-tab-pane name="slm" :tab="t('snapshot.tabSlm')">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getSLMPolicies">{{ t('common.refresh') }}</n-button>
            <n-button :render-icon="renderIcon(AddFilled)" @click="slmForm.show = true">{{ t('snapshot.createPolicy') }}</n-button>
          </n-flex>
          <n-spin :show="slmLoading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="slmColumns"
                :data="slmData"
                :max-height="550"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>

        <n-modal v-model:show="slmForm.show" preset="dialog" :title="t('snapshot.createPolicy')" :positive-text="t('common.confirm')"
                 :negative-text="t('common.cancel')" @positive-click="handleCreateSLM" style="width: 520px;">
          <n-form label-placement="left" label-width="auto">
            <n-form-item :label="t('snapshot.colPolicyId')">
              <n-input v-model:value="slmForm.policyId" placeholder="daily-snapshots"/>
            </n-form-item>
            <n-form-item :label="t('snapshot.colSnapshotNameTemplate')">
              <n-input v-model:value="slmForm.name" placeholder="<daily-snap-{now/d}>"/>
            </n-form-item>
            <n-form-item :label="t('snapshot.colSchedule')">
              <n-input v-model:value="slmForm.schedule" placeholder="0 30 1 * * ?（每天凌晨1:30）"/>
            </n-form-item>
            <n-form-item :label="t('snapshot.repoName')">
              <n-select v-model:value="slmForm.repository" :options="repoSelectOptions"
                        :placeholder="t('snapshot.selectRepo')"/>
            </n-form-item>
            <n-form-item :label="t('snapshot.indices')">
              <n-input v-model:value="slmForm.indices" :placeholder="t('snapshot.allIndices')"/>
            </n-form-item>
            <n-form-item label="过期时间">
              <n-input v-model:value="slmForm.expireAfter" placeholder="例如: 30d"/>
            </n-form-item>
            <n-form-item label="最少保留数">
              <n-input-number v-model:value="slmForm.minCount" :min="0" placeholder="5"/>
            </n-form-item>
            <n-form-item label="最多保留数">
              <n-input-number v-model:value="slmForm.maxCount" :min="0" placeholder="50"/>
            </n-form-item>
          </n-form>
        </n-modal>
      </n-tab-pane>

      <n-tab-pane name="ilm" :tab="t('snapshot.tabIlm')">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getILMPolicies">{{ t('common.refresh') }}</n-button>
            <n-button :render-icon="renderIcon(AddFilled)" @click="openCreateILM">{{ t('snapshot.createIlmPolicy') }}</n-button>
          </n-flex>
          <n-spin :show="ilmLoading" :description="t('app.loading')">
            <n-data-table
                :bordered="false"
                :columns="ilmColumns"
                :data="ilmData"
                :max-height="550"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>

        <n-modal v-model:show="ilmForm.show" preset="card" :title="t('snapshot.createIlmPolicy')" style="width: 640px;">
          <n-form label-placement="top">
            <n-form-item :label="t('snapshot.colPolicyId')">
              <n-input v-model:value="ilmForm.policyId" placeholder="logs-lifecycle"/>
            </n-form-item>
            <n-form-item :label="t('snapshot.ilmPolicyBody')">
              <n-input v-model:value="ilmForm.policy" type="textarea" :autosize="{minRows: 12, maxRows: 24}"
                       class="json-editor-input"
                       :placeholder='JSON.stringify({"phases": {"hot": {"actions": {}}, "delete": {"min_age": "30d", "actions": {"delete": {}}}}}, null, 2)'/>
            </n-form-item>
          </n-form>
          <n-text depth="3">{{ t('snapshot.ilmPolicyHint') }}</n-text>
          <template #footer>
            <n-flex justify="end">
              <n-button @click="ilmForm.show = false">{{ t('common.cancel') }}</n-button>
              <n-button type="primary" :loading="ilmForm.saving" @click="handleCreateILM">{{ t('common.save') }}</n-button>
            </n-flex>
          </template>
        </n-modal>

        <n-modal v-model:show="ilmDetail.show" preset="card" :title="ilmDetail.title" style="width: 680px; max-width: 90vw; text-align: left;">
          <n-scrollbar style="max-height: 65vh;">
            <n-code :code="ilmDetail.content" language="json" show-line-numbers word-wrap style="text-align: left;"/>
          </n-scrollbar>
          <template #footer>
            <n-flex justify="end">
              <n-button @click="ilmDetail.show = false">{{ t('common.close') }}</n-button>
            </n-flex>
          </template>
        </n-modal>
      </n-tab-pane>
    </n-tabs>
  </n-flex>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import {computed, h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NTag, useDialog, useMessage} from 'naive-ui'
import {renderIcon} from "../utils/common";
import {RefreshOutlined, AddFilled} from "@vicons/material";
import {
  GetSnapshots, GetSnapshotRepositories, CreateSnapshotRepository, DeleteSnapshotRepository,
  VerifySnapshotRepository, CreateSnapshot, DeleteSnapshot, GetSnapshotDetail,
  RestoreSnapshot, GetSnapshotRestoreStatus,
  GetSLMPolicies, CreateSLMPolicy, DeleteSLMPolicy, ExecuteSLMPolicy,
  GetILMPolicies, CreateILMPolicy, DeleteILMPolicy,
} from "../../wailsjs/go/service/ESService";

const { t } = useI18n()
const message = useMessage()
const dialog = useDialog()

// ==================== 仓库管理 ====================
const repoLoading = ref(false)
const repoData = ref([])

const repoForm = ref({
  show: false,
  name: '',
  type: 'fs',
  settings: '',
})

const repoTypeOptions = [
  {label: 'fs ' + t('snapshot.repoType'), value: 'fs'},
  {label: 's3 (AWS S3)', value: 's3'},
  {label: 'hdfs (Hadoop HDFS)', value: 'hdfs'},
  {label: 'azure (Azure Blob)', value: 'azure'},
  {label: 'gcs (Google Cloud Storage)', value: 'gcs'},
  {label: 'url ' + t('snapshot.repoType'), value: 'url'},
]

const repoSelectOptions = computed(() => {
  return repoData.value.map(r => ({label: r.name, value: r.name}))
})

const getRepos = async () => {
  repoLoading.value = true
  const res = await GetSnapshotRepositories()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    repoData.value = res.results || []
  }
  repoLoading.value = false
}

const handleCreateRepo = async () => {
  const res = await CreateSnapshotRepository(repoForm.value.name, repoForm.value.type, repoForm.value.settings)
  if (res.err !== "") {
    message.error(res.err)
    return false
  }
  message.success(t('snapshot.repoCreated'))
  repoForm.value = {show: false, name: '', type: 'fs', settings: ''}
  await getRepos()
}

const handleDeleteRepo = (name) => {
  dialog.warning({
    title: t('common.warning'),
    content: t('snapshot.confirmDeleteRepo', { name }),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      const res = await DeleteSnapshotRepository(name)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success(t('snapshot.repoDeleted'))
        await getRepos()
      }
    }
  })
}

const handleVerifyRepo = async (name) => {
  const res = await VerifySnapshotRepository(name)
  if (res.err !== "") {
    message.error(t('snapshot.verifyFailed', { msg: res.err }))
  } else {
    message.success(t('snapshot.repoVerified'))
  }
}

const repoColumns = computed(() => [
  {title: t('snapshot.colRepoName'), key: 'name', width: 180},
  {title: t('snapshot.colRepoType'), key: 'type', width: 100},
  {
    title: t('snapshot.colSettings'),
    key: 'settings',
    render: (row) => row.settings ? JSON.stringify(row.settings) : '-',
  },
  {
    title: t('common.operation'),
    key: 'actions',
    width: 180,
    render: (row) => h('div', {style: 'display: flex; gap: 8px;'}, [
      h(NButton, {size: 'small', quaternary: true, type: 'info', onClick: () => handleVerifyRepo(row.name)},
          {default: () => t('common.verify')}),
      h(NButton, {size: 'small', quaternary: true, type: 'error', onClick: () => handleDeleteRepo(row.name)},
          {default: () => t('common.delete')}),
    ])
  }
])

// ==================== 快照管理 ====================
const snapLoading = ref(false)
const snapData = ref([])

const snapForm = ref({
  show: false,
  repository: null,
  snapshot: '',
  indices: '',
  includeGlobalState: false,
})

const snapDetail = ref({
  show: false,
  content: '',
})

const getSnapshots = async () => {
  snapLoading.value = true
  const res = await GetSnapshots()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    snapData.value = (res.results || []).sort((a, b) => {
      return (b.start_time || '').localeCompare(a.start_time || '')
    })
  }
  snapLoading.value = false
}

const handleCreateSnapshot = async () => {
  const res = await CreateSnapshot(
      snapForm.value.repository,
      snapForm.value.snapshot,
      snapForm.value.indices,
      snapForm.value.includeGlobalState
  )
  if (res.err !== "") {
    message.error(res.err)
    return false
  }
  message.success(t('snapshot.snapshotCreated'))
  snapForm.value = {show: false, repository: null, snapshot: '', indices: '', includeGlobalState: false}
  await getSnapshots()
}

const handleDeleteSnapshot = (repository, snapshot) => {
  dialog.warning({
    title: t('common.warning'),
    content: t('snapshot.confirmDeleteSnapshot', { repo: repository, snap: snapshot }),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      const res = await DeleteSnapshot(repository, snapshot)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success(t('snapshot.snapshotDeleted'))
        await getSnapshots()
      }
    }
  })
}

const handleViewDetail = async (repository, snapshot) => {
  const res = await GetSnapshotDetail(repository, snapshot)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    snapDetail.value.content = JSON.stringify(res.result, null, 2)
    snapDetail.value.show = true
  }
}

const snapColumns = computed(() => [
  {title: t('snapshot.colSnapshotName'), key: 'snapshot', width: 160},
  {title: t('snapshot.colRepo'), key: 'repository', width: 130},
  {
    title: t('snapshot.colState'), key: 'state', width: 110,
    render: (row) => h(NTag, {
      size: 'small',
      type: row.state === 'SUCCESS' ? "success" : row.state === 'FAILED' ? "error" :
          row.state === 'IN_PROGRESS' ? "info" : "warning"
    }, {default: () => row.state}),
  },
  {title: t('snapshot.colStartTime'), key: 'start_time', width: 170},
  {title: t('snapshot.colEndTime'), key: 'end_time', width: 170},
  {
    title: t('snapshot.colIndices'), key: 'indices', width: 80,
    render: (row) => Array.isArray(row.indices) ? row.indices.length : 0,
  },
  {title: t('snapshot.colTotalShards'), key: 'total_shards', width: 80},
  {title: t('snapshot.colSuccessShards'), key: 'successful_shards', width: 90},
  {
    title: t('common.operation'), key: 'actions', width: 200,
    render: (row) => h('div', {style: 'display: flex; gap: 8px;'}, [
      h(NButton, {
        size: 'small', quaternary: true, type: 'info',
        onClick: () => handleViewDetail(row.repository, row.snapshot)
      }, {default: () => t('common.details')}),
      h(NButton, {
        size: 'small', quaternary: true, type: 'warning',
        onClick: () => {
          restoreForm.value.repository = row.repository
          restoreForm.value.snapshot = row.snapshot
          message.info(t('rest.dumpToRestore'))
        }
      }, {default: () => t('common.execute')}),
      h(NButton, {
        size: 'small', quaternary: true, type: 'error',
        onClick: () => handleDeleteSnapshot(row.repository, row.snapshot)
      }, {default: () => t('common.delete')}),
    ])
  }
])

// ==================== 快照恢复 ====================
const restoreForm = ref({
  repository: null,
  snapshot: null,
  indices: '',
  renamePattern: '',
  renameReplacement: '',
  includeGlobalState: false,
})

const restoreSnapOptions = ref([])
const restoreStatusLoading = ref(false)
const restoreStatusData = ref([])

const onRestoreRepoChange = async (repo) => {
  restoreSnapOptions.value = []
  restoreForm.value.snapshot = null
  if (snapData.value.length === 0) {
    await getSnapshots()
  }
  const filtered = snapData.value.filter(s => s.repository === repo && s.state === 'SUCCESS')
  restoreSnapOptions.value = filtered.map(s => ({label: s.snapshot, value: s.snapshot}))
}

const handleRestore = () => {
  if (!restoreForm.value.repository || !restoreForm.value.snapshot) {
    message.warning(t('snapshot.selectRepoAndSnap'))
    return
  }
  dialog.warning({
    title: t('common.warning'),
    content: t('snapshot.confirmRestore', { repo: restoreForm.value.repository, snap: restoreForm.value.snapshot }),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      const res = await RestoreSnapshot(
          restoreForm.value.repository,
          restoreForm.value.snapshot,
          restoreForm.value.indices,
          restoreForm.value.renamePattern,
          restoreForm.value.renameReplacement,
          restoreForm.value.includeGlobalState
      )
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success(t('snapshot.restoreSubmitted'))
        await getRestoreStatus()
      }
    }
  })
}

const getRestoreStatus = async () => {
  restoreStatusLoading.value = true
  const res = await GetSnapshotRestoreStatus()
  if (res.err !== "") {
    message.error(res.err)
    restoreStatusData.value = []
  } else {
    const data = res.result || {}
    const list = []
    for (const [indexName, info] of Object.entries(data)) {
      const shards = info.shards || []
      for (const shard of shards) {
        list.push({
          index: indexName,
          shard: shard.id,
          type: shard.type,
          stage: shard.stage,
          source_node: shard.source?.name || '-',
          target_node: shard.target?.name || '-',
          bytes_recovered: shard.index?.size?.recovered_in_bytes || 0,
          bytes_total: shard.index?.size?.total_in_bytes || 0,
        })
      }
    }
    restoreStatusData.value = list
  }
  restoreStatusLoading.value = false
}

const restoreColumns = computed(() => [
  {title: t('snapshot.colIndex'), key: 'index', width: 160},
  {title: t('snapshot.colShard'), key: 'shard', width: 60},
  {title: t('snapshot.colType'), key: 'type', width: 100},
  {
    title: t('snapshot.colStage'), key: 'stage', width: 100,
    render: (row) => h(NTag, {
      size: 'small',
      type: row.stage === 'DONE' ? 'success' : row.stage === 'INDEX' ? 'info' : 'warning'
    }, {default: () => row.stage})
  },
  {title: t('snapshot.colSourceNode'), key: 'source_node', width: 120},
  {title: t('snapshot.colTargetNode'), key: 'target_node', width: 120},
  {
    title: t('snapshot.colProgress'), key: 'progress', width: 120,
    render: (row) => {
      if (row.bytes_total === 0) return '-'
      const pct = Math.round(row.bytes_recovered / row.bytes_total * 100)
      return pct + '%'
    }
  },
])

// ==================== SLM 策略管理 ====================
const slmLoading = ref(false)
const slmData = ref([])

const slmForm = ref({
  show: false,
  policyId: '',
  name: '<daily-snap-{now/d}>',
  schedule: '0 30 1 * * ?',
  repository: null,
  indices: '',
  expireAfter: '30d',
  minCount: 5,
  maxCount: 50,
})

const getSLMPolicies = async () => {
  slmLoading.value = true
  const res = await GetSLMPolicies()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    slmData.value = res.results || []
  }
  slmLoading.value = false
}

const handleCreateSLM = async () => {
  const f = slmForm.value
  const res = await CreateSLMPolicy(
      f.policyId, f.name, f.schedule, f.repository, f.indices,
      f.expireAfter, f.minCount || 0, f.maxCount || 0
  )
  if (res.err !== "") {
    message.error(res.err)
    return false
  }
  message.success(t('snapshot.policyCreated'))
  slmForm.value = {
    show: false, policyId: '', name: '<daily-snap-{now/d}>', schedule: '0 30 1 * * ?',
    repository: null, indices: '', expireAfter: '30d', minCount: 5, maxCount: 50
  }
  await getSLMPolicies()
}

const handleDeleteSLM = (policyId) => {
  dialog.warning({
    title: t('common.warning'),
    content: t('snapshot.confirmDeletePolicy', { name: policyId }),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      const res = await DeleteSLMPolicy(policyId)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success(t('snapshot.policyDeleted'))
        await getSLMPolicies()
      }
    }
  })
}

const handleExecuteSLM = (policyId) => {
  dialog.info({
    title: t('common.warning'),
    content: t('snapshot.confirmExecutePolicy', { name: policyId }),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      const res = await ExecuteSLMPolicy(policyId)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success(t('snapshot.policyExecuted'))
      }
    }
  })
}

const slmColumns = computed(() => [
  {title: t('snapshot.colPolicyId'), key: 'name', width: 160},
  {
    title: t('snapshot.colPolicyRepo'), key: 'repository', width: 130,
    render: (row) => (row.policy && row.policy.repository) || '-'
  },
  {
    title: t('snapshot.colSchedule'), key: 'schedule', width: 160,
    render: (row) => (row.policy && row.policy.schedule) || '-'
  },
  {
    title: t('snapshot.colSnapshotNameTemplate'), key: 'snapshot_name', width: 200,
    render: (row) => (row.policy && row.policy.name) || '-'
  },
  {
    title: t('snapshot.colNextExec'), key: 'next_execution_millis', width: 170,
    render: (row) => row.next_execution ? row.next_execution : '-'
  },
  {
    title: t('snapshot.colLastSuccess'), key: 'last_success', width: 170,
    render: (row) => {
      if (row.last_success && row.last_success.time) return row.last_success.time
      return '-'
    }
  },
  {
    title: t('snapshot.colLastFailure'), key: 'last_failure', width: 170,
    render: (row) => {
      if (row.last_failure && row.last_failure.time) {
        return h(NTag, {size: 'small', type: 'error'}, {default: () => row.last_failure.time})
      }
      return '-'
    }
  },
  {
    title: t('common.operation'), key: 'actions', width: 180,
    render: (row) => h('div', {style: 'display: flex; gap: 8px;'}, [
      h(NButton, {
        size: 'small', quaternary: true, type: 'info',
        onClick: () => handleExecuteSLM(row.name)
      }, {default: () => t('common.execute')}),
      h(NButton, {
        size: 'small', quaternary: true, type: 'error',
        onClick: () => handleDeleteSLM(row.name)
      }, {default: () => t('common.delete')}),
    ])
  }
])

// ==================== ILM 索引生命周期管理 ====================
const ilmLoading = ref(false)
const ilmData = ref([])

const ilmForm = ref({
  show: false,
  policyId: '',
  policy: '',
  saving: false,
})

const ilmDetail = ref({
  show: false,
  title: '',
  content: '',
})

const getILMPolicies = async () => {
  ilmLoading.value = true
  try {
    const res = await GetILMPolicies()
    if (res.err !== "") {
      message.error(res.err)
    } else {
      ilmData.value = (res.results || []).sort((a, b) => (a.name || '').localeCompare(b.name || ''))
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    ilmLoading.value = false
  }
}

const openCreateILM = () => {
  ilmForm.value = {show: true, policyId: '', policy: '', saving: false}
}

const handleCreateILM = async () => {
  if (!ilmForm.value.policyId || !ilmForm.value.policy) {
    message.warning(t('snapshot.ilmNeedIdAndBody'))
    return
  }
  ilmForm.value.saving = true
  try {
    const res = await CreateILMPolicy(ilmForm.value.policyId, ilmForm.value.policy)
    if (res.err !== "") {
      message.error(res.err)
    } else {
      message.success(t('snapshot.ilmPolicyCreated'))
      ilmForm.value.show = false
      await getILMPolicies()
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    ilmForm.value.saving = false
  }
}

const viewILMDetail = (row) => {
  ilmDetail.value = {
    show: true,
    title: row.name,
    content: JSON.stringify({policy: row.policy, in_use_by: row.in_use_by}, null, 2),
  }
}

const handleDeleteILM = (policyId) => {
  dialog.warning({
    title: t('common.warning'),
    content: t('snapshot.confirmDeleteIlmPolicy', {name: policyId}),
    positiveText: t('common.confirm'),
    negativeText: t('common.cancel'),
    onPositiveClick: async () => {
      const res = await DeleteILMPolicy(policyId)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success(t('snapshot.ilmPolicyDeleted'))
        await getILMPolicies()
      }
    }
  })
}

const renderPhases = (row) => {
  const phases = row.policy && row.policy.phases
  if (!phases || typeof phases !== 'object') return '-'
  return Object.keys(phases).join(', ')
}

const renderIlmIndices = (row) => {
  const indices = row.in_use_by && row.in_use_by.indices
  if (!Array.isArray(indices) || indices.length === 0) return '-'
  return indices.join(', ')
}

const ilmColumns = computed(() => [
  {title: t('snapshot.colPolicyId'), key: 'name', width: 160},
  {
    title: t('snapshot.ilmPhases'), key: 'phases',
    render: (row) => renderPhases(row),
  },
  {
    title: t('snapshot.ilmIndicesInUse'), key: 'in_use_by',
    render: (row) => renderIlmIndices(row),
  },
  {
    title: t('snapshot.ilmModifiedDate'), key: 'modified_date', width: 170,
    render: (row) => row.modified_date || '-',
  },
  {
    title: t('common.operation'), key: 'actions', width: 180,
    render: (row) => h('div', {style: 'display: flex; gap: 8px;'}, [
      h(NButton, {size: 'small', quaternary: true, type: 'info', onClick: () => viewILMDetail(row)},
          {default: () => t('common.details')}),
      h(NButton, {size: 'small', quaternary: true, type: 'error', onClick: () => handleDeleteILM(row.name)},
          {default: () => t('common.delete')}),
    ])
  }
])

// ==================== 生命周期 ====================
const selectNode = async () => {
  repoData.value = []
  snapData.value = []
  slmData.value = []
  ilmData.value = []
  await loadAllData()
}

const loadAllData = async () => {
  await getRepos()
  await getSnapshots()
  await getSLMPolicies()
  await getILMPolicies()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  loadAllData()
})
</script>

<style scoped>
.json-editor-input :deep(textarea) {
  font-family: Consolas, Monaco, monospace;
}
</style>

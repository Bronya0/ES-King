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
      <h2>{{ t('nodes.title') }}</h2>
      <n-text>{{ t('nodes.total', { count: data.length }) }}</n-text>
      <n-button :render-icon="renderIcon(RefreshOutlined)" @click="getData">{{ t('common.refresh') }}</n-button>
      <n-button :render-icon="renderIcon(DriveFileMoveTwotone)" @click="downloadAllDataCsv">{{ t('common.exportCsv') }}</n-button>
      <n-text>{{ t('nodes.clusterName', { name: cluster_name }) }}</n-text>
    </n-flex>
    <n-spin :show="loading" :description="t('app.connecting')">
      <n-data-table
          ref="tableRef"
          :bordered="false"
          :columns="refColumns(columns)"
          :data="data"
          :pagination="pagination"
          size="small"
          striped
      />
    </n-spin>
  </n-flex>
</template>
<script setup>
import { useI18n } from 'vue-i18n'
import {computed, h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDataTable, NFlex, NProgress, NTag, NText, NTooltip, useMessage} from 'naive-ui'
import {
  createCsvContent,
  download_file,
  formatBytes,
  formatMillis, formatMillisToDays,
  formatNumber,
  refColumns,
  renderIcon
} from "../utils/common";
import {DriveFileMoveTwotone, RefreshOutlined} from "@vicons/material";
import {GetNodes} from "../../wailsjs/go/service/ESService";

const { t } = useI18n()

const selectNode = async (node) => {
  await getData()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  getData()
})

const loading = ref(false)
const data = ref([])
const message = useMessage()
const tableRef = ref();
const cluster_name = ref("");

const getData = async () => {
  loading.value = true;
  const res = await GetNodes();
  if (res.err !== "") {
    message.error(res.err);
    loading.value = false;
    return;
  }
  cluster_name.value = res.result.cluster_name;
  const nodesData = res.result.nodes || {};

  const masterEligibleNodes = Object.keys(nodesData).filter(id => nodesData[id].roles?.includes('master'));
  const masterNodeId = masterEligibleNodes.length > 0 ? masterEligibleNodes[0] : null;

  const flattenedData = Object.values(nodesData).map(node => {
    const diskTotal = node.fs?.total?.total_in_bytes ?? 0;
    const diskFree = node.fs?.total?.available_in_bytes ?? 0;
    const diskUsedPercent = diskTotal > 0 ? Math.round(((diskTotal - diskFree) / diskTotal) * 100) : 0;

    const indices = node.indices ?? {};
    const search = indices.search ?? {};
    const merges = indices.merges ?? {};
    const query_cache = indices.query_cache ?? {};
    const fielddata = indices.fielddata ?? {};
    const request_cache = indices.request_cache ?? {};
    const segments = indices.segments ?? {};
    const jvm = node.jvm ?? {};
    const jvm_mem = jvm.mem ?? {};
    const os_cpu = node.os?.cpu ?? {};
    const process = node.process ?? {};
    const fs_total = node.fs?.total ?? {};
    const fs_io = node.fs?.io_stats?.total ?? {};

    return {
      name: node.name,
      ip: node.transport_address?.split(':')[0] ?? 'N/A',
      roles: node.roles || [],
      is_master: node.name === nodesData[masterNodeId]?.name,
      uptime: jvm.uptime_in_millis ?? 0,
      docs_count: indices.docs?.count ?? 0,
      store_size: indices.store?.size_in_bytes ?? 0,
      disk_total: diskTotal,
      disk_percent: diskUsedPercent,
      load_5m: os_cpu.load_average?.['5m'] ?? 0,
      heap_used_in_bytes: jvm_mem.heap_used_in_bytes ?? 0,
      heap_max_in_bytes: jvm_mem.heap_max_in_bytes ?? 0,
      heap_percent: jvm_mem.heap_used_percent ?? 0,
      segments_count: segments.count ?? 0,
      stats_search: {
        "查询总数": formatNumber(search.query_total ?? 0),
        "查询耗时": formatMillis(search.query_time_in_millis ?? 0),
        "拉取总数": formatNumber(search.fetch_total ?? 0),
        "拉取耗时": formatMillis(search.fetch_time_in_millis ?? 0),
        "滚动总数": formatNumber(search.scroll_total ?? 0),
        "滚动耗时": formatMillis(search.scroll_time_in_millis ?? 0),
      },
      stats_merges: {
        "合并总数": formatNumber(merges.total ?? 0),
        "合并总耗时": formatMillis(merges.total_time_in_millis ?? 0),
        "合并文档总数": formatNumber(merges.total_docs ?? 0),
        "合并总大小": formatBytes(merges.total_size_in_bytes ?? 0),
        "当前合并数": merges.current ?? 0,
      },
      stats_cache: `查询缓存: ${formatBytes(query_cache.memory_size_in_bytes ?? 0)} |
      Fielddata: ${formatBytes(fielddata.memory_size_in_bytes ?? 0)} |
      请求缓存: ${formatBytes(request_cache.memory_size_in_bytes ?? 0)} |
      段内存: ${formatBytes(segments.memory_in_bytes ?? 0)}`,
      stats_cache_size: (query_cache.memory_size_in_bytes ?? 0) + (fielddata.memory_size_in_bytes ?? 0) + (request_cache.memory_size_in_bytes ?? 0)
          + (segments.memory_in_bytes ?? 0),
      stats_segments: {
        "段总数": formatNumber(segments.count ?? 0),
        "总内存占用": formatBytes(segments.memory_in_bytes ?? 0),
        "词项 (Terms)": formatBytes(segments.terms_memory_in_bytes ?? 0),
        "存储字段 (Stored Fields)": formatBytes(segments.stored_fields_memory_in_bytes ?? 0),
        "Doc Values": formatBytes(segments.doc_values_memory_in_bytes ?? 0),
        "Norms": formatBytes(segments.norms_memory_in_bytes ?? 0),
      },
      stats_process: {
        "打开文件描述符": `${formatNumber(process.open_file_descriptors ?? 0)} / ${formatNumber(process.max_file_descriptors ?? 0)}`,
        "进程CPU使用率": `${process.cpu?.percent ?? 0}%`,
        "虚拟内存占用": formatBytes(process.mem?.total_virtual_in_bytes ?? 0),
      },
      stats_fs: {
        "总空间": formatBytes(fs_total.total_in_bytes ?? 0),
        "可用空间": formatBytes(fs_total.available_in_bytes ?? 0),
        "IO读操作": formatNumber(fs_io.read_operations ?? 0),
        "IO写操作": formatNumber(fs_io.write_operations ?? 0),
        "IO读流量": formatBytes((fs_io.read_kilobytes ?? 0) * 1024),
        "IO写流量": formatBytes((fs_io.write_kilobytes ?? 0) * 1024),
      }
    };
  });

  flattenedData.sort((a, b) => (b.heap_percent ?? 0) - (a.heap_percent ?? 0));
  data.value = flattenedData;
  loading.value = false;
};

function createTooltipContent(stats, formatValueAsBytes = false) {
  return h(NFlex, { vertical: true, style: { maxWidth: '400px', textAlign: 'left'} }, () =>
      Object.entries(stats).map(([key, value]) =>
          h(NText, null, () => `${key}: ${formatValueAsBytes ? formatBytes(value) : value}`)
      )
  );
}

const getProgressType = (value) => {
  const numValue = Number(value)
  if (numValue < 60) return 'success'
  if (numValue < 80) return 'warning'
  return 'error'
}

const downloadAllDataCsv = () => {
  if (!data.value || data.value.length === 0) {
    message.warning(t('nodes.noData'));
    return;
  }

  const exportColumns = [
    { title: t('nodes.csvColName'), key: 'name' },
    { title: t('nodes.csvColIp'), key: 'ip' },
    { title: t('nodes.csvColRoles'), getCsvValue: (row) => row.roles.map(role => roleMap[role.charAt(0)] || role).join('/') },
    { title: t('nodes.csvColCpu'), key: 'load_5m' },
    { title: t('nodes.csvColUptime'), getCsvValue: (row) => formatMillisToDays(row.uptime) },
    { title: t('nodes.csvColDocs'), getCsvValue: (row) => formatNumber(row.docs_count) },
    { title: t('nodes.csvColSegments'), getCsvValue: (row) => formatNumber(row.segments_count) },
    { title: t('nodes.csvColHeapPct'), key: 'heap_percent' },
    { title: t('nodes.csvColHeapUsed'), getCsvValue: (row) => formatBytes(row.heap_used_in_bytes) },
    { title: t('nodes.csvColHeapMax'), getCsvValue: (row) => formatBytes(row.heap_max_in_bytes) },
    { title: t('nodes.csvColDiskPct'), key: 'disk_percent' },
    { title: t('nodes.csvColStoreUsed'), getCsvValue: (row) => formatBytes(row.store_size) },
    { title: t('nodes.csvColDiskTotal'), getCsvValue: (row) => formatBytes(row.disk_total) },
    { title: t('nodes.csvColCacheTotal'), getCsvValue: (row) => formatBytes(row.stats_cache_size) },
    {
      title: t('nodes.csvColCacheDetail'),
      key: 'stats_cache',
      getCsvValue: (row) => (row.stats_cache || '').replace(/\s+/g, ' ').trim()
    },
  ];

  const firstRow = data.value[0];
  const statsToFlatten = {
    [t('perfSearch')]: 'stats_search',
    [t('perfMerge')]: 'stats_merges',
    [t('nodes.colSegments')]: 'stats_segments',
    [t('nodes.sysProcess')]: 'stats_process',
    [t('nodes.sysFs')]: 'stats_fs',
  };

  for (const [prefix, dataKey] of Object.entries(statsToFlatten)) {
    if (firstRow && typeof firstRow[dataKey] === 'object' && firstRow[dataKey] !== null) {
      for (const statKey in firstRow[dataKey]) {
        exportColumns.push({
          title: `${prefix} - ${statKey}`,
          getCsvValue: (row) => row[dataKey]?.[statKey] ?? '',
        });
      }
    }
  }

  try {
    const csvContent = createCsvContent(data.value, exportColumns);
    const fileName = `es-nodes-${cluster_name.value || 'export'}.csv`;
    download_file(csvContent, fileName, 'text/csv;charset=utf-8;');
    message.success(t('nodes.exportSuccess'));
  } catch (e) {
    message.error(t('nodes.exportFailed', { msg: e.message }));
  }
};

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
})

const roleMap = { m: '主', d: '数据', i: 'Ingest', l: 'ML', c: '协调', r: '远程', t: '转换', h: '热', w: '温', f: '冻', v: '投票' };

const columns = computed(() => [
  { title: t('nodes.colName'), key: 'name', width: 120, fixed: 'left' },
  { title: t('nodes.colIp'), key: 'ip', width: 120 },
  {
    title: t('nodes.colRoles'), key: 'roles', width: 120,
    render: (row) => row.roles.map(role => roleMap[role.charAt(0)] || role).join('/')
  },
  { title: t('nodes.colCpu'), key: 'load_5m', width: 100 },
  {
    title: t('nodes.colHeap'), key: 'heap_percent', width: 160,
    render: (row) => h(NFlex, { vertical: true }, () => [
      h(NText, null, () => `${formatBytes(row.heap_used_in_bytes)} / ${formatBytes(row.heap_max_in_bytes)}`),
      h(NProgress, { type: "line", percentage: row.heap_percent, status: getProgressType(row.heap_percent), indicatorPlacement: 'inside', borderRadius: 4, })
    ]),
    sorter: (a, b) => a.heap_percent - b.heap_percent
  },
  {
    title: t('nodes.colDisk'), key: 'disk_percent', width: 160,
    render: (row) => h(NFlex, { vertical: true }, () => [
      h(NText, null, () => `${formatBytes(row.store_size)} / ${formatBytes(row.disk_total)}`),
      h(NProgress, { type: "line", percentage: row.disk_percent, status: getProgressType(row.disk_percent), indicatorPlacement: 'inside', borderRadius: 4, })
    ]),
    sorter: (a, b) => a.disk_percent - b.disk_percent
  },
  {
    title: t('nodes.colPerf'), key: 'perf', width: 160,
    render: (row) => h(NFlex, null, () => [
      h(NTooltip, null, { trigger: () => h(NTag, { type: 'primary' }, { default: () => t('nodes.perfSearch') }), default: () => createTooltipContent(row.stats_search) }),
      h(NTooltip, null, { trigger: () => h(NTag, { type: 'primary' }, { default: () => t('nodes.perfMerge') }), default: () => createTooltipContent(row.stats_merges) }),
      h(NTooltip, null, { trigger: () => h(NTag, { type: 'primary' }, { default: () => t('nodes.perfSeg') }), default: () => createTooltipContent(row.stats_segments) }),
    ])
  },
  {
    title: t('nodes.colSys'), key: 'sys', width: 120,
    render: (row) => h(NFlex, null, () => [
      h(NTooltip, null, { trigger: () => h(NTag, { type: 'info' }, { default: () => t('nodes.sysProcess') }), default: () => createTooltipContent(row.stats_process) }),
      h(NTooltip, null, { trigger: () => h(NTag, { type: 'info' }, { default: () => t('nodes.sysFs') }), default: () => createTooltipContent(row.stats_fs) }),
    ])
  },
  {title: t('nodes.colCache'), key: 'cache', width: 100, render: (row) => row.stats_cache,
    sorter: (a, b) => a.stats_cache_size - b.stats_cache_size
  },
  {title: t('nodes.colDocs'), key: 'docs_count', width: 100, render: (row) => formatNumber(row.docs_count),},
  { title: t('nodes.colSegments'), key: 'segments_count', width: 100, render: (row) => formatNumber(row.segments_count)},
  { title: t('nodes.colUptime'), key: 'uptime', width: 90, render: (row) => formatMillisToDays(row.uptime) },
]);

</script>

<style scoped>

</style>

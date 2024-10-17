<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2 style="width: 42px;">指标</h2>
      <n-button @click="getCore" type="primary">
        刷新
      </n-button>
    </n-flex>
    <n-spin :show="loading" description="Connecting...">
      <n-collapse>
        <n-collapse-item title="节点" name="node">
          <n-table :bordered="false" :single-line="false">
            <thead>
            <tr>
              <th>说明</th>
              <th>值</th>
              <th>key</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in filterByKey(data, 'node')" :key="key">
              <td>
                <n-tooltip placement="top" trigger="hover">
                  <template #trigger>{{ getLabel(key) }}</template>
                  {{key}}
                </n-tooltip>
              </td>
              <td>{{ value }}</td>
              <td>{{ key }}</td>
            </tr>
            </tbody>
          </n-table>
        </n-collapse-item>
        <n-collapse-item title="内存" name="memory">
          <n-table :bordered="false" :single-line="false">
            <thead>
            <tr>
              <th>说明</th>
              <th>值</th>
              <th>key</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in filterByKey(data, 'memory')" :key="key">
              <td>
                <n-tooltip placement="top" trigger="hover">
                  <template #trigger>{{ getLabel(key) }}</template>
                  {{key}}
                </n-tooltip>
              </td>
              <td>{{ value }}</td>
              <td>{{ key }}</td>
            </tr>
            </tbody>
          </n-table>
        </n-collapse-item>
        <n-collapse-item title="索引" name="indices">
          <n-table :bordered="false" :single-line="false">
            <thead>
            <tr>
              <th>说明</th>
              <th>值</th>
              <th>key</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in filterByKey(data, 'indices')" :key="key">
              <td>
                <n-tooltip placement="top" trigger="hover">
                  <template #trigger>{{ getLabel(key) }}</template>
                  {{key}}
                </n-tooltip>
              </td>
              <td>{{ value }}</td>
              <td>{{ key }}</td>
            </tr>
            </tbody>
          </n-table>
        </n-collapse-item>
        <n-collapse-item title="文档" name="doc">
          <n-table :bordered="false" :single-line="false">
            <thead>
            <tr>
              <th>说明</th>
              <th>值</th>
              <th>key</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in filterByKey(data, 'doc')" :key="key">
              <td>
                <n-tooltip placement="top" trigger="hover">
                  <template #trigger>{{ getLabel(key) }}</template>
                  {{key}}
                </n-tooltip>
              </td>
              <td>{{ value }}</td>
              <td>{{ key }}</td>
            </tr>
            </tbody>
          </n-table>
        </n-collapse-item>
        <n-collapse-item title="分片" name="shard">
          <n-table :bordered="false" :single-line="false">
            <thead>
            <tr>
              <th>说明</th>
              <th>值</th>
              <th>key</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in filterByKey(data, 'shard')" :key="key">
              <td>
                <n-tooltip placement="top" trigger="hover">
                  <template #trigger>{{ getLabel(key) }}</template>
                  {{key}}
                </n-tooltip>
              </td>
              <td>{{ value }}</td>
              <td>{{ key }}</td>
            </tr>
            </tbody>
          </n-table>
        </n-collapse-item>
        <n-collapse-item title="存储" name="store">
          <n-table :bordered="false" :single-line="false">
            <thead>
            <tr>
              <th>说明</th>
              <th>值</th>
              <th>key</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(value, key) in filterByKey(data, 'store')" :key="key">
              <td>
                <n-tooltip placement="top" trigger="hover">
                  <template #trigger>{{ getLabel(key) }}</template>
                  {{key}}
                </n-tooltip>
              </td>
              <td>{{ value }}</td>
              <td>{{ key }}</td>
            </tr>
            </tbody>
          </n-table>
        </n-collapse-item>
      </n-collapse>

    </n-spin>
  </n-flex>
</template>


<script setup>
import {onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {useMessage} from "naive-ui";
import {GetStats} from "../../wailsjs/go/service/ESService";
import {flattenObject} from "../utils/common";

const loading = ref(false)
const data = ref({})

const message = useMessage()

onMounted(async () => {
  emitter.on('selectNode', selectNode)
  await getCore()
})

const getCore = async () => {
  loading.value = true
  const res = await GetStats()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    data.value = flattenObject(res.result)
  }
  console.log(data.value)
  loading.value = false

}
// 方法，返回过滤后的数据
const filterByKey = (data, searchString) => {
  const result = {};
  for (const [key, value] of Object.entries(data)) {
    if (key.includes(searchString)) {
      result[key] = value;
    }
  }
  return result;
};
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
    "_nodes.failed": '报告中失败的节点数量',
    "_nodes.successful": '报告中成功的节点数量',
    "_nodes.total": '集群中报告的总节点数',
    "cluster_name": '集群名称',
    "cluster_uuid": '集群的唯一标识符',
    "indices.analysis.analyzer_types": '分析器类型列表',
    "indices.analysis.built_in_analyzers": '内置分析器列表',
    "indices.analysis.built_in_char_filters": '内置字符过滤器列表',
    "indices.analysis.built_in_filters": '内置过滤器列表',
    "indices.analysis.built_in_tokenizers": '内置分词器列表',
    "indices.analysis.char_filter_types": '字符过滤器类型列表',
    "indices.analysis.filter_types": '过滤器类型列表',
    "indices.analysis.tokenizer_types": '分词器类型列表',
    "indices.completion.size_in_bytes": '完成建议字段使用的内存大小（字节）',
    "indices.count": '索引总数',
    "indices.docs.count": '文档总数',
    "indices.docs.deleted": '已删除文档的数量',
    "indices.fielddata.evictions": '字段数据缓存驱逐次数',
    "indices.fielddata.memory_size_in_bytes": '字段数据缓存使用的内存大小（字节）',
    "indices.mappings.field_types": '映射字段类型列表',
    "indices.mappings.runtime_field_types": '运行时字段类型列表',
    "indices.mappings.total_deduplicated_field_count": '去重后的字段计数',
    "indices.mappings.total_deduplicated_mapping_size_in_bytes": '去重后的映射大小（字节）',
    "indices.mappings.total_field_count": '字段计数',
    "indices.query_cache.cache_count": '查询缓存条目数',
    "indices.query_cache.cache_size": '查询缓存大小',
    "indices.query_cache.evictions": '查询缓存驱逐次数',
    "indices.query_cache.hit_count": '查询缓存命中次数',
    "indices.query_cache.memory_size_in_bytes": '查询缓存使用的内存大小（字节）',
    "indices.query_cache.miss_count": '查询缓存未命中次数',
    "indices.query_cache.total_count": '总的查询缓存条目数',
    "indices.segments.count": '段数',
    "indices.segments.doc_values_memory_in_bytes": '文档值使用的内存大小（字节）',
    "indices.segments.fixed_bit_set_memory_in_bytes": '固定位集使用的内存大小（字节）',
    "indices.segments.index_writer_memory_in_bytes": '索引写入器使用的内存大小（字节）',
    "indices.segments.max_unsafe_auto_id_timestamp": '最大不安全的自动 ID 时间戳',
    "indices.segments.memory_in_bytes": '段使用的内存大小（字节）',
    "indices.segments.norms_memory_in_bytes": '规范化因子使用的内存大小（字节）',
    "indices.segments.points_memory_in_bytes": '点使用的内存大小（字节）',
    "indices.segments.stored_fields_memory_in_bytes": '存储字段使用的内存大小（字节）',
    "indices.segments.term_vectors_memory_in_bytes": '词条向量使用的内存大小（字节）',
    "indices.segments.terms_memory_in_bytes": '词条使用的内存大小（字节）',
    "indices.segments.version_map_memory_in_bytes": '版本映射使用的内存大小（字节）',
    "indices.shards.index.primaries.avg": '主分片平均数量',
    "indices.shards.index.primaries.max": '主分片最大数量',
    "indices.shards.index.primaries.min": '主分片最小数量',
    "indices.shards.index.replication.avg": '副本平均数量',
    "indices.shards.index.replication.max": '副本最大数量',
    "indices.shards.index.replication.min": '副本最小数量',
    "indices.shards.index.shards.avg": '分片平均数量',
    "indices.shards.index.shards.max": '分片最大数量',
    "indices.shards.index.shards.min": '分片最小数量',
    "indices.shards.primaries": '主分片总数',
    "indices.shards.replication": '副本总数',
    "indices.shards.total": '分片总数',
    "indices.store.reserved_in_bytes": '保留的空间大小（字节）',
    "indices.store.size_in_bytes": '存储大小（字节）',
    "indices.store.total_data_set_size_in_bytes": '总数据集大小（字节）',
    "indices.versions": '索引版本信息',
    "nodes.count.coordinating_only": '仅协调节点的数量',
    "nodes.count.data": '数据节点的数量',
    "nodes.count.data_cold": '冷数据节点的数量',
    "nodes.count.data_content": '数据内容节点的数量',
    "nodes.count.data_frozen": '冻结数据节点的数量',
    "nodes.count.data_hot": '热数据节点的数量',
    "nodes.count.data_warm": '温数据节点的数量',
    "nodes.count.ingest": '摄取节点的数量',
    "nodes.count.master": '主节点的数量',
    "nodes.count.ml": '机器学习节点的数量',
    "nodes.count.remote_cluster_client": '远程集群客户端节点的数量',
    "nodes.count.transform": '转换节点的数量',
    "nodes.count.voting_only": '仅投票节点的数量',
    "nodes.count.total": '节点总数',
    "nodes.discovery_types.multi_node": '多节点发现类型数量',
    "nodes.fs.available_in_bytes": '可用磁盘空间大小（字节）',
    "nodes.fs.free_in_bytes": '空闲磁盘空间大小（字节）',
    "nodes.fs.total_in_bytes": '总磁盘空间大小（字节）',
    "nodes.indexing_pressure.memory.current.all_in_bytes": '当前所有索引压力内存大小（字节）',
    "nodes.indexing_pressure.memory.current.combined_coordinating_and_primary_in_bytes": '当前组合协调和主要索引压力内存大小（字节）',
    "nodes.indexing_pressure.memory.current.coordinating_in_bytes": '当前协调索引压力内存大小（字节）',
    "nodes.indexing_pressure.memory.current.primary_in_bytes": '当前主要索引压力内存大小（字节）',
    "nodes.indexing_pressure.memory.current.replica_in_bytes": '当前副本索引压力内存大小（字节）',
    "nodes.indexing_pressure.memory.limit_in_bytes": '索引压力内存限制大小（字节）',
    "nodes.indexing_pressure.memory.total.all_in_bytes": '总计所有索引压力内存大小（字节）',
    "nodes.indexing_pressure.memory.total.combined_coordinating_and_primary_in_bytes": '总计组合协调和主要索引压力内存大小（字节）',
    "nodes.indexing_pressure.memory.total.coordinating_in_bytes": '总计协调索引压力内存大小（字节）',
    "nodes.indexing_pressure.memory.total.coordinating_rejections": '总计协调索引拒绝次数',
    "nodes.indexing_pressure.memory.total.primary_in_bytes": '总计主要索引压力内存大小（字节）',
    "nodes.indexing_pressure.memory.total.primary_rejections": '总计主要索引拒绝次数',
    "nodes.indexing_pressure.memory.total.replica_in_bytes": '总计副本索引压力内存大小（字节）',
    "nodes.indexing_pressure.memory.total.replica_rejections": '总计副本索引拒绝次数',
    "nodes.ingest.number_of_pipelines": '摄取管道数量',
    "nodes.jvm.max_uptime_in_millis": 'JVM 上线时间（毫秒）',
    "nodes.jvm.mem.heap_max_in_bytes": '堆内存最大大小（字节）',
    "nodes.jvm.mem.heap_used_in_bytes": '堆内存使用大小（字节）',
    "nodes.jvm.threads": 'JVM 线程数',
    "nodes.jvm.versions": 'JVM 版本信息',
    "nodes.network_types.http_types.netty4": 'HTTP 类型为 Netty 4 的节点数量',
    "nodes.network_types.transport_types.netty4": '传输类型为 Netty 4 的节点数量',
    "nodes.os.allocated_processors": '分配的处理器数量',
    "nodes.os.architectures": '操作系统架构信息',
    "nodes.os.available_processors": '可用处理器数量',
    "nodes.os.mem.adjusted_total_in_bytes": '调整后的总内存大小（字节）',
    "nodes.os.mem.free_in_bytes": '空闲内存大小（字节）',
    "nodes.os.mem.free_percent": '空闲内存百分比',
    "nodes.os.mem.total_in_bytes": '总内存大小（字节）',
    "nodes.os.mem.used_in_bytes": '使用内存大小（字节）',
    "nodes.os.mem.used_percent": '使用内存百分比',
    "nodes.os.names": '操作系统名称',
    "nodes.os.pretty_names": '操作系统友好名称',
    "nodes.packaging_types": '打包类型信息',
    "nodes.plugins": '插件信息',
    "nodes.process.cpu.percent": 'CPU 使用率',
    "nodes.process.open_file_descriptors.avg": '平均打开的文件描述符数量',
    "nodes.process.open_file_descriptors.max": '最大打开的文件描述符数量',
    "nodes.process.open_file_descriptors.min": '最小打开的文件描述符数量',
    "nodes.versions": '节点版本信息',
    "status": '集群健康状态（绿色、黄色、红色）',
    "timestamp": '报告的时间戳'
  };
  return descriptions[key] || '暂无说明'
}

const selectNode = (node) => {
}
</script>

<style scoped>

</style>
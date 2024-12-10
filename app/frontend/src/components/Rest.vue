<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2 style="max-width: 200px;">REST</h2>
      <n-text>一个 Restful 调试工具</n-text>
    </n-flex>
    <n-flex align="center">
      <n-select v-model:value="method" :options="methodOptions" style="width: 120px;"/>
      <n-input v-model:value="path" placeholder="输入url path，以/开头" autosize
               style="min-width: 300px;text-align: left"/>
      <n-button @click="sendRequest" :loading="send_loading" :render-icon="renderIcon(SendSharp)">Send</n-button>
      <n-button @click="exportJson" :render-icon="renderIcon(ArrowDownwardOutlined)">导出结果</n-button>
      <n-button @click="showDrawer = true" :render-icon="renderIcon(MenuBookTwotone)">ES查询示例</n-button>
      <n-button @click="showHistoryDrawer = true" :render-icon="renderIcon(HistoryOutlined)">历史记录</n-button>
    </n-flex>
    <n-grid x-gap="20" :cols="2">
      <n-grid-item>
        <div id="json_editor" class="editarea" @paste="toTree"></div>
      </n-grid-item>
      <n-grid-item>
        <div id="json_view" class="editarea"></div>
      </n-grid-item>
    </n-grid>
  </n-flex>
  <!--  示例-->
  <n-drawer v-model:show="showDrawer" style="width: 38.2%" placement="right">
    <n-drawer-content title="ES DSL查询示例" style="text-align: left;">
      <n-flex vertical>
        <n-collapse>
          <n-collapse-item title="1. Term查询" name="1">
            <n-code :code="dslExamples.term" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="2. Terms查询" name="2">
            <n-code :code="dslExamples.terms" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="3. Match查询" name="3">
            <n-code :code="dslExamples.match" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="4. Match Phrase查询" name="4">
            <n-code :code="dslExamples.matchPhrase" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="5. Range查询" name="5">
            <n-code :code="dslExamples.range" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="6. Bool复合查询" name="6">
            <n-code :code="dslExamples.bool" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="7. Terms Aggregation" name="7">
            <n-code :code="dslExamples.termsAggs" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="8. Date Histogram聚合" name="8">
            <n-code :code="dslExamples.dateHistogram" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="9. Nested查询" name="9">
            <n-code :code="dslExamples.nested" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="10. Exists查询" name="10">
            <n-code :code="dslExamples.exists" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="11. Multi-match查询" name="11">
            <n-code :code="dslExamples.multiMatch" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="12. Wildcard查询" name="12">
            <n-code :code="dslExamples.wildcard" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="13. Metrics聚合" name="13">
            <n-code :code="dslExamples.metrics" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="14. Cardinality聚合" name="14">
            <n-code :code="dslExamples.cardinality" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="15. Script查询" name="15">
            <n-code :code="dslExamples.script" language="json"/>
          </n-collapse-item>
        </n-collapse>
      </n-flex>
    </n-drawer-content>
  </n-drawer>

  <!-- 历史记录抽屉 -->
  <n-drawer v-model:show="showHistoryDrawer" style="width: 38.2%">
    <n-drawer-content title="查询历史记录">
      <!-- 搜索框 -->
      <n-input
          v-model:value="searchText"
          placeholder="搜索历史记录，同时支持method、path、dsl"
          clearable
          style="margin-bottom: 12px"
      >
        <template #prefix>
          <n-icon><SearchFilled /></n-icon>
        </template>
      </n-input>

      <!-- 历史记录列表 -->
      <n-list>
        <n-pagination
            v-model:page="currentPage"
            :page-size="pageSize"
            :item-count="filteredHistory.length"
        />

          <n-list-item v-for="item in currentPageData" :key="item.timestamp" >
              <n-tooltip placement="left" trigger="hover" style="max-height: 618px;overflow-y: auto">
                <template #trigger>
                  <div style="display: flex;font-size: 14px; justify-content: space-between;">
                    <n-tag :type="getMethodTagType(item.method)">
                      {{ item.method }}
                    </n-tag>
                    <n-text>{{ item.path }}</n-text>
                    <n-text depth="3">
                      {{ formatTimestamp(item.timestamp) }}
                    </n-text>
                  </div>
                </template>
                 <n-code :code="formatDSL(item.dsl)" language="json" style="text-align: left;" v-if="item.dsl !== ''"/>

              </n-tooltip>
          </n-list-item>

      </n-list>
    </n-drawer-content>
  </n-drawer>
</template>

<script setup>

import {NButton, NGrid, NGridItem, NInput, NSelect, useMessage} from 'naive-ui'
import {computed, onMounted, ref} from "vue";
import JSONEditor from 'jsoneditor';
import '../assets/css/jsoneditor.min.css'
import {Search} from "../../wailsjs/go/service/ESService";
import {ArrowDownwardOutlined, HistoryOutlined, MenuBookTwotone, SearchFilled, SendSharp} from "@vicons/material";
import {formatTimestamp, renderIcon} from "../utils/common";
import 'ace-builds/src-noconflict/theme-tomorrow_night';
import 'ace-builds/src-noconflict/theme-monokai';
import 'jsoneditor/src/js/ace/theme-jsoneditor';
import {GetConfig, GetHistory, SaveHistory} from "../../wailsjs/go/config/AppConfig";
import emitter from "../utils/eventBus";

const message = useMessage()
const method = ref('GET')
const path = ref('')
const searchText = ref('')
const history = ref([])
const editor = ref();
const response = ref()
const send_loading = ref(false)
const showDrawer = ref(false)
const showHistoryDrawer = ref(false)
// 状态管理
const currentPage = ref(1)
const pageSize = ref(10)

const methodOptions = [
  {label: 'GET', value: 'GET'},
  {label: 'POST', value: 'POST'},
  {label: 'PUT', value: 'PUT'},
  {label: 'HEAD', value: 'HEAD'},
  {label: 'PATCH', value: 'PATCH'},
  {label: 'OPTIONS', value: 'OPTIONS'},
  {label: 'DELETE', value: 'DELETE'}
]

const selectNode = (node) => {
  response.value.setText('{"tip": "响应结果，支持搜索"}')
  send_loading.value = false
}

onMounted(async () => {

  emitter.on('selectNode', selectNode)
  emitter.on('update_theme', themeChange)

  const loadedConfig = await GetConfig()
  let theme = 'ace/theme/jsoneditor'
  if (loadedConfig) {
    if (loadedConfig.theme !== 'light') {
      theme = 'ace/theme/monokai'
    }
    editor.value = new JSONEditor(document.getElementById('json_editor'), {
      mode: 'code',
      theme: theme,
      mainMenuBar: false,
      statusBar: false,
    });
    response.value = new JSONEditor(document.getElementById('json_view'), {
      mode: 'code',
      theme: theme,
      mainMenuBar: false,
      statusBar: false,
    });
    editor.value.setText(null)
    response.value.setText('{"tip": "响应结果，支持搜索"}')
  }
  await read_history()


});

const read_history = async () => {
  console.log("read_history")
  try {
    history.value = await GetHistory()
  } catch (e) {
    message.error(e)
  }
}
const write_history = async () =>  {
  console.log("write_history")
  try {
    // 从左侧插入history
    history.value.unshift({
      timestamp: Date.now(),
      method: method.value,
      path: path.value,
      dsl: editor.value.getText()
    })
    // 只保留100条
    if (history.value.length > 100) {
      history.value = history.value.slice(0, 100)
    }
    console.log(history.value)
    const res = await SaveHistory(history.value)
    if (res !== "") {
      message.error("保存查询失败：" + res)
    }
  } catch (e) {
    message.error(e)
  }
}

function themeChange(newTheme) {
  const new_editor_theme = newTheme.name === 'dark' ? 'ace/theme/monokai' : 'ace/theme/jsoneditor'
  editor.value.aceEditor.setTheme(new_editor_theme)
  response.value.aceEditor.setTheme(new_editor_theme)

}


const formatDSL = (dsl) => {
  try {
    return JSON.stringify(JSON.parse(dsl), null, 2)
  } catch {
    return dsl
  }
}

const sendRequest = async () => {
  send_loading.value = true
  // 清空response
  response.value.set({})
  if (!path.value.startsWith('/')) {
    path.value = '/' + path.value;
  }
  try {
    const res = await Search(method.value, path.value, editor.value.getText())
    // 返回不是200也写入结果框
    if (res.err !== "") {
      response.value.set(res.err)
    } else {
      response.value.set(res.result)
      // 写入历史记录
      write_history()
    }
  } catch (e) {
    message.error(e)
  }
  send_loading.value = false

}
const toTree = () => {
  editor.value.format();
}


function exportJson() {
  const blob = new Blob([response.value.getText()], {type: 'application/json'})
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'response.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// 过滤和分页逻辑
const filteredHistory = computed(() => {
  if (!searchText.value){
    return history.value
  }else {
    return history.value.filter(item => {
      return item.method.includes(searchText.value) ||
          item.path.includes(searchText.value) ||
          item.dsl.includes(searchText.value)
    })
  }

})

const currentPageData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredHistory.value.slice(start, end)
})
const getMethodTagType = (method) => {
  const types = {
    'GET': 'success',
    'POST': 'info',
    'PUT': 'warning',
    'DELETE': 'error'
  }
  return types[method] || 'default'
}
const dslExamples = {
  term: JSON.stringify({
    "query": {
      "term": {
        "status": "active"
      }
    },
    "size": 10,
    "track_total_hits": true
  }, null, 2),

  terms: JSON.stringify({
    "query": {
      "terms": {
        "user_id": [1, 2, 3, 4]
      }
    },
    "size": 10
  }, null, 2),

  match: JSON.stringify({
    "query": {
      "match": {
        "description": "quick brown fox"
      }
    },
    "size": 20
  }, null, 2),

  matchPhrase: JSON.stringify({
    "query": {
      "match_phrase": {
        "description": {
          "query": "quick brown fox",
          "slop": 1
        }
      }
    }
  }, null, 2),

  range: JSON.stringify({
    "query": {
      "range": {
        "age": {
          "gte": 20,
          "lte": 30
        }
      }
    }
  }, null, 2),

  bool: JSON.stringify({
    "query": {
      "bool": {
        "must": [
          {"term": {"status": "active"}}
        ],
        "must_not": [
          {"term": {"type": "deleted"}}
        ],
        "should": [
          {"term": {"category": "electronics"}},
          {"term": {"category": "computers"}}
        ],
        "minimum_should_match": 1
      }
    }
  }, null, 2),

  termsAggs: JSON.stringify({
    "aggs": {
      "status_counts": {
        "terms": {
          "field": "status",
          "missing": "N/A",
          "size": 10
        }
      }
    },
    "size": 0
  }, null, 2),

  dateHistogram: JSON.stringify({
    "aggs": {
      "sales_over_time": {
        "date_histogram": {
          "field": "created_at",
          "calendar_interval": "1d",
          "format": "yyyy-MM-dd"
        }
      }
    },
    "size": 0
  }, null, 2),

  nested: JSON.stringify({
    "query": {
      "nested": {
        "path": "comments",
        "query": {
          "bool": {
            "must": [
              {"match": {"comments.text": "great"}},
              {"term": {"comments.rating": 5}}
            ]
          }
        }
      }
    }
  }, null, 2),

  exists: JSON.stringify({
    "query": {
      "exists": {
        "field": "email"
      }
    }
  }, null, 2),

  multiMatch: JSON.stringify({
    "query": {
      "multi_match": {
        "query": "quick brown fox",
        "fields": ["title", "description^2"],
        "type": "best_fields"
      }
    }
  }, null, 2),

  wildcard: JSON.stringify({
    "query": {
      "wildcard": {
        "email": "*@gmail.com"
      }
    }
  }, null, 2),

  metrics: JSON.stringify({
    "aggs": {
      "avg_price": {"avg": {"field": "price"}},
      "max_price": {"max": {"field": "price"}},
      "min_price": {"min": {"field": "price"}},
      "sum_quantity": {"sum": {"field": "quantity"}}
    },
    "size": 0
  }, null, 2),

  cardinality: JSON.stringify({
    "aggs": {
      "unique_users": {
        "cardinality": {
          "field": "user_id",
          "precision_threshold": 100
        }
      }
    },
    "size": 0
  }, null, 2),

  script: JSON.stringify({
    "query": {
      "script_score": {
        "query": {"match_all": {}},
        "script": {
          "source": "doc['price'].value * doc['rating'].value",
          "lang": "painless"
        }
      }
    }
  }, null, 2)
}

</script>

<style scoped>
.editarea, .json_view {
  height: 72dvh;
}

</style>
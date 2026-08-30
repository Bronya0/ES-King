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
      <h2>{{ t('analyze.title') }}</h2>
      <n-text>{{ t('analyze.desc') }}</n-text>
    </n-flex>

    <n-card size="small">
      <n-form label-placement="left" label-width="auto" style="max-width: 860px;">
        <n-form-item :label="t('analyze.index')">
          <n-flex align="center" style="width: 100%;">
            <n-select
                v-model:value="indexName"
                :options="indexOptions"
                filterable
                clearable
                :placeholder="t('analyze.indexOptional')"
                style="min-width: 240px"
            />
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="loadIndexes"></n-button>
          </n-flex>
        </n-form-item>
        <n-form-item :label="t('analyze.analyzer')">
          <n-select
              v-model:value="analyzer"
              :options="analyzerOptions"
              filterable
              tag
              clearable
              :placeholder="t('analyze.analyzerPlaceholder')"
              :disabled="field !== ''"
              style="min-width: 240px"
          />
        </n-form-item>
        <n-form-item :label="t('analyze.field')">
          <n-input v-model:value="field" :placeholder="t('analyze.fieldPlaceholder')" style="width: 240px"/>
        </n-form-item>
        <n-form-item :label="t('analyze.text')">
          <n-input
              v-model:value="text"
              type="textarea"
              :autosize="{minRows: 3, maxRows: 8}"
              :placeholder="t('analyze.textPlaceholder')"
              @keydown.enter="doAnalyze"
          />
        </n-form-item>
      </n-form>
      <n-flex>
        <n-button type="primary" :loading="loading" :render-icon="renderIcon(SearchFilled)" @click="doAnalyze">
          {{ t('analyze.run') }}
        </n-button>
      </n-flex>
    </n-card>

    <n-spin :show="loading" :description="t('app.loading')">
      <n-data-table
          :bordered="false"
          :columns="tokenColumns"
          :data="tokens"
          :max-height="400"
          size="small"
          striped
      />
    </n-spin>
  </n-flex>
</template>

<script setup>
import {useI18n} from 'vue-i18n'
import {computed, h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NTag, useMessage} from 'naive-ui'
import {refColumns, renderIcon} from "../utils/common";
import {RefreshOutlined, SearchFilled} from "@vicons/material";
import {AnalyzeText, GetIndexes} from "../../wailsjs/go/service/ESService";

const {t} = useI18n()
const message = useMessage()

const indexName = ref(null)
const indexOptions = ref([])
const analyzer = ref('standard')
const field = ref("")
const text = ref("")
const tokens = ref([])
const loading = ref(false)

const analyzerOptions = [
  'standard', 'simple', 'whitespace', 'stop', 'keyword', 'pattern', 'english', 'french',
  'german', 'cjk', 'ik_max_word', 'ik_smart', 'pinyin',
].map(v => ({label: v, value: v}))

const loadIndexes = async () => {
  const res = await GetIndexes("")
  if (res.err !== "") {
    return
  }
  indexOptions.value = (res.results || []).map(item => ({label: item.index, value: item.index}))
}

const tokenColumns = computed(() => refColumns([
  {
    title: t('analyze.colToken'), key: 'token',
    render: (row) => h(NTag, {size: 'small', type: 'info'}, {default: () => row.token}),
  },
  {title: t('analyze.colType'), key: 'type'},
  {title: 'position', key: 'position', width: 100},
  {title: 'start_offset', key: 'start_offset', width: 130},
  {title: 'end_offset', key: 'end_offset', width: 130},
]))

const doAnalyze = async () => {
  if (!text.value.trim()) {
    message.warning(t('analyze.inputTextFirst'))
    return
  }
  if (!analyzer.value && !field.value) {
    message.warning(t('analyze.needAnalyzerOrField'))
    return
  }
  loading.value = true
  tokens.value = []
  try {
    const res = await AnalyzeText(indexName.value || '', text.value, analyzer.value || '', field.value)
    if (res.err !== "") {
      message.error(res.err)
      return
    }
    tokens.value = (res.result && res.result.tokens) || []
    if (tokens.value.length === 0) {
      message.info(t('analyze.noTokens'))
    }
  } catch (e) {
    message.error(e.message)
  } finally {
    loading.value = false
  }
}

const selectNode = () => {
  indexOptions.value = []
  tokens.value = []
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  loadIndexes()
})
</script>

<style scoped>
</style>

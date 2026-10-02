/*
 * Copyright 2025 Bronya0 <tangssst@163.com>.
 * Author Github: https://github.com/Bronya0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * 校验三份语言文案能否被 vue-i18n 的 ICU 编译器解析。
 *
 * 为什么要单独检查：文案里出现"裸花括号"（例如 JSON 示例 {"term":{"status":"active"}}）时会被
 * 当成 ICU 占位符解析。开发构建只会打印 "Message compilation error" 日志、并照常返回原文，
 * 所以 wails dev 里一切正常；但生产构建下 t() 会直接抛 SyntaxError。由于这类文案常出现在模板
 * 表达式里（:placeholder="t('xxx')"），一抛错整块 DOM 都会被 Vue 丢弃，表现为：
 *   - 某个工具栏/输入框整行消失（如文档浏览的索引选择 + 查询框）
 *   - 某段初始化逻辑被中断（如 REST 页 onMounted 里 t() 抛错导致后面的读历史不执行）
 * 正确写法：把字面量整段包起来，例如
 *   "queryPlaceholder": "如 {'{\"term\":{\"status\":\"active\"}}'}，留空查询全部"
 *
 * 用法：npm run check:i18n（已挂在 npm run build 前面，构建失败即拦截）
 */
const fs = require('fs')
const path = require('path')

function loadCompiler() {
  const candidates = [
    '@intlify/message-compiler',
    'vue-i18n/node_modules/@intlify/message-compiler',
  ]
  for (const c of candidates) {
    try {
      return require(c)
    } catch (e) {
      // 继续尝试下一个
    }
  }
  console.warn('警告：未找到 @intlify/message-compiler，跳过文案校验')
  return null
}

const compiler = loadCompiler()
if (!compiler) {
  process.exit(0)
}

const localesDir = path.join(__dirname, '..', 'src', 'locales')
const files = fs.readdirSync(localesDir).filter(f => f.endsWith('.json'))

let total = 0
const failures = []

function walk(node, prefix, locale, file) {
  for (const [k, v] of Object.entries(node)) {
    const key = prefix ? `${prefix}.${k}` : k
    if (v && typeof v === 'object') {
      walk(v, key, locale, file)
      continue
    }
    if (typeof v !== 'string') continue
    total++
    let err = null
    try {
      compiler.baseCompile(v, {
        onError: (e) => {
          err = e
        },
      })
    } catch (e) {
      err = e
    }
    if (err) {
      failures.push({file, locale, key, msg: v, reason: String(err.message).split('\n')[0]})
    }
  }
}

for (const f of files) {
  const locale = path.basename(f, '.json')
  walk(JSON.parse(fs.readFileSync(path.join(localesDir, f), 'utf8')), '', locale, f)
}

if (failures.length === 0) {
  console.log(`i18n 文案校验通过：${files.length} 个语言包 / ${total} 条文案`)
  process.exit(0)
}

console.error(`i18n 文案校验失败：${failures.length} 条文案无法被 ICU 编译器解析`)
for (const f of failures) {
  console.error(`\n  [${f.file}] ${f.key}\n    ${f.reason}\n    文案: ${JSON.stringify(f.msg)}`)
}
console.error(`\n修复方式：把文案里的字面花括号用 {' '} 包起来，例如`)
console.error(`  "{\\"tip\\": \\"ok\\"}"  ->  "{'{\\"tip\\": \\"ok\\"}'}"`)
process.exit(1)

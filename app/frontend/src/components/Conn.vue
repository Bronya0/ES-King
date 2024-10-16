<template>
  <div>
    <n-flex vertical>
      <n-flex  align="center" >
        <h2 style="width: 42px;">集群</h2>
        <n-text>共有 {{ esNodes.length }} 个</n-text>
        <n-button @click="addNewNode" :render-icon="renderIcon(AddFilled)">添加集群</n-button>
      </n-flex>
      <n-grid :x-gap="12" :y-gap="12" :cols="4">
        <n-gi v-for="node in esNodes" :key="node.id">
          <n-card :title="node.name" @click="selectNode(node)" hoverable>
            <template #header-extra>
              <n-space>
                <n-button @click.stop="editNode(node)" size="small">
                  编辑
                </n-button>
                <n-popconfirm @positive-click="deleteNode(node.id)">
                  <template #trigger>
                    <n-button @click.stop size="small">
                      删除
                    </n-button>
                  </template>
                  确定删除该节点吗？
                </n-popconfirm>
              </n-space>
            </template>
            <n-descriptions :column="1" label-placement="left">
              <n-descriptions-item label="主机">
                {{ node.host }}
              </n-descriptions-item>
              <n-descriptions-item label="端口">
                {{ node.port }}
              </n-descriptions-item>
            </n-descriptions>
          </n-card>
        </n-gi>
      </n-grid>
    </n-flex>

    <n-drawer v-model:show="showEditDrawer" :width="500" placement="right">
      <n-drawer-content :title="drawerTitle">
        <n-form
            ref="formRef"
            :model="currentNode"
            :rules="rules"
            label-placement="left"
        >
          <n-form-item label="节点名称" path="name">
            <n-input v-model:value="currentNode.name" placeholder="输入节点名称" />
          </n-form-item>
          <n-form-item label="主机" path="host">
            <n-input v-model:value="currentNode.host" placeholder="输入主机地址" />
          </n-form-item>
          <n-form-item label="端口" path="port">
            <n-input-number v-model:value="currentNode.port" placeholder="输入端口号" />
          </n-form-item>
          <n-form-item label="用户名" path="username">
            <n-input v-model:value="currentNode.username" placeholder="输入用户名" />
          </n-form-item>
          <n-form-item label="密码" path="password">
            <n-input
                v-model:value="currentNode.password"
                type="password"
                placeholder="输入密码"
            />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showEditDrawer = false">取消</n-button>
            <n-button type="primary" @click="saveNode">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import {renderIcon} from "../utils/common";
import {AddFilled} from "@vicons/material";
import emitter from "../utils/eventBus";

const message = useMessage()

const esNodes = ref([
  { id: 1, name: 'ES节点1', host: 'localhost', port: 9200, username: 'user1', password: 'pass1' },
  { id: 2, name: 'ES节点2', host: '192.168.1.100', port: 9200, username: 'user2', password: 'pass2' },
  { id: 2, name: 'ES节点2', host: '192.168.1.100', port: 9200, username: 'user2', password: 'pass2' },
  { id: 2, name: 'ES节点2', host: '192.168.1.100', port: 9200, username: 'user2', password: 'pass2' },
  { id: 2, name: 'ES节点2', host: '192.168.1.100', port: 9200, username: 'user2', password: 'pass2' },
  { id: 2, name: 'ES节点2', host: '192.168.1.100', port: 9200, username: 'user2', password: 'pass2' },
  { id: 2, name: 'ES节点2', host: '192.168.1.100', port: 9200, username: 'user2', password: 'pass2' },

])

const showEditDrawer = ref(false)
const showAddDrawer = ref(false)
const currentNode = ref({})
const isEditing = ref(false)

const drawerTitle = computed(() => isEditing.value ? '编辑 ES 连接' : '添加 ES 连接')

const rules = {
  name: { required: true, message: '请输入节点名称', trigger: 'blur' },
  host: { required: true, message: '请输入主机地址', trigger: 'blur' },
  port: { required: true, type: 'number', message: '请输入有效的端口号', trigger: 'blur' },
}

const formRef = ref(null)

function editNode(node) {
  currentNode.value = { ...node }
  isEditing.value = true
  showEditDrawer.value = true
}

function addNewNode() {
  currentNode.value = { name: '', host: '', port: 9200, username: '', password: '' }
  isEditing.value = false
  showEditDrawer.value = true
}

function saveNode() {
  formRef.value?.validate((errors) => {
    if (!errors) {
      if (isEditing.value) {
        const index = esNodes.value.findIndex(node => node.id === currentNode.value.id)
        if (index !== -1) {
          esNodes.value[index] = { ...currentNode.value }
        }
      } else {
        const newId = Math.max(...esNodes.value.map(node => node.id), 0) + 1
        esNodes.value.push({ ...currentNode.value, id: newId })
      }
      showEditDrawer.value = false
      message.success('保存成功')
    } else {
      message.error('请填写所有必填字段')
    }
  })
}

function deleteNode(id) {
  esNodes.value = esNodes.value.filter(node => node.id !== id)
  message.success('删除成功')
}

function selectNode(node) {
  // 这里实现切换菜单的逻辑
  console.log('选中节点:', node)
  message.info(`选中了节点: ${node.name}`)
  emitter.emit('menu_select', "健康" )


  // node：{ id: 1, name: 'ES节点1', host: 'localhost', port: 9200, username: 'user1', password: 'pass1' },
  emitter.emit('selectNode', node)
}
</script>
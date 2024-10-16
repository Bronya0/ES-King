

<template>
  <n-flex vertical>
    <h2 style="width: 42px;">健康</h2>
  </n-flex>
</template>
<script setup>
import {onMounted, onActivated, ref} from "vue";
import emitter from "../utils/eventBus";
import {useLoadingBar, useMessage} from "naive-ui";
import esService from "../utils/http_service";
const message = useMessage()
const loadingBar = useLoadingBar()

const health_data = []

onMounted(async () => {
  emitter.on('selectNode', selectNode)
})

onActivated(async () => {
  message.success("onActivated")
})

const getHealth = async() => {
  loadingBar.start()
  health_data.value = await esService.getHealth()
  loadingBar.finish()

}
const selectNode = async (node) => {
  await getHealth()
}
</script>
<style scoped>

</style>
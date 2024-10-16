<script setup>
import {onMounted} from "vue";
import emitter from "../utils/eventBus";

onMounted(async () => {
  emitter.on('selectNode', selectNode)
})

const selectNode = (node) => {}
</script>

<template>
  <n-flex vertical>
    <h2 style="width: 42px;">指标</h2>
  </n-flex>
</template>

<style scoped>

</style>
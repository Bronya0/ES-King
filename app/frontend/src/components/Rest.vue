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
    <h2 style="width: 42px;">Rest</h2>
  </n-flex>
</template>

<style scoped>

</style>
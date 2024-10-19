<script setup>
import {onMounted} from "vue";
import emitter from "../utils/eventBus";
import {BrowserOpenURL} from "../../wailsjs/runtime";
import {renderIcon} from "../utils/common";
import {HouseTwotone} from "@vicons/material";

onMounted(async () => {
  emitter.on('selectNode', selectNode)
})

const selectNode = (node) => {}
</script>

<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2 style="width: 42px;">快照</h2>
    </n-flex>
    <n-flex align="center">
      <n-p>开发中……敬请期待</n-p>
    </n-flex>
  </n-flex>
</template>

<style scoped>

</style>
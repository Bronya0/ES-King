<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2 style="width: 42px;">建议</h2>
    </n-flex>
    <n-flex align="center">
      <n-button @click="BrowserOpenURL(home_url)" :render-icon="renderIcon(HouseTwotone)">项目主页</n-button>
    </n-flex>
  </n-flex>
</template>

<script setup>
import {onMounted} from "vue";
import emitter from "../utils/eventBus";
import {renderIcon} from "../utils/common";
import {HouseTwotone} from "@vicons/material";
import {BrowserOpenURL} from "../../wailsjs/runtime";

const home_url = "https://github.com/Bronya0/ES-King"


onMounted(async () => {
})

</script>


<style scoped>

</style>
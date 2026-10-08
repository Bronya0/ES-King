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
  <!--  https://www.naiveui.com/zh-CN/os-theme/components/menu-->
  <n-menu
      :mode="'vertical'"
      :value="props.value"
      :theme-overrides="{ itemHeight: (props.itemSize || 32) + 'px' }"
      @update:value="handleMenuSelect"
      :options="props.options"
      style="--wails-draggable:no-drag"
  />

</template>


<script setup>

import emitter from "../utils/eventBus";

const props = defineProps(['options', 'value', 'itemSize']);

const handleMenuSelect = (key, item) => {
  emitter.emit('menu_select', key)
}

</script>

<style>
/* 收起态菜单：naive 默认行距 6px，缩到 32px 方块后图标显得挤，这里放到 12px；
   首项保持 6px，免得顶栏下面空档过大 */
.n-menu--collapsed .n-menu-item {
  margin-top: 12px;
}

.n-menu--collapsed .n-menu-item:first-child {
  margin-top: 6px;
}
</style>
<template>
<!--  https://www.naiveui.com/zh-CN/os-theme/components/menu-->
    <n-menu
        :mode="'vertical'"
        :value="props.value"
        @update:value="handleMenuSelect"
        :options="props.options"
        style="--wails-draggable:no-drag"
    />

</template>


<script setup>

const props = defineProps(['options', 'value']);
const emit = defineEmits(['update:value'])

const handleMenuSelect = (key, item) => {
  emit('update:value', key, item)
}

</script>

<style>
.aside-btn .n-button .n-button__icon {
  font-size: 22px;
}
</style>
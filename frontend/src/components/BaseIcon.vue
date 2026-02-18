<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  }
})

// Load all SVGs as raw strings eagerly
const modules = import.meta.glob('../assets/icons/*.svg', { 
  query: '?raw', 
  import: 'default', 
  eager: true 
})

const iconContent = computed(() => {
  const path = `../assets/icons/${props.name}.svg`
  return modules[path] || modules['../assets/icons/empty.svg']
})
</script>

<template>
  <div v-html="iconContent" class="base-icon w-5 h-5 [&>svg]:w-full [&>svg]:h-full [&>svg]:fill-current"></div>
</template>

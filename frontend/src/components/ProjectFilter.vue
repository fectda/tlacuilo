<script setup>
import { ref, watch } from 'vue'
import { UI_STRINGS } from '../constants/uiStrings'
import BaseIcon from './BaseIcon.vue'

const props = defineProps({
  initialFilters: {
    type: Object,
    default: () => ({
      collections: [],
      statuses: []
    })
  }
})

const emit = defineEmits(['change'])

const collections = [
  { id: 'atoms', label: UI_STRINGS.filters.collections.atoms },
  { id: 'bits', label: UI_STRINGS.filters.collections.bits },
  { id: 'mind', label: UI_STRINGS.filters.collections.mind }
]

const statuses = [
  { id: 'borrador', label: UI_STRINGS.filters.status.borrador },
  { id: 'revisión', label: UI_STRINGS.filters.status.revision },
  { id: 'traducción', label: UI_STRINGS.filters.status.traduccion },
  { id: 'publicado', label: UI_STRINGS.filters.status.publicado }
]

const activeCollections = ref([...props.initialFilters.collections])
const activeStatuses = ref([...props.initialFilters.statuses])

const toggleCollection = (id) => {
  const index = activeCollections.value.indexOf(id)
  if (index > -1) {
    activeCollections.value.splice(index, 1)
  } else {
    activeCollections.value.push(id)
  }
}

const toggleStatus = (id) => {
  const index = activeStatuses.value.indexOf(id)
  if (index > -1) {
    activeStatuses.value.splice(index, 1)
  } else {
    activeStatuses.value.push(id)
  }
}

const clearFilters = () => {
  activeCollections.value = []
  activeStatuses.value = []
}

watch([activeCollections, activeStatuses], () => {
  emit('change', {
    collections: [...activeCollections.value],
    statuses: [...activeStatuses.value]
  })
}, { 
  deep: true 
})
</script>

<template>
  <div class="flex flex-col gap-6 py-6 border-y border-white/5 animate-in fade-in slide-in-from-top-4 duration-500">
    <!-- Collections Filter -->
    <div class="flex flex-wrap items-center gap-4">
      <span class="font-mono text-[9px] uppercase tracking-[0.2em] text-neutral-500 font-bold mr-2">{{ UI_STRINGS.filters.collections.title }}</span>
      <div class="flex flex-wrap gap-2">
        <button 
          v-for="col in collections" 
          :key="col.id"
          @click="toggleCollection(col.id)"
          :class="[
            'px-3 py-1 text-[10px] uppercase font-bold tracking-widest transition-all duration-300 border',
            activeCollections.includes(col.id) 
              ? 'bg-accent/10 border-accent/50 text-accent shadow-status-wait' 
              : 'bg-white/5 border-white/10 text-neutral-500 hover:border-white/20'
          ]"
        >
          {{ col.label }}
        </button>
      </div>
    </div>

    <!-- Status Filter -->
    <div class="flex flex-wrap items-center gap-4">
      <span class="font-mono text-[9px] uppercase tracking-[0.2em] text-neutral-500 font-bold mr-2">{{ UI_STRINGS.filters.status.title }}</span>
      <div class="flex flex-wrap gap-2">
        <button 
          v-for="status in statuses" 
          :key="status.id"
          @click="toggleStatus(status.id)"
          :class="[
            'px-3 py-1 text-[10px] uppercase font-bold tracking-widest transition-all duration-300 border',
            activeStatuses.includes(status.id) 
              ? 'bg-accent/10 border-accent/50 text-accent shadow-status-wait' 
              : 'bg-white/5 border-white/10 text-neutral-500 hover:border-white/20'
          ]"
        >
          {{ status.label }}
        </button>
      </div>

      <!-- Clear Button -->
      <button 
        v-if="activeCollections.length > 0 || activeStatuses.length > 0"
        @click="clearFilters"
        class="ml-auto font-mono text-[9px] uppercase tracking-widest text-accent-light hover:text-accent transition-colors underline underline-offset-4 decoration-accent/30"
      >
        {{ UI_STRINGS.filters.reset }}
      </button>
    </div>
  </div>
</template>

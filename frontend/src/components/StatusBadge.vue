<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'dot' // 'dot' or 'badge'
  }
})

const statusConfig = computed(() => {
  const s = String(props.status).toUpperCase().trim()
  switch (s) {
    case 'ONLINE':
    case 'PUBLISHED':
    case 'PUBLICADO':
    case 'SUCCESS':
      return {
        color: 'text-green-500',
        bg: 'bg-green-500/10',
        border: 'border-green-500/20',
        dot: 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.4)]'
      }
    case 'STANDBY':
    case 'WARNING':
    case 'REVISIÓN':
    case 'TRADUCCIÓN':
    case 'WAITING':
      return {
        color: 'text-amber-500',
        bg: 'bg-amber-500/10',
        border: 'border-amber-500/20',
        dot: 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.4)]'
      }
    case 'OFFLINE':
    case 'ERROR':
    case 'FAILED':
      return {
        color: 'text-red-500',
        bg: 'bg-red-500/10',
        border: 'border-red-500/20',
        dot: 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.4)]'
      }
    case 'DRAFT':
    case 'BORRADOR':
    default:
      return {
        color: 'text-neutral-400',
        bg: 'bg-white/5',
        border: 'border-white/10',
        dot: 'bg-neutral-600'
      }
  }
})
</script>

<template>
  <div v-if="props.type === 'dot'" class="flex items-center gap-2">
    <span :class="['w-2 h-2 rounded-full shrink-0', statusConfig.dot]"></span>
    <span :class="['font-mono text-[10px] font-black tracking-[0.2em] uppercase whitespace-nowrap', statusConfig.color]">
      {{ props.label }}
    </span>
  </div>
  
  <span v-else :class="[
    'text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border shadow-sm',
    statusConfig.color, statusConfig.bg, statusConfig.border
  ]">
    {{ props.label }}
  </span>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSystemStore } from '../stores/system'
import { UI_STRINGS } from '../constants/uiStrings'
import BaseIcon from './BaseIcon.vue'
import StatusBadge from './StatusBadge.vue'

const store = useSystemStore()
const { vitals } = storeToRefs(store)
const { startPolling, stopPolling } = store

onMounted(() => {
    startPolling(10000)
})

onUnmounted(() => {
    stopPolling()
})
</script>

<template>
    <div class="w-full flex items-center justify-between border-t border-accent/20 px-6 py-2 bg-black/40">
        <div class="flex items-center gap-2">
            <BaseIcon name="vitals" class="text-accent w-4 h-4" />
            <h2 class="text-xs font-bold text-neutral-400 tracking-widest uppercase">{{ UI_STRINGS.system.title }}</h2>
        </div>

        <div class="flex items-center gap-4">
            <div v-for="(service, id) in vitals" :key="id" 
                 class="flex items-center gap-2 px-2 py-1 rounded bg-transparent group transition-colors hover:bg-white/5">
                <span class="text-xs font-medium text-neutral-500 group-hover:text-neutral-300 transition-colors">{{ service.label }}</span>
                
                <div class="flex items-center gap-2">
                    <BaseIcon v-if="service.status === 'POLLING'" name="polling" class="w-3 h-3 text-neutral-600 animate-spin" />
                    <StatusBadge 
                        v-if="service && service.status"
                        :status="service.status" 
                        :label="UI_STRINGS.system.status[service.status.toLowerCase()] || service.status" 
                        type="dot" 
                    />
                </div>
            </div>
        </div>
    </div>
</template>

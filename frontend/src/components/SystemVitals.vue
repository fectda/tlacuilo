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
    <div class="glass-card border-l-2 border-l-accent/50 p-6 bg-black/40">
        <div class="flex items-center gap-2 mb-6">
            <BaseIcon name="vitals" class="text-accent" />
            <h2 class="text-lg font-bold text-white tracking-tight">{{ UI_STRINGS.system.title }}</h2>
        </div>

        <div class="space-y-3">
            <div v-for="(service, id) in vitals" :key="id" 
                 class="flex items-center justify-between p-3 bg-white/5 border border-white/5 rounded-lg group transition-colors hover:bg-white/10">
                <span class="text-sm font-medium text-neutral-400 group-hover:text-neutral-200 transition-colors">{{ service.label }}</span>
                
                <div class="flex items-center gap-3">
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

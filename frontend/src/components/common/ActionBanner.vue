<script setup>
import { computed } from 'vue'

const props = defineProps({
    status: { type: String, default: null }, // 'success' | 'error' | 'loading'
    message: String,
    title: String
})

const isVisible = computed(() => !!props.status)

const theme = computed(() => {
    switch (props.status) {
        case 'success': return {
            bg: 'rgba(6, 78, 59, 0.9)',
            border: '#10b981',
            glow: '0 0 40px rgba(16, 185, 129, 0.3)',
            icon: '#10b981',
            bar: '#10b981'
        }
        case 'error': return {
            bg: 'rgba(69, 10, 10, 0.9)',
            border: '#ef4444',
            glow: '0 0 40px rgba(239, 68, 68, 0.35)',
            icon: '#ef4444',
            bar: '#ef4444'
        }
        case 'loading': return {
            bg: 'rgba(30, 20, 0, 0.95)',
            border: '#f59e0b',
            glow: '0 0 40px rgba(245, 158, 11, 0.3)',
            icon: '#f59e0b',
            bar: '#f59e0b'
        }
        default: return {
            bg: 'rgba(0,0,0,0.9)',
            border: '#3b82f6',
            glow: 'none',
            icon: '#3b82f6',
            bar: '#3b82f6'
        }
    }
})
</script>

<template>
    <Teleport to="body">
        <div
            v-if="isVisible"
            class="fixed inset-0 z-[1200] flex items-center justify-center p-4 pointer-events-none"
        >
            <div
                class="relative flex items-center gap-5 px-6 py-5 border-2 backdrop-blur-md overflow-hidden"
                :style="{
                    background: theme.bg,
                    borderColor: theme.border,
                    boxShadow: theme.glow
                }"
            >
                <!-- Animated Progress Bar for loading -->
                <div v-if="status === 'loading'" class="absolute bottom-0 left-0 right-0 h-[2px] overflow-hidden">
                    <div class="h-full animate-[scan_1.5s_ease-in-out_infinite]" :style="{ background: theme.bar, width: '40%' }"></div>
                </div>

                <!-- Status icon -->
                <div class="shrink-0">
                    <div v-if="status === 'loading'" class="w-8 h-8 border-2 rounded-full animate-spin"
                         :style="{ borderColor: theme.icon + '30', borderTopColor: theme.icon }">
                    </div>
                    <svg v-else-if="status === 'success'" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" :style="{ color: theme.icon }">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                    </svg>
                    <svg v-else-if="status === 'error'" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" :style="{ color: theme.icon }">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>

                <!-- Divider line -->
                <div class="w-px h-10 shrink-0" :style="{ background: theme.border + '50' }"></div>

                <!-- Text content -->
                <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-black uppercase tracking-[0.2em]" :style="{ color: theme.border }">
                        {{ title || (status === 'loading' ? 'PROCESANDO...' : status === 'success' ? 'ÉXITO' : 'FALLO DEL SISTEMA') }}
                    </h4>
                    <p class="text-[13px] text-white/80 font-medium mt-1 leading-snug">
                        {{ message }}
                    </p>
                </div>

                <!-- Auto-hide dot indicator for non-loading -->
                <div v-if="status !== 'loading'" class="shrink-0 flex flex-col items-center gap-1">
                    <div class="w-1.5 h-1.5 rounded-full animate-ping" :style="{ background: theme.border }"></div>
                    <span class="text-[7px] text-white/30 font-bold uppercase tracking-widest">AUTO</span>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<style scoped>
@keyframes scan {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(350%); }
}
</style>

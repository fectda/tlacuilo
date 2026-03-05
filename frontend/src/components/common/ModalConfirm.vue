<script setup>
import { computed } from 'vue'

const props = defineProps({
    isOpen: Boolean,
    title: { type: String, default: 'CONFIRMACIÓN REQUERIDA' },
    message: String,
    confirmText: { type: String, default: 'ACEPTAR' },
    cancelText: { type: String, default: 'CANCELAR' },
    type: { type: String, default: 'info' } // info, danger, warning
})

const emit = defineEmits(['close', 'confirm'])

const accentColor = computed(() => {
    switch (props.type) {
        case 'danger': return '#ef4444' // Red-500
        case 'warning': return '#f59e0b' // Amber-500
        default: return '#3b82f6' // Blue-500
    }
})

const handleConfirm = () => {
    emit('confirm')
    emit('close')
}
</script>

<template>
    <Teleport to="body">
        <div v-if="isOpen" class="fixed inset-0 z-[1000] flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm animate-in fade-in duration-200">
            <div 
                class="w-full max-w-md bg-[#050505] border-t-2 shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col animate-in zoom-in-95 duration-200"
                :style="{ borderColor: accentColor }"
            >
                <!-- Header -->
                <div class="px-6 py-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-1 h-4" :style="{ background: accentColor }"></div>
                        <span class="text-[10px] font-black tracking-[0.3em] uppercase text-white/90">{{ title }}</span>
                    </div>
                    <button @click="emit('close')" class="text-neutral-500 hover:text-white transition-colors">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                </div>

                <!-- Body -->
                <div class="p-8">
                    <p class="text-[13px] text-neutral-300 font-medium leading-relaxed">
                        {{ message }}
                    </p>
                </div>

                <!-- Footer -->
                <div class="px-6 py-4 border-t border-white/5 bg-white/5 flex items-center justify-end gap-4">
                    <button 
                        @click="emit('close')"
                        class="px-4 py-2 text-[10px] uppercase font-bold tracking-[0.2em] text-neutral-500 hover:text-white transition-colors"
                    >
                        {{ cancelText }}
                    </button>
                    <button 
                        @click="handleConfirm"
                        class="px-6 py-2 text-[10px] uppercase font-bold tracking-[0.2em] text-white transition-all shadow-lg hover:brightness-110 active:translate-y-0.5"
                        :style="{ background: accentColor }"
                    >
                        {{ confirmText }}
                    </button>
                </div>

                <!-- Corner Accent -->
                <div class="absolute bottom-0 right-0 w-8 h-8 opacity-20 pointer-events-none overflow-hidden">
                    <div class="absolute bottom-[-16px] right-[-16px] w-12 h-12 rotate-45" :style="{ background: accentColor }"></div>
                </div>
            </div>
        </div>
    </Teleport>
</template>

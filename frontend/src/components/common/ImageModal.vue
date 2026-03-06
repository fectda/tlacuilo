<script setup>
import { onMounted, onUnmounted } from 'vue'

const props = defineProps({
    isOpen: Boolean,
    imageUrl: String,
    title: String
})

const emit = defineEmits(['close'])

const handleKeydown = (e) => {
    if (e.key === 'Escape') emit('close')
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
    <Teleport to="body">
        <Transition
            enter-active-class="transition duration-300 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition duration-200 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
        >
            <div 
                v-if="isOpen" 
                class="fixed inset-0 z-[2000] flex flex-col bg-black/95 backdrop-blur-xl pointer-events-auto"
                @click.self="emit('close')"
            >
                <!-- Header -->
                <div class="flex items-center justify-between px-8 py-6 border-b border-white/5 bg-black/40">
                    <div class="flex items-center gap-4">
                        <div class="w-1 h-6 bg-cyan-500"></div>
                        <div class="flex flex-col">
                            <span class="text-[10px] font-black tracking-[0.3em] uppercase text-cyan-500/80">Visualización de Detalle</span>
                            <span class="text-sm font-bold tracking-widest uppercase text-white">{{ title || 'Imagen de Proyecto' }}</span>
                        </div>
                    </div>
                    
                    <button 
                        @click="emit('close')"
                        class="group flex items-center gap-3 px-4 py-2 border border-white/10 hover:border-white/30 transition-all"
                    >
                        <span class="text-[9px] font-black tracking-widest text-neutral-500 group-hover:text-white uppercase transition-colors">Cerrar [ESC]</span>
                        <svg class="w-5 h-5 text-neutral-500 group-hover:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <!-- Main Image Area -->
                <div class="flex-1 relative flex items-center justify-center p-8 overflow-hidden" @click.self="emit('close')">
                    <div class="relative max-w-full max-h-full shadow-[0_0_100px_rgba(37,188,192,0.1)] group">
                        <img 
                            :src="imageUrl" 
                            class="max-w-full max-h-[80vh] object-contain border border-white/10 animate-in zoom-in-95 duration-500"
                            :alt="title"
                        />
                        
                        <!-- Overlay accents -->
                        <div class="absolute -top-px -left-px w-8 h-8 border-t border-l border-cyan-500/50"></div>
                        <div class="absolute -bottom-px -right-px w-8 h-8 border-b border-r border-cyan-500/50"></div>
                    </div>
                </div>

                <!-- Footer / Technical Meta -->
                <div class="px-8 py-4 bg-black/60 border-t border-white/5 flex items-center justify-between">
                    <div class="flex items-center gap-8 font-mono text-[9px] text-neutral-500 tracking-[0.2em]">
                        <div class="flex flex-col gap-0.5">
                            <span class="text-neutral-700">SOURCE</span>
                            <span class="text-neutral-400">IXTLI_GEN_V1</span>
                        </div>
                        <div class="flex flex-col gap-0.5">
                            <span class="text-neutral-700">RENDER</span>
                            <span class="text-neutral-400">HIGH_FIDELITY</span>
                        </div>
                    </div>
                    
                    <a 
                        :href="imageUrl" 
                        target="_blank"
                        class="text-[9px] font-black tracking-widest text-cyan-500 hover:text-white transition-colors uppercase flex items-center gap-2"
                    >
                        Abrir en nueva pestaña
                        <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                    </a>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<style scoped>
.v-enter-active,
.v-leave-active {
  transition: opacity 0.3s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>

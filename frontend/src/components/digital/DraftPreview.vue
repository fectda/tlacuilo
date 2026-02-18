<script setup>
import { defineProps } from 'vue'

const props = defineProps(['projectId', 'content'])

// Placeholder for content. In a real scenario, we might want to fetch the content 
// from the ProjectStore or receive it as a prop.
// For now, we assume parent passes content or we fetch it.

const saveToDisk = () => {
    console.log('Save to disk clicked')
    // Implementation for saving would call ProjectStore action
}
</script>

<template>
    <div class="flex flex-col h-full bg-black text-neutral-300">
        <!-- Sticky Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-black/80 backdrop-blur-sm z-10 sticky top-0">
            <h2 class="text-xs font-mono text-neutral-500 uppercase tracking-widest">
                DRAFT PREVIEW
            </h2>
            <button 
                @click="saveToDisk"
                class="flex items-center gap-2 text-xs font-mono px-3 py-1.5 bg-neutral-900 border border-green-500/30 text-green-500 hover:bg-green-500/10 transition-all rounded"
            >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
                SAVE TO DISK
            </button>
        </div>

        <!-- Content Area -->
        <div class="flex-1 overflow-y-auto p-8 prose prose-invert prose-neutral max-w-none">
             <div v-if="!props.content" class="h-full flex flex-col items-center justify-center text-neutral-600">
                <p class="font-mono text-xs mb-2">NO DRAFT CONTENT</p>
                <p class="text-sm">Genera un borrador en el chat para previsualizarlo aquí.</p>
            </div>
            
            <article v-else class="whitespace-pre-wrap font-mono text-sm leading-relaxed">
                {{ props.content }}
            </article>
        </div>
    </div>
</template>

<style scoped>
/* Basic styling for the preview area */
</style>

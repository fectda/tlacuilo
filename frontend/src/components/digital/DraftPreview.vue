<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import { useProjectStore } from '../../stores/project'

const props = defineProps(['collection', 'slug', 'content', 'isTranslation'])
const projectStore = useProjectStore()

const renderMarkdown = (text) => {
    if (!text) return ''
    return marked(text)
}

const handleManualSave = async () => {
    try {
        if (props.isTranslation) {
             await projectStore.persistTranslation(props.collection, props.slug, props.content)
        } else {
             await projectStore.persistContent(props.collection, props.slug, props.content)
        }
        // In a real app we might use a toast, but keeping it simple/premium as per rules
    } catch (e) {
        console.error(e)
    }
}

const handlePromote = async () => {
    try {
        if (confirm('¿Estás seguro de promover este borrador al Portafolio?')) {
            await projectStore.promoteProject(props.collection, props.slug)
        }
    } catch (e) {
        console.error(e)
    }
}

const validation = computed(() => {
    if (props.isTranslation) return null
    return projectStore.currentProject?.validation || null
})

const isWorkingCopyActive = computed(() => {
    return projectStore.currentProject?.is_working_copy_active || false
})
</script>

<template>
    <div class="flex flex-col h-full bg-[#050505] text-neutral-300 relative border-l border-white/5">
        <!-- Sticky Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[#050505]/90 backdrop-blur-md z-10 sticky top-0">
            <div class="flex flex-col">
                <h2 class="text-[10px] font-bold text-white uppercase tracking-[0.2em]">
                    {{ isTranslation ? 'English Translation' : 'Archivo Maestro' }}
                </h2>
                <span class="text-[8px] text-neutral-600 uppercase tracking-widest mt-0.5">
                    {{ slug }}{{ isTranslation ? '.en' : '' }}.md
                </span>
            </div>
            
            <div class="flex gap-2">
                 <button v-if="!isTranslation && isWorkingCopyActive"
                    @click="handlePromote"
                    class="flex items-center gap-2 text-[9px] font-bold px-3 py-1.5 bg-amber-500 text-black hover:bg-amber-400 transition-all uppercase tracking-widest shadow-[0_0_15px_rgba(245,158,11,0.2)]"
                >
                    Promover al Portafolio
                </button>

                <button 
                    @click="handleManualSave"
                    class="flex items-center gap-2 text-[9px] font-bold px-3 py-1.5 bg-neutral-900 border border-neutral-700 text-neutral-300 hover:text-white hover:border-neutral-500 transition-all uppercase tracking-widest"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
                    Guardar
                </button>
            </div>
        </div>

        <!-- Validation Results Banner -->
        <div v-if="validation" class="px-6 py-2 border-b border-white/5 bg-[#0a0a0a] space-y-1">
            <div v-if="validation.schema_check?.valid" class="text-[9px] text-emerald-500 flex items-center gap-2">
                <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
                SCHEMA OK
            </div>
            <div v-else-if="validation.schema_check" class="text-[9px] text-red-500 flex items-center gap-2 font-bold animate-pulse">
                <span class="w-1.5 h-1.5 bg-red-500 rounded-full"></span>
                ERROR DE SCHEMA: {{ validation.schema_check.error }}
            </div>

            <div v-if="validation.spellcheck?.errors?.length > 0" class="text-[9px] text-amber-500 flex items-center gap-2">
                <span class="w-1.5 h-1.5 bg-amber-500 rounded-full"></span>
                {{ validation.spellcheck.errors.length }} POSIBLES ERRORES DE ORTOGRAFÍA
            </div>
        </div>

        <!-- Content Area -->
        <div class="flex-1 overflow-y-auto p-10 custom-scrollbar selection:bg-amber-500 selection:text-black">
             <div v-if="!props.content" class="h-full flex flex-col items-center justify-center text-neutral-800">
                <p class="font-mono text-xs mb-2 uppercase tracking-[0.3em] font-bold">SIN DATOS</p>
                <p class="text-[10px] font-mono tracking-widest opacity-30">EL ARCHIVO ESTÁ VACÍO O NO HA SIDO CARGADO.</p>
            </div>
            
            <article v-else class="prose prose-invert prose-xs max-w-none font-mono leading-relaxed prose-headings:uppercase prose-headings:tracking-widest prose-headings:text-neutral-200">
                <div v-html="renderMarkdown(props.content)"></div>
            </article>
        </div>
    </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: #050505;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #262626;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #404040;
}
</style>

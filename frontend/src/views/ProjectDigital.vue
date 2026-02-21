<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../stores/project'
import { useChatStore } from '../stores/chat'
import ChatArea from '../components/digital/ChatArea.vue'
import DraftPreview from '../components/digital/DraftPreview.vue'

const route = useRoute()
const projectStore = useProjectStore()
const chatStore = useChatStore()
const { collection, slug } = route.params
const previewRef = ref(null)

onMounted(async () => {
    try {
        // 1. Get metadata from the global list (cached or fetched)
        await projectStore.fetchProjectFromList(collection, slug)

        // 2. Load context (Content & History)
        await Promise.all([
            projectStore.fetchContent(collection, slug),
            chatStore.fetchHistory(collection, slug)
        ])

        // 3. TRIGGER SESSION (Ciclo de Inicio)
        // Must be called after loading history to avoid race conditions.
        // If history is empty, /init will trigger the first message.
        // If there's technical debt, /init will trigger the missing reply.
        await chatStore.initSession(collection, slug)

    } catch (e) {
        console.warn('Initialization warning:', e)
    }
})

const viewMode = ref('original') // 'original' | 'translation'

// Computed content for preview
const temporaryDraft = ref(null)

const currentContent = computed(() => {
    if (temporaryDraft.value) {
        return temporaryDraft.value
    }
    if (viewMode.value === 'translation') {
        return projectStore.currentTranslation?.content || ''
    }
    return projectStore.currentProject?.content || ''
})

const handleDraftGenerated = (content) => {
    temporaryDraft.value = content
}

// Handlers for Translation
const toggleViewMode = async (mode) => {
    viewMode.value = mode
    if (mode === 'translation') {
        if (!projectStore.currentTranslation) {
            await projectStore.fetchTranslation(collection, slug)
        }
        chatStore.mode = 'translation' 
    } else {
        chatStore.mode = 'interview'
    }
}

const handleStartTranslation = async () => {
    if (confirm('¿Iniciar traducción al inglés? Esto generará una propuesta basada en la versión publicada.')) {
        await chatStore.translateDraft(collection, slug, { from_scratch: true })
        await projectStore.fetchTranslation(collection, slug) // Refresh to see result
        viewMode.value = 'translation'
    }
}

const handlePublishTranslation = async () => {
     if (confirm('¿Publicar traducción al Portafolio?')) {
        await projectStore.publishTranslation(collection, slug)
        alert('Traducción publicada.')
    }
}

const handleRevert = async () => {
    if (confirm('¿Estás seguro de descartar todos los cambios locales y volver a la versión del Portafolio?')) {
        await projectStore.revertProject(collection, slug)
    }
}

const handlePublish = async () => {
    if (confirm('¿Deseas promover esta copia de trabajo al Portafolio?')) {
        await projectStore.promoteProject(collection, slug)
    }
}

const handleChildSave = async () => {
    if (previewRef.value) {
        await previewRef.value.handleManualSave()
    }
}

const handleDiscardDraft = () => {
    temporaryDraft.value = null
}

// Clear temporary draft when changing view modes or reverting
watch(viewMode, () => temporaryDraft.value = null)
watch(() => projectStore.currentProject?.content, () => temporaryDraft.value = null)

</script>

<template>
    <div class="flex flex-col h-screen bg-black overflow-hidden font-mono">
        <!-- Header / Status Bar -->
        <div class="flex items-center justify-between px-6 py-3 border-b border-white/10 bg-[#0a0a0a]">
            <!-- Left: Navigation & Title -->
            <div class="flex items-center gap-4">
                <router-link to="/" class="text-neutral-500 hover:text-white transition-colors">
                    &lt; VOLVER
                </router-link>
                <div class="h-4 w-[1px] bg-white/10"></div>
                <h1 class="text-sm font-bold tracking-widest uppercase truncate max-w-[200px]">
                    {{ projectStore.currentProject?.name || slug }}
                </h1>
                
                <!-- Status & Mode Indicators -->
                <div class="flex items-center gap-2">
                    <span v-if="projectStore.currentProject?.doc_status === 'promovido' && viewMode === 'original'"
                          class="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 text-[10px] tracking-tighter uppercase font-bold">
                        Promovido
                    </span>
                    <span v-else-if="projectStore.isWorkingCopyActive && viewMode === 'original'" 
                          class="bg-amber-500/10 text-amber-500 border border-amber-500/20 px-2 py-0.5 text-[10px] tracking-tighter uppercase">
                        Copia de Trabajo
                    </span>
                    <span v-else-if="viewMode === 'original'"
                          class="bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 px-2 py-0.5 text-[10px] tracking-tighter uppercase font-bold">
                        Sincronizado
                    </span>
                     <span v-if="viewMode === 'translation'" 
                          class="bg-blue-500/10 text-blue-500 border border-blue-500/20 px-2 py-0.5 text-[10px] tracking-tighter uppercase">
                        Modo Traducción
                    </span>
                </div>
            </div>

            <!-- Center: View Toggle REMOVED -->
            <div class="flex items-center justify-center flex-1">
                 <span class="text-[9px] text-neutral-600 uppercase tracking-[0.3em] font-bold">
                    {{ viewMode === 'translation' ? 'TRADUCCIÓN EN' : 'ESPACIO DE TRABAJO' }}
                </span>
            </div>

            <!-- Right: Actions -->
            <div class="flex items-center gap-3">
                <!-- Translation Actions -->
                <template v-if="viewMode === 'translation'">
                     <button v-if="!projectStore.currentTranslation"
                            @click="handleStartTranslation"
                            class="text-[10px] bg-blue-600/20 text-blue-500 border border-blue-500/50 hover:bg-blue-600 hover:text-white px-3 py-1 transition-all uppercase tracking-widest">
                        Iniciar Traducción
                    </button>
                     <button v-if="projectStore.currentTranslation"
                            @click="handlePublishTranslation"
                            class="text-[10px] bg-white text-black hover:bg-neutral-200 px-3 py-1 transition-all uppercase tracking-widest font-bold">
                        Publicar EN
                    </button>
                </template>

                <!-- Original Actions -->
                <template v-else>
                    <template v-if="projectStore.isWorkingCopyActive && !temporaryDraft">
                        <button @click="handleRevert"
                                class="text-[10px] border border-red-500/30 text-red-500/70 hover:text-red-500 hover:border-red-500 px-3 py-1 transition-all uppercase tracking-widest">
                            DESCARTAR CAMBIOS
                        </button>
                        <button @click="handlePublish"
                                class="text-[10px] bg-white text-black hover:bg-neutral-200 px-3 py-1 transition-all uppercase tracking-widest font-bold">
                            PROMOVER
                        </button>
                    </template>
                </template>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex flex-1 overflow-hidden">
            <!-- Left Pane: Chat (40%) -->
            <div class="w-[40%] h-full relative z-10">
                <ChatArea 
                    :collection="collection" 
                    :slug="slug" 
                />
            </div>

            <!-- Right Pane: Preview (60%) -->
            <div class="w-[60%] h-full bg-[#050505]">
                <DraftPreview 
                    ref="previewRef"
                    :collection="collection" 
                    :slug="slug" 
                    :content="currentContent" 
                    :isTranslation="viewMode === 'translation'"
                    @draft-generated="handleDraftGenerated"
                    @discard-draft="handleDiscardDraft"
                />
            </div>
        </div>
    </div>
</template>

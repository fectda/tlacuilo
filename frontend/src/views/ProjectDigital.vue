<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../stores/project'
import { useChatStore } from '../stores/chat'
import ChatArea from '../components/digital/ChatArea.vue'
import DraftPreview from '../components/digital/DraftPreview.vue'

const route = useRoute()
const projectStore = useProjectStore()
const chatStore = useChatStore()
const { collection, slug } = route.params

onMounted(async () => {
    try {
        // 1. Fetch metadata (Name, etc.) - Essential for header
        await projectStore.fetchProject(collection, slug)

        // 2. Context Synchronization (Parallel per Architecture)
        // GET /content -> Authoritative content & status
        // GET /chat/history -> Chat history
        await Promise.all([
            projectStore.fetchContent(collection, slug),
            chatStore.fetchHistory(collection, slug)
        ])
    } catch (e) {
        console.warn('Initialization warning:', e)
    }
})

const viewMode = ref('original') // 'original' | 'translation'

// Computed content for preview
const currentContent = computed(() => {
    if (viewMode.value === 'translation') {
        return projectStore.currentTranslation?.content || ''
    }
    return projectStore.currentProject?.content || ''
})

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
        // In this architecture, publishing translation might be the same as publishing the project
        // but focusing on English content. For now we use the general publish.
        await projectStore.publishProject(collection, slug)
        alert('Traducción publicada.')
    }
}

const handleRevert = async () => {
    if (confirm('¿Estás seguro de descartar todos los cambios locales y volver a la versión del Portafolio?')) {
        await projectStore.revertProject(collection, slug)
    }
}

const handlePublish = async () => {
    if (confirm('¿Deseas publicar esta copia de trabajo al Portafolio?')) {
        await projectStore.publishProject(collection, slug)
    }
}
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
                    <span v-if="projectStore.isWorkingCopyActive && viewMode === 'original'" 
                          class="bg-amber-500/10 text-amber-500 border border-amber-500/20 px-2 py-0.5 text-[10px] tracking-tighter uppercase">
                        Copia de Trabajo
                    </span>
                    <span v-else-if="viewMode === 'original'"
                          class="bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 px-2 py-0.5 text-[10px] tracking-tighter uppercase">
                        Sincronizado
                    </span>
                     <span v-if="viewMode === 'translation'" 
                          class="bg-blue-500/10 text-blue-500 border border-blue-500/20 px-2 py-0.5 text-[10px] tracking-tighter uppercase">
                        Modo Traducción
                    </span>
                </div>
            </div>

            <!-- Center: View Toggle -->
            <div class="flex bg-neutral-900 border border-neutral-800 p-1 gap-1">
                <button 
                    @click="toggleViewMode('original')"
                    :class="viewMode === 'original' ? 'bg-neutral-800 text-white' : 'text-neutral-500 hover:text-neutral-300'"
                    class="px-3 py-1 text-[10px] uppercase tracking-widest transition-all">
                    Español
                </button>
                <button 
                    @click="toggleViewMode('translation')"
                    :class="viewMode === 'translation' ? 'bg-neutral-800 text-white' : 'text-neutral-500 hover:text-neutral-300'"
                    class="px-3 py-1 text-[10px] uppercase tracking-widest transition-all">
                    English
                </button>
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
                    <button v-if="projectStore.isWorkingCopyActive"
                            @click="handleRevert"
                            class="text-[10px] border border-red-500/30 text-red-500/70 hover:text-red-500 hover:border-red-500 px-3 py-1 transition-all uppercase tracking-widest">
                        Descartar
                    </button>
                    <button v-if="projectStore.isWorkingCopyActive"
                            @click="handlePublish"
                            class="text-[10px] bg-white text-black hover:bg-neutral-200 px-3 py-1 transition-all uppercase tracking-widest font-bold">
                        Publicar
                    </button>
                </template>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex flex-1 overflow-hidden">
            <!-- Left Pane: Chat (60%) -->
            <div class="w-[60%] h-full">
                <ChatArea :collection="collection" :slug="slug" />
            </div>

            <!-- Right Pane: Preview (40%) -->
            <div class="w-[40%] h-full border-l border-white/10">
                <DraftPreview 
                    :collection="collection" 
                    :slug="slug" 
                    :content="currentContent" 
                    :isTranslation="viewMode === 'translation'"
                />
            </div>
        </div>
    </div>
</template>

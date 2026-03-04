<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../stores/project'
import { useChatStore } from '../stores/chat'
import ChatArea from '../components/digital/ChatArea.vue'
import TranslationStudio from '../components/digital/TranslationStudio.vue'
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

const originalDraft = ref(null)
const translationDraft = ref(null)

const handleDraftGenerated = (content) => {
    if (viewMode.value === 'translation') {
        translationDraft.value = content
    } else {
        originalDraft.value = content
    }
}

// Handlers for Translation
const toggleViewMode = async (mode) => {
    viewMode.value = mode
    if (mode === 'translation') {
        if (!projectStore.currentTranslation || projectStore.currentTranslation.source === 'empty') {
            await projectStore.fetchTranslation(collection, slug)
        }
        chatStore.mode = 'translation' 
    } else {
        chatStore.mode = 'interview'
    }
}

const handleGlobalPromotion = async () => {
    // Re-verify Section D status if needed
     if (confirm('¿Ejecutar PROMOCIÓN GLOBAL? (Git Ops: Commit & Push al repositorio remoto)')) {
        await projectStore.publishGlobal(collection, slug)
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
    if (viewMode.value === 'translation') {
        translationDraft.value = null
    } else {
        originalDraft.value = null
    }
}

// Clear temporary drafts when reverting
watch(() => projectStore.currentProject?.content, () => originalDraft.value = null)
watch(() => projectStore.currentTranslation?.content, () => translationDraft.value = null)
watch(() => projectStore.isWorkingCopyActive, (val) => {
    if (!val) originalDraft.value = null
})

</script>

<template>
    <div class="flex flex-col h-full bg-black overflow-hidden font-mono">
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
                <div class="flex items-center gap-2 cursor-pointer group" @click="toggleViewMode(viewMode === 'original' ? 'translation' : 'original')">
                    <span v-if="viewMode === 'original'"
                          class="bg-amber-500/10 text-amber-500 border border-amber-500/20 px-3 py-1 text-[10px] tracking-[0.2em] uppercase font-black transition-all group-hover:bg-amber-500/20 group-hover:text-amber-400">
                        EDICIÓN
                    </span>
                    <span v-else 
                          class="bg-blue-500/10 text-blue-500 border border-blue-500/20 px-3 py-1 text-[10px] tracking-[0.2em] uppercase font-black transition-all group-hover:bg-blue-500/20 group-hover:text-blue-400">
                        TRADUCCIÓN
                    </span>
                </div>

                <!-- Studio Link -->
                <router-link
                    :to="`/project/${collection}/${slug}/studio`"
                    class="bg-cyan-500/5 text-cyan-600 border border-cyan-500/10 px-3 py-1 text-[10px] tracking-[0.2em] uppercase font-black hover:bg-cyan-500/10 hover:text-cyan-400 transition-all"
                >
                    ⌀ IXTLI
                </router-link>
            </div>

            <!-- Center: Breadcrumbs (Static in Header) -->
            <div class="flex items-center justify-center flex-1">
                <span class="text-[9px] text-neutral-500 uppercase tracking-[0.4em] font-mono">
                    {{ collection }} / <span class="text-white">{{ slug }}</span>
                </span>
            </div>

            <!-- Right: Contextual Actions -->
            <div class="flex items-center gap-3">
                <template v-if="projectStore.isWorkingCopyActive">
                    <button @click="handleRevert"
                            class="text-[10px] border border-red-500/50 text-red-500 hover:bg-red-500/10 px-4 py-1.5 transition-all uppercase tracking-[0.2em] font-black">
                        DESCARTAR
                    </button>
                    <button @click="handlePublish"
                            class="text-[10px] bg-white text-black hover:bg-neutral-200 px-4 py-1.5 transition-all uppercase tracking-[0.2em] font-black shadow-xl">
                        PROMOVER
                    </button>
                </template>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex flex-1 overflow-hidden">
            <!-- Dynamic Workspace Left Pane -->
            <div v-if="viewMode === 'original'" class="w-[40%] h-full relative z-10">
                <ChatArea :collection="collection" :slug="slug" />
            </div>
            <div v-else class="w-[40%] h-full relative z-10">
                <TranslationStudio :collection="collection" :slug="slug" @draft-generated="handleDraftGenerated" />
            </div>

            <!-- Left Sidebar Removed -->

            <!-- Right Workspace: Preview / Editor -->
            <div class="flex-1 overflow-hidden relative group">
                <!-- Actions Bar Removed (Consolidated in Header) -->

                <DraftPreview 
                    v-show="viewMode === 'original'"
                    :collection="collection" 
                    :slug="slug" 
                    :content="originalDraft !== null ? originalDraft : (projectStore.currentProject?.content || '')" 
                    :isTranslation="false"
                    @draft-generated="handleDraftGenerated"
                    @discard-draft="handleDiscardDraft"
                    @update:content="c => originalDraft = c"
                />
                <DraftPreview 
                    v-show="viewMode === 'translation'"
                    :collection="collection" 
                    :slug="slug" 
                    :content="translationDraft !== null ? translationDraft : (projectStore.currentTranslation?.content || '')" 
                    :isTranslation="true"
                    @draft-generated="handleDraftGenerated"
                    @discard-draft="handleDiscardDraft"
                    @update:content="c => translationDraft = c"
                />
            </div>
        </div>

    </div>
</template>

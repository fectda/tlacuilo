<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useStudioStore } from '../stores/studio'
import { useProjectStore } from '../stores/project'
import ShotCard from '../components/studio/ShotCard.vue'
import CreateShotModal from '../components/studio/CreateShotModal.vue'
import ShotDetailPanel from '../components/studio/ShotDetailPanel.vue'
import { UI_TEXTS } from '../constants/uiTexts'
import ModalConfirm from '../components/common/ModalConfirm.vue'
import ActionBanner from '../components/common/ActionBanner.vue'

const texts = { ...UI_TEXTS.PROJECT_COMMON, ...UI_TEXTS.PROJECT_STUDIO }
const commonTexts = UI_TEXTS.COMMON

const route = useRoute()
const studioStore = useStudioStore()
const projectStore = useProjectStore()

const { collection, slug } = route.params
const showCreateModal = ref(false)

// Modal State
const confirmModal = ref({
    show: false,
    title: '',
    message: '',
    type: 'info',
    onConfirm: () => {}
})

const showConfirm = (title, message, onConfirm, type = 'info') => {
    confirmModal.value = { show: true, title, message, onConfirm, type }
}

onMounted(async () => {
    await projectStore.fetchProjectFromList(collection, slug)
    await studioStore.fetchShots(collection, slug)
})

const handleSelectShot = async (shot) => {
    await studioStore.selectShot(collection, slug, shot.shot_id)
}

const handleDeleteShot = async (shotId) => {
    showConfirm(
        'ELIMINAR SHOT',
        texts.CONFIRM_DELETE_SHOT,
        () => studioStore.deleteShot(collection, slug, shotId),
        'danger'
    )
}

const handleSuggest = async () => {
    await studioStore.suggestShots(collection, slug)
}

const handleCreateShot = async (payload) => {
    await studioStore.createShot(collection, slug, payload)
    showCreateModal.value = false
}

const handleGlobalPromotion = async () => {
    showConfirm(
        'EJECUTAR PUBLICACIÓN',
        texts.CONFIRM_PUBLISH,
        () => projectStore.publishProject(collection, slug),
        'warning'
    )
}
</script>

<template>
    <div class="flex flex-col h-full bg-black overflow-hidden font-mono">

        <!-- Header / Status Bar -->
        <div class="flex items-center justify-between px-6 py-3 border-b border-white/10 bg-[#0a0a0a] shrink-0">
            <!-- Left: Navigation -->
            <div class="flex items-center gap-4">
                <router-link :to="`/project/${collection}/${slug}`" class="text-neutral-500 hover:text-white transition-colors text-xs">
                    &lt; {{ texts.BACK }}
                </router-link>
                <div class="h-4 w-[1px] bg-white/10"></div>
                <h1 class="text-sm font-bold tracking-widest uppercase truncate max-w-[200px]">
                    {{ projectStore.currentProject?.name || slug }}
                </h1>
                <span class="bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-3 py-1 text-[10px] tracking-[0.2em] uppercase font-black">
                    {{ texts.TITLE }}
                </span>
            </div>

            <!-- Center: Breadcrumb -->
            <div class="flex items-center justify-center flex-1">
                <span class="text-[9px] text-neutral-500 uppercase tracking-[0.4em] font-mono">
                    {{ collection }} / <span class="text-white">{{ slug }}</span> / studio
                </span>
            </div>

            <!-- Right: Actions -->
            <div class="flex items-center gap-2">
                <button
                    @click="showCreateModal = true"
                    class="text-[10px] border border-white/10 text-neutral-400 hover:text-white hover:border-white/30 px-4 py-1.5 transition-all uppercase tracking-[0.2em] font-black"
                >
                    {{ texts.NEW_SHOT }}
                </button>
                <button
                    @click="handleSuggest"
                    :disabled="studioStore.isSuggesting"
                    class="text-[10px] bg-cyan-600/20 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-600/30 px-4 py-1.5 transition-all uppercase tracking-[0.2em] font-black disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    <span v-if="studioStore.isSuggesting">{{ texts.ANALYZING }}</span>
                    <span v-else>{{ texts.SUGGEST_AI }}</span>
                </button>
                <div class="h-4 w-[1px] bg-white/10 mx-1"></div>
                <button @click="handleGlobalPromotion"
                        class="text-[10px] bg-amber-600/20 text-amber-500 border border-amber-500/30 hover:bg-amber-600/30 px-4 py-1.5 transition-all uppercase tracking-[0.2em] font-black"
                        :title="texts.PUBLISH_TOOLTIP">
                    {{ texts.PUBLISH }}
                </button>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex flex-1 overflow-hidden">

            <!-- Left: Shot List -->
            <div class="w-[280px] flex flex-col shrink-0 border-r border-white/5 bg-[#050505]">
                <!-- Panel Header -->
                <div class="px-5 py-3 border-b border-white/5 bg-[#070707]">
                    <div class="flex items-center justify-between">
                        <span class="text-[9px] font-black tracking-[0.3em] uppercase text-neutral-500">{{ texts.SHOT_LIST }}</span>
                        <span class="text-[9px] text-neutral-700">{{ studioStore.shots.length }} {{ commonTexts.SHOTS || 'shots' }}</span>
                    </div>
                </div>

                <!-- Shot Cards -->
                <div class="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-1">
                    <!-- Loading state -->
                    <div v-if="studioStore.isLoading" class="flex items-center justify-center py-12 text-neutral-700">
                        <div class="flex gap-1.5">
                            <div v-for="i in 3" :key="i" class="w-1 h-1 bg-neutral-700 rounded-full animate-bounce" :style="{ animationDelay: (i*0.2)+'s' }"></div>
                        </div>
                    </div>

                    <!-- Suggesting overlay -->
                    <div v-else-if="studioStore.isSuggesting" class="flex flex-col items-center justify-center py-12 gap-3 text-center">
                        <div class="flex gap-1.5">
                            <div v-for="i in 3" :key="i" class="w-1.5 h-1.5 bg-cyan-500/50 rounded-full animate-bounce" :style="{ animationDelay: (i*0.2)+'s' }"></div>
                        </div>
                        <p class="text-[9px] text-cyan-500/70 uppercase tracking-widest">{{ texts.ANALYZING_DOC }}</p>
                    </div>

                    <!-- Empty state -->
                    <div v-else-if="!studioStore.shots.length" class="flex flex-col items-center justify-center py-16 text-neutral-700 text-center px-4 space-y-3">
                        <span class="text-3xl opacity-20">📷</span>
                        <p class="text-[9px] uppercase tracking-widest">{{ texts.NO_SHOTS }}</p>
                        <p class="text-[8px] text-neutral-800">{{ texts.NO_SHOTS_DESC }}</p>
                    </div>

                    <!-- Shot cards -->
                    <ShotCard
                        v-else
                        v-for="shot in studioStore.shots"
                        :key="shot.shot_id"
                        :shot="shot"
                        :collection="collection"
                        :slug="slug"
                        :isSelected="studioStore.currentShot?.shot_id === shot.shot_id"
                        @select="handleSelectShot"
                        @delete="handleDeleteShot"
                    />
                </div>

                <!-- Error bar -->
                <div v-if="studioStore.error" class="px-4 py-2 bg-red-950/50 border-t border-red-500/20">
                    <p class="text-[8px] text-red-400 uppercase tracking-wider truncate">{{ studioStore.error }}</p>
                </div>
            </div>

            <!-- Right: Shot Detail -->
            <div class="flex-1 overflow-hidden">
                <ShotDetailPanel :collection="collection" :slug="slug" @delete-shot="handleDeleteShot" />
            </div>
        </div>

        <!-- Create Modal -->
        <CreateShotModal
            v-if="showCreateModal"
            @submit="handleCreateShot"
            @close="showCreateModal = false"
        />
        <!-- Feedback & Modals -->
        <ActionBanner 
            :status="projectStore.actionFeedback.status"
            :message="projectStore.actionFeedback.message"
            :title="projectStore.actionFeedback.title"
        />

        <ModalConfirm 
            :isOpen="confirmModal.show"
            :title="confirmModal.title"
            :message="confirmModal.message"
            :type="confirmModal.type"
            @close="confirmModal.show = false"
            @confirm="confirmModal.onConfirm"
        />

    </div>
</template>

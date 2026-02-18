<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../stores/project'
import { useChatStore } from '../stores/chat'
import ChatArea from '../components/digital/ChatArea.vue'
import DraftPreview from '../components/digital/DraftPreview.vue'

const route = useRoute()
const projectStore = useProjectStore()
const chatStore = useChatStore()
const { collection, slug } = route.params
const projectId = slug // slug acts as projectId

onMounted(async () => {
    // Ensure project data is loaded
    if (!projectStore.currentProject || projectStore.currentProject.id !== slug) {
         await projectStore.fetchProject(collection, slug)
    }
    
    // Initialize Chat
    await chatStore.loadHistory(projectId)
})

onUnmounted(() => {
    // Optional: chatStore.resetState() if we want to clear history on leave
})

const currentContent = computed(() => {
    // Return markdown content from project store 
    // This assumes fetchProject loads the content
    return projectStore.currentProject?.content || ''
})

</script>

<template>
    <div class="flex h-screen bg-black overflow-hidden">
        <!-- Split View Layout -->
        
        <!-- Left Pane: Chat (60%) -->
        <div class="w-[60%] h-full">
            <ChatArea :projectId="projectId" />
        </div>

        <!-- Right Pane: Preview (40%) -->
        <div class="w-[40%] h-full border-l border-white/10">
            <DraftPreview :projectId="projectId" :content="currentContent" />
        </div>
    </div>
</template>

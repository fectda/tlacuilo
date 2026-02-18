import { defineStore } from 'pinia'
import { ref } from 'vue'
import ChatService from '../services/ChatService'

export const useChatStore = defineStore('chat', () => {
    const history = ref([])
    const isTyping = ref(false)
    const mode = ref('interview')
    const error = ref(null)

    const loadHistory = async (projectId) => {
        error.value = null
        try {
            // Try to fetch existing history
            const data = await ChatService.getHistory(projectId)
            if (data && data.length > 0) {
                history.value = data
            } else {
                // If empty/new, start the chat (interviewer initiates)
                const startData = await ChatService.startChat(projectId)
                history.value = startData
            }
        } catch (e) {
            console.warn('History not found or error, attempting to start fresh:', e)
            try {
                const startData = await ChatService.startChat(projectId)
                history.value = startData
            } catch (startError) {
                error.value = startError.message || 'Failed to initialize chat'
                console.error('Chat init error:', startError)
            }
        }
    }

    const sendMessage = async (projectId, text) => {
        if (!text.trim()) return

        // Optimistic UI update (optional, but good for UX)
        // For now we'll wait for the server to return the updated history/message interaction
        // specifically because the backend agent might be fast or we want strict sync.
        // Actually, let's append user message immediately for responsiveness? 
        // The backend returns the *updated* history or just the new messages. 
        // Let's assume for now we append user message locally, then replace/append with server response.

        history.value.push({ role: 'user', content: text })
        isTyping.value = true
        error.value = null

        try {
            const response = await ChatService.sendMessage(projectId, text, mode.value)
            // Assuming response contains the Agent's reply or the updated history slice
            // If response is the full history: history.value = response
            // If response is just the new message: history.value.push(response)

            // Per ARCHITECTURE.md, `POST /chat/message` logic isn't fully detailed on response format,
            // but `POST /chat/start` returns updated history. Let's assume consistent behavior or append agent reply.
            // Adjust based on actual API response structure during integration.

            // Safe fallback: if response is array, replace/merge. If object, push.
            if (Array.isArray(response)) {
                history.value = response
            } else {
                history.value.push(response)
            }

        } catch (e) {
            error.value = e.message || 'Failed to send message'
            console.error('Send error:', e)
            // Remove the user message if failed? Or show error state.
        } finally {
            isTyping.value = false
        }
    }

    const generateDraft = async (projectId) => {
        isTyping.value = true
        try {
            await ChatService.generateDraft(projectId)
            // Draft generation might update the file on disk. 
            // Ideally we'd trigger a refresh of the DraftPreview here or via the ProjectStore.
        } catch (e) {
            console.error('Draft gen error:', e)
            error.value = e.message
        } finally {
            isTyping.value = false
        }
    }

    const resetState = () => {
        history.value = []
        isTyping.value = false
        error.value = null
        mode.value = 'interview'
    }

    return {
        history,
        isTyping,
        mode,
        error,
        loadHistory,
        sendMessage,
        generateDraft,
        resetState
    }
})

import { defineStore } from 'pinia'
import { ref } from 'vue'
import ChatService from '../services/ChatService'

export const useChatStore = defineStore('chat', () => {
    const history = ref([])
    const isTyping = ref(false)
    const isDrafting = ref(false)
    const mode = ref('interview')
    const loading = ref(false)
    const chatError = ref(null)
    const draftError = ref(null)

    const loadHistory = (messages) => {
        chatError.value = null
        draftError.value = null
        history.value = messages || []
    }

    const fetchHistory = async (collection, slug) => {
        loading.value = true
        chatError.value = null
        draftError.value = null
        try {
            const data = await ChatService.getHistory(collection, slug)
            const messages = data.messages || []
            loadHistory(messages)
            return messages
        } catch (e) {
            chatError.value = e.response?.data?.detail || e.message || 'Failed to fetch chat history'
            console.error('Fetch history error:', e)
        } finally {
            loading.value = false
        }
    }

    /**
     * Initialize session. Should be called on mount if history is empty.
     */
    const initSession = async (collection, slug) => {
        isTyping.value = true
        chatError.value = null
        draftError.value = null
        try {
            const response = await ChatService.initSession(collection, slug)
            if (response && response.content) {
                history.value.push(response)
            }
            return response
        } catch (e) {
            console.error('Init session error:', e)
            chatError.value = e.response?.data?.detail || e.message
        } finally {
            isTyping.value = false
        }
    }

    const sendMessage = async (collection, slug, text, systemOnly = false, isNote = false, responseSystemOnly = false) => {
        if (!text.trim()) return

        // Local optimistic update (only for non-system messages)
        if (!systemOnly) {
            history.value.push({ role: 'user', content: text, timestamp: new Date().toISOString() })
        }

        // Only show typing indicator if we expect an AI response that is not hidden
        if (!isNote && !responseSystemOnly) {
            isTyping.value = true
        }
        chatError.value = null
        draftError.value = null

        try {
            const payload = {
                content: text,
                system_only: systemOnly,
                is_note: isNote,
                response_system_only: responseSystemOnly
            }
            const response = await ChatService.sendMessage(collection, slug, payload)

            if (response && response.content && !isNote && !responseSystemOnly) {
                history.value.push(response)
            }
            return response
        } catch (e) {
            chatError.value = e.response?.data?.detail || e.message || 'Failed to send message'
            console.error('Send error:', e)
        } finally {
            isTyping.value = false
        }
    }

    const generateDraft = async (collection, slug) => {
        isDrafting.value = true
        chatError.value = null
        draftError.value = null
        try {
            const response = await ChatService.generateDraft(collection, slug)
            return response
        } catch (e) {
            console.error('Draft gen error:', e)
            draftError.value = e.response?.data?.detail || e.message
        } finally {
            isDrafting.value = false
        }
    }

    const translateDraft = async (collection, slug, payload) => {
        isDrafting.value = true
        chatError.value = null
        draftError.value = null
        try {
            const response = await ChatService.translateDraft(collection, slug, payload)
            return response
        } catch (e) {
            console.error('Translate draft error:', e)
            draftError.value = e.response?.data?.detail || e.message
        } finally {
            isDrafting.value = false
        }
    }

    const resetState = () => {
        history.value = []
        isTyping.value = false
        chatError.value = null
        draftError.value = null
        mode.value = 'interview'
    }

    return {
        history,
        isTyping,
        isDrafting,
        mode,
        loading,
        chatError,
        draftError,
        loadHistory,
        fetchHistory,
        initSession,
        sendMessage,
        generateDraft,
        translateDraft,
        resetState
    }
})

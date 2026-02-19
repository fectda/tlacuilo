import { defineStore } from 'pinia'
import { ref } from 'vue'
import ChatService from '../services/ChatService'

export const useChatStore = defineStore('chat', () => {
    const history = ref([])
    const isTyping = ref(false)
    const mode = ref('interview')
    const loading = ref(false)
    const error = ref(null)

    const loadHistory = (messages) => {
        error.value = null
        history.value = messages || []
    }

    const fetchHistory = async (collection, slug) => {
        loading.value = true
        error.value = null
        try {
            const data = await ChatService.getHistory(collection, slug)
            const messages = data.messages || []
            loadHistory(messages)
            return messages
        } catch (e) {
            error.value = e.message || 'Failed to fetch chat history'
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
        error.value = null
        try {
            const response = await ChatService.initSession(collection, slug)
            if (response && response.content) {
                history.value.push(response)
            }
            return response
        } catch (e) {
            console.error('Init session error:', e)
            error.value = e.message
        } finally {
            isTyping.value = false
        }
    }

    const sendMessage = async (collection, slug, text, systemOnly = false) => {
        if (!text.trim()) return

        // Local optimistic update (only for non-system messages)
        if (!systemOnly) {
            history.value.push({ role: 'user', content: text, timestamp: new Date().toISOString() })
        }

        isTyping.value = true
        error.value = null

        try {
            const payload = {
                content: text,
                system_only: systemOnly
            }
            const response = await ChatService.sendMessage(collection, slug, payload)

            if (response && response.content) {
                history.value.push(response)
            }
            return response
        } catch (e) {
            error.value = e.message || 'Failed to send message'
            console.error('Send error:', e)
        } finally {
            isTyping.value = false
        }
    }

    const generateDraft = async (collection, slug) => {
        isTyping.value = true
        error.value = null
        try {
            const response = await ChatService.generateDraft(collection, slug)
            // Draft response contains { content, status }
            // The /draft endpoint calls /message internally with response_system_only: true
            // so we should probably refresh history to see the hidden message if needed,
            // but usually the AI doesn't send a visible message during draft gen.
            return response
        } catch (e) {
            console.error('Draft gen error:', e)
            error.value = e.message
        } finally {
            isTyping.value = false
        }
    }

    const translateDraft = async (collection, slug, payload) => {
        isTyping.value = true
        error.value = null
        try {
            const response = await ChatService.translateDraft(collection, slug, payload)
            return response
        } catch (e) {
            console.error('Translate draft error:', e)
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
        loading,
        error,
        loadHistory,
        fetchHistory,
        initSession,
        sendMessage,
        generateDraft,
        translateDraft,
        resetState
    }
})

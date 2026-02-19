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
        if (messages && messages.length > 0) {
            history.value = messages
        } else {
            // Initialize with local welcome message if history is empty
            history.value = [{
                role: 'assistant',
                content: 'Hola, soy Tlacuilo. ¿En qué puedo ayudarte hoy a documentar?'
            }]
        }
    }

    const fetchHistory = async (collection, slug) => {
        loading.value = true
        error.value = null
        try {
            const data = await ChatService.getHistory(collection, slug)
            // Architecture says data should be { messages: [...] }
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

    const sendMessage = async (collection, slug, text) => {
        if (!text.trim()) return

        history.value.push({ role: 'user', content: text })
        isTyping.value = true
        error.value = null

        try {
            const response = await ChatService.sendMessage(collection, slug, text)

            // Per ARCHITECTURE.md, the response format might vary. 
            // If response is the full history: history.value = response
            // If response is just the new message: history.value.push(response)

            if (Array.isArray(response)) {
                history.value = response
            } else if (response && response.content) {
                history.value.push(response)
            } else {
                // Fallback: reload history via project if needed, 
                // but let's assume one of the above for now.
            }

        } catch (e) {
            error.value = e.message || 'Failed to send message'
            console.error('Send error:', e)
        } finally {
            isTyping.value = false
        }
    }

    const generateDraft = async (collection, slug) => {
        isTyping.value = true
        try {
            const response = await ChatService.generateDraft(collection, slug)
            // Draft response might contain a message or the updated project state
            if (response && response.message) {
                history.value.push({ role: 'assistant', content: response.message })
            }
            return response
        } catch (e) {
            console.error('Draft gen error:', e)
            error.value = e.message
        } finally {
            isTyping.value = false
        }
    }

    const refineTranslation = async (collection, slug, text) => {
        if (!text.trim()) return

        history.value.push({ role: 'user', content: text })
        isTyping.value = true

        try {
            const response = await ChatService.refineTranslation(collection, slug, text)
            if (Array.isArray(response)) {
                history.value = response
            } else if (response && response.content) {
                history.value.push(response)
            }
        } catch (e) {
            error.value = e.message
            console.error('Refine error:', e)
        } finally {
            isTyping.value = false
        }
    }

    const startTranslation = async (collection, slug) => {
        isTyping.value = true
        try {
            const response = await ChatService.translateProject(collection, slug)
            // Ideally response contains the first content
            if (response && response.message) {
                history.value.push({ role: 'assistant', content: response.message })
            }
            return response
        } catch (e) {
            console.error('Start translation error:', e)
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
        sendMessage,
        generateDraft,
        refineTranslation,
        startTranslation,
        resetState
    }
})

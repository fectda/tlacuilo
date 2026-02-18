import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useSystemStore = defineStore('system', () => {
    const vitals = ref({
        api: { status: 'POLLING', label: 'Backend API' },
        ollama: { status: 'POLLING', label: 'Ollama (LLM)' },
        comfyui: { status: 'POLLING', label: 'ComfyUI Bridge' }
    })
    const loading = ref(false)
    const error = ref(null)
    let pollingInterval = null

    const fetchVitals = async () => {
        try {
            const response = await api.get('/system/vitals')
            vitals.value = response.data
            error.value = null
        } catch (e) {
            vitals.value.api.status = 'OFFLINE'
            vitals.value.ollama.status = 'OFFLINE'
            vitals.value.comfyui.status = 'OFFLINE'
            error.value = 'API connection lost'
        }
    }

    const startPolling = (intervalMs = 30000) => {
        if (pollingInterval) return
        fetchVitals() // Initial fetch
        pollingInterval = setInterval(fetchVitals, intervalMs)
    }

    const stopPolling = () => {
        if (pollingInterval) {
            clearInterval(pollingInterval)
            pollingInterval = null
        }
    }

    return {
        vitals,
        loading,
        error,
        fetchVitals,
        startPolling,
        stopPolling
    }
})

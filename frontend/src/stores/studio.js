import { defineStore } from 'pinia'
import { ref } from 'vue'
import StudioService from '../services/StudioService'

export const useStudioStore = defineStore('studio', () => {
    const shots = ref([])
    const currentShot = ref(null)
    const isLoading = ref(false)
    const isSuggesting = ref(false)
    const isGenerating = ref(false)
    const error = ref(null)

    async function fetchShots(collection, slug) {
        isLoading.value = true
        error.value = null
        try {
            shots.value = await StudioService.listShots(collection, slug)
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
        } finally {
            isLoading.value = false
        }
    }

    async function suggestShots(collection, slug) {
        isSuggesting.value = true
        error.value = null
        try {
            const result = await StudioService.suggestShots(collection, slug)
            // Reload the full list after suggestion
            await fetchShots(collection, slug)
            return result
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        } finally {
            isSuggesting.value = false
        }
    }

    async function createShot(collection, slug, payload) {
        error.value = null
        try {
            const shot = await StudioService.createShot(collection, slug, payload)
            await fetchShots(collection, slug)
            return shot
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        }
    }

    async function deleteShot(collection, slug, shotId) {
        error.value = null
        try {
            await StudioService.deleteShot(collection, slug, shotId)
            shots.value = shots.value.filter(s => s.shot_id !== shotId)
            if (currentShot.value?.shot_id === shotId) {
                currentShot.value = null
            }
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        }
    }

    async function selectShot(collection, slug, shotId) {
        error.value = null
        try {
            currentShot.value = await StudioService.getShot(collection, slug, shotId)
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
        }
    }

    async function updateShot(collection, slug, shotId, payload) {
        error.value = null
        try {
            await StudioService.updateShot(collection, slug, shotId, payload)
            await selectShot(collection, slug, shotId)
            await fetchShots(collection, slug)
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        }
    }

    async function uploadAndGenerate(collection, slug, shotId, file) {
        isGenerating.value = true
        error.value = null
        try {
            const result = await StudioService.uploadAndGenerate(collection, slug, shotId, file)
            await selectShot(collection, slug, shotId)
            await fetchShots(collection, slug)
            return result
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        } finally {
            isGenerating.value = false
        }
    }

    async function correctShot(collection, slug, shotId, instruction) {
        isGenerating.value = true
        error.value = null
        try {
            const result = await StudioService.correctShot(collection, slug, shotId, instruction)
            await selectShot(collection, slug, shotId)
            await fetchShots(collection, slug)
            return result
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        } finally {
            isGenerating.value = false
        }
    }

    async function approveShot(collection, slug, shotId, filename) {
        error.value = null
        try {
            const result = await StudioService.approveShot(collection, slug, shotId, filename)
            await selectShot(collection, slug, shotId)
            await fetchShots(collection, slug)
            return result
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        }
    }

    function clearCurrentShot() {
        currentShot.value = null
    }

    return {
        shots,
        currentShot,
        isLoading,
        isSuggesting,
        isGenerating,
        error,
        fetchShots,
        suggestShots,
        createShot,
        deleteShot,
        selectShot,
        updateShot,
        uploadAndGenerate,
        correctShot,
        approveShot,
        clearCurrentShot,
    }
})

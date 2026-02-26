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

    async function updateShot(collection, slug, shot_id, payload) {
        error.value = null
        try {
            await StudioService.updateShot(collection, slug, shot_id, payload)
            // Update local state directly
            if (currentShot.value?.shot_id === shot_id) {
                Object.assign(currentShot.value, payload)
            }
            const shotInList = shots.value.find(s => s.shot_id === shot_id)
            if (shotInList) Object.assign(shotInList, payload)
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        }
    }

    async function uploadAndGenerate(collection, slug, shot_id, file) {
        isGenerating.value = true
        error.value = null
        try {
            const data = await StudioService.uploadAndGenerate(collection, slug, shot_id, file)
            if (currentShot.value?.shot_id === shot_id) {
                currentShot.value.images = data.images
                currentShot.value.status = 'queued'
                currentShot.value.has_original = true
            }
            const shotInList = shots.value.find(s => s.shot_id === shot_id)
            if (shotInList) {
                shotInList.status = 'queued'
                shotInList.has_original = true
            }
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        } finally {
            isGenerating.value = false
        }
    }

    async function pollShotStatus(collection, slug, shot_id) {
        try {
            const data = await StudioService.getShotStatus(collection, slug, shot_id)
            const images = data?.images || []
            
            if (currentShot.value?.shot_id === shot_id) {
                currentShot.value.images = images
                
                // Derive aggregate status locally
                let newStatus = 'pending_upload'
                if (images.some(i => i.status === 'approved')) newStatus = 'approved'
                else if (images.some(i => i.status === 'generated')) newStatus = 'generated'
                else if (images.some(i => i.status === 'queue')) newStatus = 'queued'
                
                currentShot.value.status = newStatus
                const shotInList = shots.value.find(s => s.shot_id === shot_id)
                if (shotInList) shotInList.status = newStatus
            }
            return images
        } catch (e) {
            console.error('Polling error:', e)
        }
    }

    async function correctShot(collection, slug, shot_id, instruction, comfly_id) {
        isGenerating.value = true
        error.value = null
        try {
            const data = await StudioService.correctShot(collection, slug, shot_id, instruction, comfly_id)
            if (currentShot.value?.shot_id === shot_id) {
                currentShot.value.images = data.images
                currentShot.value.status = 'queued'
            }
            const shotInList = shots.value.find(s => s.shot_id === shot_id)
            if (shotInList) shotInList.status = 'queued'
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        } finally {
            isGenerating.value = false
        }
    }

    async function approveShot(collection, slug, shot_id, comfly_id) {
        error.value = null
        try {
            const data = await StudioService.approveShot(collection, slug, shot_id, comfly_id)
            if (currentShot.value?.shot_id === shot_id) {
                currentShot.value.images = data.images
                currentShot.value.status = 'approved'
            }
            const shotInList = shots.value.find(s => s.shot_id === shot_id)
            if (shotInList) shotInList.status = 'approved'
            return data
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        }
    }

    async function deleteImage(collection, slug, shot_id, comfly_id) {
        error.value = null
        try {
            const data = await StudioService.deleteImage(collection, slug, shot_id, comfly_id)
            const newImages = data?.images || []
            
            if (currentShot.value?.shot_id === shot_id) {
                currentShot.value.images = newImages
                
                // Re-derive aggregate status locally
                let newStatus = 'pending_upload'
                if (newImages.some(i => i.status === 'approved')) newStatus = 'approved'
                else if (newImages.some(i => i.status === 'generated')) newStatus = 'generated'
                else if (newImages.some(i => i.status === 'queue')) newStatus = 'queued'
                
                currentShot.value.status = newStatus
                const shotInList = shots.value.find(s => s.shot_id === shot_id)
                if (shotInList) shotInList.status = newStatus
            }
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
        pollShotStatus,
        correctShot,
        approveShot,
        deleteImage,
        clearCurrentShot,
    }
})

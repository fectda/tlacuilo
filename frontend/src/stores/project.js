import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import ProjectService from '../services/ProjectService'

export const useProjectStore = defineStore('project', () => {
    const projects = ref({
        atoms: [],
        bits: [],
        mind: []
    })
    const currentProject = ref(null)
    const loading = ref(false)
    const error = ref(null)

    const currentTranslation = ref(null)

    // Actions
    const fetchProjects = async () => {
        loading.value = true
        error.value = null
        try {
            const data = await ProjectService.listProjects()
            projects.value = data
        } catch (e) {
            error.value = e.message || 'Failed to fetch projects'
            console.error('Fetch error:', e)
        } finally {
            loading.value = false
        }
    }

    const fetchProject = async (collection, slug) => {
        loading.value = true
        error.value = null
        currentTranslation.value = null // Reset translation logic on new project load
        try {
            const data = await ProjectService.getProject(collection, slug)
            currentProject.value = data
            // If the response includes history, we should probably update chat store too
            // or let the view handle it. For now, just store the project data.
            return data
        } catch (e) {
            error.value = e.message || 'Failed to fetch project'
            console.error('Fetch error:', e)
            throw e
        } finally {
            loading.value = false
        }
    }

    const fetchTranslation = async (collection, slug) => {
        try {
            const data = await ProjectService.getTranslation(collection, slug)
            currentTranslation.value = data
            return data
        } catch (e) {
            console.error('Fetch translation error:', e)
            // It's okay if it fails (not exists yet), we handle UI accordingly
            currentTranslation.value = null
        }
    }

    const fetchContent = async (collection, slug) => {
        // Architecture: GET /content returns content and status
        try {
            const data = await ProjectService.getProjectContent(collection, slug)
            if (currentProject.value) {
                currentProject.value = { ...currentProject.value, ...data }
            } else {
                // Determine minimal structure if project not loaded yet
                currentProject.value = { collection, slug, ...data }
            }
            return data
        } catch (e) {
            console.error('Fetch content error:', e)
            throw e
        }
    }

    const createProject = async (name, collection, slug) => {
        loading.value = true
        error.value = null
        try {
            const newProject = await ProjectService.createProject(name, collection, slug)
            await fetchProjects()
            return newProject
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        } finally {
            loading.value = false
        }
    }

    const updateContent = async (collection, slug, content, metadata = null) => {
        try {
            const result = await ProjectService.updateContent(collection, slug, content, metadata)
            // result might contain schema_check and spelling results
            if (currentProject.value && currentProject.value.slug === slug) {
                currentProject.value.content = content
                if (metadata) {
                    currentProject.value.metadata = { ...currentProject.value.metadata, ...metadata }
                }
                // Store validation results if any
                currentProject.value.validation = result.validation || null
            }
            return result
        } catch (e) {
            console.error('Update error:', e)
            throw e
        }
    }

    const updateTranslationContent = async (collection, slug, content) => {
        try {
            const result = await ProjectService.updateTranslation(collection, slug, content)
            if (currentTranslation.value) {
                currentTranslation.value.content = content
            } else {
                currentTranslation.value = { content }
            }
            return result
        } catch (e) {
            console.error('Update translation error:', e)
            throw e
        }
    }

    const forgetProject = async (collection, slug) => {
        try {
            await ProjectService.forgetProject(collection, slug)
            await fetchProjects()
        } catch (e) {
            console.error('Forget error:', e)
            throw e
        }
    }

    const resurrectProject = async (collection, slug) => {
        try {
            await ProjectService.resurrectProject(collection, slug)
            await fetchProjects()
        } catch (e) {
            console.error('Resurrect error:', e)
            throw e
        }
    }

    const revertProject = async (collection, slug) => {
        try {
            const result = await ProjectService.revertProject(collection, slug)
            await fetchContent(collection, slug) // Refresh content specifically as per architecture
            return result
        } catch (e) {
            console.error('Revert error:', e)
            throw e
        }
    }

    const persistDraft = async (collection, slug) => {
        try {
            const result = await ProjectService.persistDraft(collection, slug)
            await fetchProject(collection, slug) // Refresh data
            return result
        } catch (e) {
            console.error('Persist error:', e)
            throw e
        }
    }

    const publishProject = async (collection, slug) => {
        try {
            const result = await ProjectService.publishProject(collection, slug)
            await fetchProject(collection, slug) // Refresh data
            return result
        } catch (e) {
            console.error('Publish error:', e)
            throw e
        }
    }

    const publishTranslation = async (collection, slug) => {
        try {
            const result = await ProjectService.publishTranslation(collection, slug)
            // Maybe refresh translation status?
            return result
        } catch (e) {
            console.error('Publish translation error:', e)
            throw e
        }
    }

    // Getters
    const totalProjects = computed(() => {
        return (projects.value.atoms?.length || 0) +
            (projects.value.bits?.length || 0) +
            (projects.value.mind?.length || 0)
    })

    const isWorkingCopyActive = computed(() => {
        return currentProject.value?.is_working_copy_active || false
    })

    return {
        projects,
        currentProject,
        currentTranslation,
        loading,
        error,
        fetchProjects,
        fetchProject,
        fetchTranslation,
        createProject,
        updateContent,
        updateTranslationContent,
        forgetProject,
        resurrectProject,
        revertProject,
        persistDraft,
        publishProject,
        publishTranslation,
        totalProjects,
        isWorkingCopyActive,
        fetchContent
    }
})

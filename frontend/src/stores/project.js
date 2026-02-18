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

    const fetchProject = async (collection, id) => {
        loading.value = true
        error.value = null
        try {
            const data = await ProjectService.getProject(collection, id)
            currentProject.value = data
            return data
        } catch (e) {
            error.value = e.message || 'Failed to fetch project'
            console.error('Fetch error:', e)
            throw e
        } finally {
            loading.value = false
        }
    }

    const createProject = async (name, collection, slug) => {
        loading.value = true
        error.value = null
        try {
            const newProject = await ProjectService.createProject(name, collection, slug)
            // Ideally we'd just push to the list, but fetching ensures sync
            await fetchProjects()
            return newProject
        } catch (e) {
            error.value = e.response?.data?.detail || e.message
            throw e
        } finally {
            loading.value = false
        }
    }

    const updateContent = async (collection, id, content, metadata) => {
        try {
            const result = await ProjectService.updateContent(collection, id, content, metadata)
            if (currentProject.value && currentProject.value.id === id) {
                currentProject.value.content = content
                if (metadata) {
                    currentProject.value.metadata = { ...currentProject.value.metadata, ...metadata }
                }
            }
            return result
        } catch (e) {
            console.error('Update error:', e)
            throw e
        }
    }

    const forgetProject = async (collection, id) => {
        try {
            await ProjectService.forgetProject(collection, id)
        } catch (e) {
            console.error('Forget error:', e)
            throw e
        }
    }

    const resurrectProject = async (collection, id) => {
        try {
            await ProjectService.resurrectProject(collection, id)
        } catch (e) {
            console.error('Resurrect error:', e)
            throw e
        }
    }

    // Getters
    const totalProjects = computed(() => {
        return (projects.value.atoms?.length || 0) +
            (projects.value.bits?.length || 0) +
            (projects.value.mind?.length || 0)
    })

    return {
        projects,
        currentProject,
        loading,
        error,
        fetchProjects,
        fetchProject,
        createProject,
        updateContent,
        forgetProject,
        resurrectProject,
        totalProjects
    }
})

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
            error.value = e.response?.data?.detail || e.message || 'Failed to fetch projects'
            console.error('Fetch error:', e)
        } finally {
            loading.value = false
        }
    }

    const fetchProjectFromList = async (collection, slug) => {
        if (!projects.value.atoms.length && !projects.value.bits.length && !projects.value.mind.length) {
            await fetchProjects()
        }
        const list = projects.value[collection] || []
        const project = list.find(p => p.slug === slug)
        if (project) {
            currentProject.value = { ...currentProject.value, ...project }
        }
        return project
    }

    const fetchTranslation = async (collection, slug) => {
        try {
            const data = await ProjectService.getTranslation(collection, slug)
            currentTranslation.value = data
            return data
        } catch (e) {
            console.error('Fetch translation error:', e)
            currentTranslation.value = null
        }
    }

    const fetchContent = async (collection, slug) => {
        try {
            const data = await ProjectService.getProjectContent(collection, slug)
            if (currentProject.value) {
                currentProject.value = { ...currentProject.value, ...data }
            } else {
                currentProject.value = { collection, slug, ...data }
            }
            return data
        } catch (e) {
            console.error('Fetch content error:', e)
            error.value = e.response?.data?.detail || e.message
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

    const persistContent = async (collection, slug, content) => {
        try {
            const result = await ProjectService.persistContent(collection, slug, content)
            if (currentProject.value && currentProject.value.slug === slug) {
                currentProject.value.content = content
                currentProject.value.validation = result.validation || null
                currentProject.value.is_working_copy_active = true
            }
            return result
        } catch (e) {
            console.error('Persist content error:', e)
            error.value = e.response?.data?.detail || e.message
            throw e
        }
    }

    const persistTranslation = async (collection, slug, content) => {
        try {
            const result = await ProjectService.persistTranslation(collection, slug, content)
            if (currentTranslation.value) {
                currentTranslation.value.content = content
            } else {
                currentTranslation.value = { content }
            }
            return result
        } catch (e) {
            console.error('Persist translation error:', e)
            error.value = e.response?.data?.detail || e.message
            throw e
        }
    }

    const promoteProject = async (collection, slug) => {
        try {
            const result = await ProjectService.promoteProject(collection, slug)
            if (currentProject.value) {
                currentProject.value.is_working_copy_active = false
                currentProject.value.doc_status = 'promovido'
            }
            return result
        } catch (e) {
            console.error('Promote error:', e)
            error.value = e.response?.data?.detail || e.message
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
            await fetchContent(collection, slug)
            return result
        } catch (e) {
            console.error('Revert error:', e)
            error.value = e.response?.data?.detail || e.message
            throw e
        }
    }

    const publishTranslation = async (collection, slug) => {
        try {
            const result = await ProjectService.publishTranslation(collection, slug)
            if (currentProject.value) {
                currentProject.value.doc_status = 'publicado'
            }
            return result
        } catch (e) {
            console.error('Publish translation error:', e)
            error.value = e.response?.data?.detail || e.message
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
        fetchProjectFromList,
        fetchTranslation,
        fetchContent,
        createProject,
        persistContent,
        persistTranslation,
        promoteProject,
        forgetProject,
        resurrectProject,
        revertProject,
        publishTranslation,
        totalProjects,
        isWorkingCopyActive
    }
})

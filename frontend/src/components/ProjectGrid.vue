<script setup>
import { onMounted, ref, computed, reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/project'
import NewProjectModal from './NewProjectModal.vue'
import ProjectFilter from './ProjectFilter.vue'
import BaseIcon from './BaseIcon.vue'
import StatusBadge from './StatusBadge.vue'
import { UI_STRINGS } from '../constants/uiStrings'

const router = useRouter()
const store = useProjectStore()
const { projects: groupedProjects, loading, error } = storeToRefs(store)
const { fetchProjects } = store

const showNewProjectModal = ref(false)
const searchQuery = ref('')
const activeFilters = reactive({
    collections: [],
    statuses: []
})

const getSectionTitle = (key) => {
    return UI_STRINGS.filters.collections[key] || key
}

const handleFilterChange = (filters) => {
    activeFilters.collections = filters.collections
    activeFilters.statuses = filters.statuses
}

const filteredProjects = computed(() => {
    const query = searchQuery.value.toLowerCase()
    const filtered = {
        atoms: [],
        bits: [],
        mind: []
    }
    
    Object.keys(groupedProjects.value).forEach(key => {
        if (activeFilters.collections.length > 0 && !activeFilters.collections.includes(key)) {
            return
        }

        filtered[key] = groupedProjects.value[key].filter(project => {
            const matchesSearch = !query || 
                                project.name.toLowerCase().includes(query) || 
                                project.description.toLowerCase().includes(query) ||
                                project.id.toLowerCase().includes(query)
            
            const matchesStatus = activeFilters.statuses.length === 0 || 
                                 activeFilters.statuses.includes(project.doc_status)
            
            return matchesSearch && matchesStatus
        })
    })
    
    return filtered
})

const openProject = (id, type) => {
    router.push({ 
        name: 'ProjectDigital', 
        params: { 
            collection: type, 
            slug: id 
        } 
    })
}

const handleProjectCreated = () => {
    fetchProjects()
}

const handleForgetProject = async (collection, slug) => {
    if (confirm(UI_STRINGS.grid.confirm_forget)) {
        try {
            await store.forgetProject(collection, slug)
            fetchProjects()
        } catch (e) {
            console.error('Forget error:', e)
        }
    }
}

const handleResurrectProject = async (collection, slug) => {
    try {
        await store.resurrectProject(collection, slug)
        fetchProjects()
    } catch (e) {
        console.error('Resurrect error:', e)
    }
}

onMounted(() => {
    fetchProjects()
})
</script>

<template>
    <div class="space-y-16 relative">
        <!-- Action Bar -->
        <div class="flex flex-col md:flex-row justify-between items-center gap-4 mb-8">
            <div class="relative w-full md:w-96">
                <input v-model="searchQuery" type="text" :placeholder="UI_STRINGS.common.search" 
                       class="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all placeholder-neutral-600 font-sans">
                <BaseIcon name="search" className="w-4 h-4 text-neutral-500 absolute left-3.5 top-3" />
            </div>
            
            <button @click="showNewProjectModal = true" class="btn-primary flex items-center gap-2 whitespace-nowrap">
                <BaseIcon name="plus" className="w-5 h-5" />
                {{ UI_STRINGS.common.new_project }}
            </button>
        </div>

        <!-- Filter Bar -->
        <ProjectFilter @change="handleFilterChange" />

        <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-6">
            <div class="relative w-12 h-12">
                <div class="absolute inset-0 border-2 border-white/5 rounded-full"></div>
                <div class="absolute inset-0 border-2 border-accent border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-neutral-500 font-mono text-[10px] uppercase tracking-[0.3em]">{{ UI_STRINGS.grid.scanning }}</p>
        </div>
        
        <div v-else-if="error" class="glass-card p-10 border-error/20 text-center max-w-2xl mx-auto shadow-glow-error/10">
            <BaseIcon name="alert" className="w-12 h-12 text-error mx-auto mb-4" />
            <h3 class="font-black text-white uppercase tracking-widest mb-2">{{ UI_STRINGS.grid.failure }}</h3>
            <p class="text-sm text-neutral-500 mb-6 font-light leading-relaxed">{{ error }}</p>
            <button @click="fetchProjects" class="btn-secondary">{{ UI_STRINGS.grid.retry }}</button>
        </div>
        
        <div v-else class="space-y-20">
            <div v-for="(projects, type) in filteredProjects" :key="type" class="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-700">
                <div v-if="projects.length > 0 || (searchQuery === '' && type === 'atoms')" class="flex items-center gap-6">
                    <h2 class="text-xl font-black uppercase tracking-[0.2em] text-white flex items-center gap-3">
                        <span class="w-1.5 h-1.5 rounded-full bg-accent"></span>
                        {{ getSectionTitle(type) }}
                    </h2>
                    <div class="h-[1px] flex-grow bg-gradient-to-r from-white/5 to-transparent"></div>
                    <span class="font-mono text-[10px] text-neutral-600 font-bold tracking-widest">{{ projects ? projects.length : 0 }} {{ UI_STRINGS.grid.entities }}</span>
                </div>
                
                <div v-if="projects && projects.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <div v-for="project in projects" :key="project.id" 
                          class="glass-card p-6 group cursor-pointer transition-all duration-500 relative overflow-hidden flex flex-col"
                          :class="{ 'opacity-60 grayscale-[0.5] items-muted': project.draft }"
                          @click="openProject(project.id, type)">
                        
                        <!-- Top Bar (Alert/Status Right) -->
                        <div class="flex justify-end items-start mb-6 relative z-20">
                            <div class="z-20">
                                <StatusBadge 
                                    v-if="project.missing_files"
                                    status="ERROR" 
                                    :label="UI_STRINGS.grid.missing_files" 
                                    type="badge" 
                                />
                                <StatusBadge 
                                    v-else
                                    :status="project.published ? 'PUBLISHED' : 'DRAFT'" 
                                    :label="project.published ? UI_STRINGS.grid.published : UI_STRINGS.grid.draft" 
                                    type="badge" 
                                />
                            </div>
                        </div>

                        <div class="flex flex-col gap-1 pr-12 overflow-hidden w-full mb-2 relative z-10">
                            <h3 class="text-lg font-bold text-white group-hover:text-accent transition-colors leading-tight tracking-tight truncate">{{ project.name }}</h3>
                            <div class="flex items-center gap-3 mt-1">
                                <span v-if="!project.missing_files" class="text-[9px] font-bold uppercase tracking-wider transition-colors bg-white/5 px-1.5 py-0.5 rounded border border-white/5 text-accent/70">
                                    {{ project.doc_status }}
                                </span>
                                <span class="font-mono text-[10px] text-neutral-500 truncate">{{ project.id }}</span>
                            </div>
                        </div>
                        
                        <p class="text-neutral-500 text-sm line-clamp-2 min-h-[40px] relative z-10 font-light leading-relaxed mb-6">
                            {{ project.description }}
                        </p>

                        <!-- Actions Grid (Only for orphans) -->
                        <div v-if="project.missing_files" class="mt-auto grid grid-cols-2 gap-3 pt-6 relative z-20">
                            <button 
                                @click.stop="handleResurrectProject(type, project.id)"
                                class="btn-accent !px-2 !py-2 !text-[9px] flex items-center justify-center gap-1.5"
                            >
                                <BaseIcon name="plus" class="w-3 h-3" />
                                {{ UI_STRINGS.grid.resurrect_file }}
                            </button>
                            
                            <button 
                                @click.stop="handleForgetProject(type, project.id)"
                                class="btn-secondary !px-2 !py-2 !text-[9px] !text-error/60 hover:!text-error flex items-center justify-center gap-1.5"
                            >
                                <BaseIcon name="trash" class="w-3 h-3" />
                                {{ UI_STRINGS.grid.forget_memory }}
                            </button>
                        </div>
                    </div>
                </div>
                <div v-else-if="type !== 'atoms'" class="py-12 glass-card border-dashed border-white/5 bg-transparent flex flex-col items-center justify-center opacity-40">
                    <BaseIcon name="empty" class="w-8 h-8 mb-3 text-neutral-800" />
                    <span class="font-mono text-[9px] uppercase tracking-[0.3em] font-black">{{ UI_STRINGS.grid.no_cataloged.replace('{type}', type) }}</span>
                </div>
            </div>
        </div>

        <NewProjectModal v-if="showNewProjectModal" @close="showNewProjectModal = false" @created="handleProjectCreated" />
    </div>
</template>

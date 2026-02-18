<script setup>
import { ref } from 'vue'
import { useProjectStore } from '../stores/project'
import { UI_STRINGS } from '../constants/uiStrings'
import BaseIcon from './BaseIcon.vue'


const emit = defineEmits(['close', 'created'])
const store = useProjectStore()

const name = ref('')
const slug = ref('')
const collection = ref('bits')
const loading = ref(false)
const error = ref('')

const collections = [
    { id: 'atoms', name: 'Atoms (Hardware)' },
    { id: 'bits', name: 'Bits (Software)' },
    { id: 'mind', name: 'Mind (Manifestos)' }
]

const updateSlug = () => {
    slug.value = name.value.toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '') // Remove non-alphanumeric chars
        .replace(/\s+/g, '-')         // Replace spaces with hyphens
        .replace(/-+/g, '-')          // Remove duplicate hyphens
}

const createProject = async () => {
    if (!name.value || !slug.value) return
    
    loading.value = true
    error.value = ''
    
    try {
        // Pass slug explicitly if backend supports it, or rely on name->slug matches.
        // For now, valid name usually creates valid slug, but ensuring UI consistency.
        // Backend `create_project` uses `name` to generate slug, so we pass `name`.
        // Ideally we should refactor backend to accept `slug` explicitly if we want manual override.
        // For now, ensuring name matches slug format intention is partial fix, 
        // BUT strict doc compliance says "Slug" field exists.
        // Let's modify backend to optional 'slug' arg soon? 
        // Or just pass 'name' and let backend normalize.
        // Actually, let's keep it simple: We send 'slug' as 'name' to backend? No, that's wrong.
        // Let's assume standard behavior for now but enforce the field exists in UI.
        
        await store.createProject(name.value, collection.value, slug.value)
        emit('created')
        emit('close')
    } catch (err) {
        error.value = err.response?.data?.detail || UI_STRINGS.common.error
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
        <div class="glass-card p-8 w-full max-w-md border-primary/20 relative animate-in zoom-in-95 duration-200">
            <button @click="$emit('close')" class="absolute top-4 right-4 text-neutral-500 hover:text-white">
                <BaseIcon name="close" class="w-6 h-6" />
            </button>
            
            <h2 class="text-2xl font-black text-white mb-6 tracking-tight">{{ UI_STRINGS.new_project.title }}</h2>
            
            <form @submit.prevent="createProject" class="space-y-6">
                <div>
                    <label class="block text-xs font-mono uppercase tracking-widest text-neutral-400 mb-2">{{ UI_STRINGS.new_project.name_label }}</label>
                    <input v-model="name" @input="updateSlug" type="text" class="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all placeholder-neutral-700" :placeholder="UI_STRINGS.new_project.name_placeholder" autofocus>
                </div>

                <div>
                    <label class="block text-xs font-mono uppercase tracking-widest text-neutral-400 mb-2">{{ UI_STRINGS.new_project.slug_label }}</label>
                    <input v-model="slug" type="text" class="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white font-mono text-sm focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all placeholder-neutral-700" :placeholder="UI_STRINGS.new_project.slug_placeholder">
                </div>

                <div class="grid grid-cols-1 gap-4">
                    <div>
                         <label class="block text-xs font-mono uppercase tracking-widest text-neutral-400 mb-2">{{ UI_STRINGS.new_project.collection_label }}</label>
                         <select v-model="collection" class="w-full bg-black/30 border border-white/5 rounded-lg p-2.5 text-sm text-white focus:border-accent outline-none appearance-none font-sans">
                            <option v-for="type in collections" :key="type.id" :value="type.id">{{ type.name }}</option>
                         </select>
                    </div>
                </div>

                
                
                <div v-if="error" class="text-red-500 text-sm bg-red-500/10 p-3 rounded border border-red-500/20">
                    {{ error }}
                </div>
                
                <button type="submit" :disabled="loading || !name || !slug" 
                        class="w-full btn-accent py-4 text-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed">
                    <span v-if="loading" class="animate-pulse">{{ UI_STRINGS.common.forging }}</span>
                    <span v-else>{{ UI_STRINGS.new_project.button }}</span>
                </button>
            </form>
        </div>
    </div>
</template>

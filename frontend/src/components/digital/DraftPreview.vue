<script setup>
import { computed, ref, watch } from 'vue'
import { marked } from 'marked'
import { useProjectStore } from '../../stores/project'
import { useChatStore } from '../../stores/chat'

const props = defineProps(['collection', 'slug', 'content', 'isTranslation'])
const projectStore = useProjectStore()
const chatStore = useChatStore()
const isSaving = ref(false)
const isEditing = ref(false)
const localContent = ref(props.content || '')
const persistError = ref(null)

const isDirty = computed(() => {
    const savedContent = props.isTranslation 
        ? (projectStore.currentTranslation?.content || '')
        : (projectStore.currentProject?.content || '')
    return localContent.value !== savedContent
})

// Sync with props when not editing
watch(() => props.content, (newVal) => {
    if (!isEditing.value) {
        localContent.value = newVal || ''
    }
})

const parsedContent = computed(() => {
    const text = localContent.value || ''
    const match = text.match(/^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/)
    
    if (match) {
        const yamlRaw = match[1]
        const body = match[2]
        const metadata = {}
        
        yamlRaw.split('\n').forEach(line => {
            const [key, ...val] = line.split(':')
            if (key && val.length) {
                metadata[key.trim()] = val.join(':').trim()
            }
        })
        
        return { metadata, body }
    }
    
    return { metadata: null, body: text }
})

const renderMarkdown = (text) => {
    if (!text) return ''
    return marked(text)
}

const handleManualSave = async () => {
    isSaving.value = true
    try {
        if (props.isTranslation) {
             await projectStore.persistTranslation(props.collection, props.slug, localContent.value)
        } else {
             await projectStore.persistContent(props.collection, props.slug, localContent.value)
        }
        persistError.value = null
    } catch (e) {
        console.error(e)
        persistError.value = e.response?.data?.detail || e.message
    } finally {
        isSaving.value = false
    }
}

const handlePromote = async () => {
    try {
        if (confirm('¿Estás seguro de promover este borrador al Portafolio?')) {
            persistError.value = null
            await projectStore.promoteProject(props.collection, props.slug)
        }
    } catch (e) {
        console.error(e)
        persistError.value = e.response?.data?.detail || e.message
    }
}

const validation = computed(() => {
    if (props.isTranslation) return null
    return projectStore.currentProject?.validation || null
})

const isWorkingCopyActive = computed(() => {
    return projectStore.currentProject?.is_working_copy_active || false
})

const emit = defineEmits(['draft-generated', 'discard-draft', 'update:content'])

watch(localContent, (newVal) => {
    emit('update:content', newVal)
})

const handleDiscard = () => {
    if (confirm('¿Descartar los cambios actuales y volver a la versión guardada?')) {
        const savedContent = props.isTranslation 
            ? (projectStore.currentTranslation?.content || '')
            : (projectStore.currentProject?.content || '')
        localContent.value = savedContent
        isEditing.value = false
        emit('discard-draft')
    }
}

const handleGenerateDraft = async () => {
    chatStore.draftError = null
    isEditing.value = false
    
    if (props.isTranslation) {
        // Translation generation is still handled by TranslationStudio (Studio side)
        return
    }

    const response = await chatStore.generateDraft(props.collection, props.slug)
    if (response && response.content) {
        emit('draft-generated', response.content)
        localContent.value = response.content
    }
}
</script>

<template>
    <div class="flex flex-col h-full bg-[#0a0f14] text-gray-300 relative border-l-2 border-white/10">
        <!-- Overlays (Cover the ABSOLUTE entire pane) -->
        <div v-if="chatStore.isDrafting" class="absolute inset-0 z-[100] flex items-center justify-center bg-[#0a0f14]/80 backdrop-blur-md">
            <div class="flex flex-col items-center gap-6 border-2 border-accent/40 bg-black/80 p-12 shadow-[0_0_50px_rgba(212,68,47,0.2)] skew-x-[-3deg] relative overflow-hidden">
                <div class="absolute top-0 left-0 h-1 bg-accent animate-[loading_2s_infinite]"></div>
                <div class="flex items-center gap-4">
                    <div class="w-2 h-8 bg-accent animate-pulse"></div>
                    <div class="flex flex-col">
                        <span class="text-sm font-black tracking-[0.5em] text-accent uppercase">GENERATING DRAFT</span>
                        <span class="text-[9px] text-neutral-500 tracking-[0.2em] uppercase mt-1">Executing GEM Protocol // Session Active</span>
                    </div>
                </div>
                <div class="flex gap-2">
                    <div v-for="i in 3" :key="i" class="w-1.5 h-1.5 bg-accent/40 rounded-full animate-bounce" :style="{ animationDelay: (i*0.2) + 's' }"></div>
                </div>
            </div>
        </div>

            <div v-if="chatStore.draftError || persistError" class="absolute inset-0 z-[100] flex items-center justify-center bg-red-950/20 backdrop-blur-sm">
                <div class="max-w-md w-full mx-4 border-2 border-red-500/50 bg-black p-8 shadow-[0_0_30px_rgba(239,68,68,0.2)] skew-x-[-2deg]">
                    <div class="flex items-center gap-3 mb-4">
                        <div class="w-1.5 h-6 bg-red-500"></div>
                        <span class="text-xs font-black tracking-[0.3em] text-red-500 uppercase">
                            {{ chatStore.draftError ? (isTranslation ? 'LOCALIZATION_FAILURE' : 'GENERATION_FAILURE') : 'VALIDATION_ERROR' }}
                        </span>
                    </div>
                    <p class="text-sm text-neutral-400 font-mono mb-6 leading-relaxed whitespace-pre-wrap">
                        {{ chatStore.draftError || persistError }}
                    </p>
                    <div class="flex gap-3">
                        <button 
                            @click="chatStore.draftError ? handleGenerateDraft() : persistError = null"
                            class="text-[10px] flex-1 bg-red-500 text-white hover:bg-red-600 px-4 py-2 transition-all uppercase tracking-widest font-bold">
                            {{ chatStore.draftError ? 'REINTENTAR' : 'ENTENDIDO' }}
                        </button>
                        <button 
                            v-if="chatStore.draftError"
                            @click="chatStore.draftError = null"
                            class="text-[10px] flex-1 border border-white/20 text-white/50 hover:border-white/40 hover:text-white px-4 py-2 transition-all uppercase tracking-widest font-bold">
                            CERRAR
                        </button>
                    </div>
                </div>
            </div>

        <!-- Terminal Header -->
        <div class="flex items-center justify-between px-4 py-3 bg-[#05080a] border-b border-white/10 z-10 sticky top-0">
            <div class="flex items-center gap-2">
                <div class="flex gap-1.5">
                    <div class="w-2.5 h-2.5 rounded-full bg-red-500/50"></div>
                    <div class="w-2.5 h-2.5 rounded-full bg-yellow-500/50"></div>
                    <div class="w-2.5 h-2.5 rounded-full bg-green-500/50"></div>
                </div>
                <div class="ml-3 text-[10px] font-mono text-neutral-500 uppercase tracking-widest flex items-center gap-2">
                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                    <span>{{ isTranslation ? 'translation.md' : 'draft.md' }}</span>
                </div>
            </div>
            
            <div class="flex items-center gap-2">
                <!-- Actions -->
                <button 
                    v-if="!isEditing && !isTranslation"
                    @click="handleGenerateDraft"
                    :disabled="chatStore.isTyping || isEditing || chatStore.isDrafting"
                    class="text-[9px] border px-2 py-0.5 transition-all uppercase tracking-widest font-mono bg-white/5 border-white/10 hover:bg-accent hover:text-black hover:border-accent">
                    <span>[ GENERAR BORRADOR ]</span>
                </button>
                <button 
                    @click="isEditing = !isEditing"
                    :disabled="chatStore.isDrafting"
                    class="text-[9px] bg-white/5 border border-white/10 hover:bg-white/10 px-2 py-0.5 transition-all uppercase tracking-widest font-mono">
                    {{ isEditing ? '[ PREVISUALIZAR ]' : '[ EDITAR ]' }}
                </button>

                <template v-if="isDirty">
                    <button 
                        @click="handleDiscard"
                        class="text-[9px] bg-white/5 border border-red-500/20 hover:bg-red-500/10 text-red-400 px-2 py-0.5 transition-all uppercase tracking-widest font-mono">
                        [ DESCARTAR ]
                    </button>
                    <button 
                        @click="handleManualSave"
                        :disabled="isSaving"
                        class="text-[9px] bg-white/5 border border-green-500/20 hover:bg-green-500/10 text-green-400 px-2 py-0.5 transition-all uppercase tracking-widest font-mono">
                        <span>{{ isSaving ? 'GUARDANDO...' : 'GUARDAR' }}</span>
                    </button>
                </template>
            </div>
        </div>

        <!-- Terminal Body -->
        <div class="flex-1 flex flex-col overflow-hidden relative font-mono text-sm leading-relaxed">
             <!-- Wallpaper Watermark -->
             <div class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.02] z-0">
                 <svg class="w-64 h-64 text-white" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5zm0 9l2.5-1.25L12 8.5l-2.5 1.25L12 11zm0 2.5l-5-2.5-5 2.5L12 22l10-8.5-5-2.5-5 2.5z"/></svg>
             </div>

            <!-- Validation Status Bar (Cyberpunk style) -->
            <div v-if="validation" class="px-8 py-2 border-b border-white/5 bg-black/40 flex items-center justify-between z-10">
                <div class="flex items-center gap-4">
                    <span class="text-[9px] uppercase tracking-widest font-bold"
                          :class="validation.schema_check?.valid ? 'text-green-500' : 'text-red-500'">
                        {{ validation.schema_check?.valid ? '[ SCHEMA_OK ]' : '[ SCHEMA_ERROR ]' }}
                    </span>
                    <span v-if="!validation.schema_check?.valid" class="text-[9px] text-red-400 opacity-80 italic">
                        {{ validation.schema_check?.error }}
                    </span>
                </div>
                <div v-if="validation.spellcheck?.errors?.length" class="text-[9px] text-amber-500/80 font-bold uppercase tracking-widest">
                    {{ validation.spellcheck.errors.length }} SPELL_WARNINGS
                </div>
            </div>

            <!-- Editor Mode -->
            <textarea 
                v-if="isEditing"
                v-model="localContent"
                class="flex-1 bg-transparent p-8 text-green-400/90 focus:outline-none custom-scrollbar resize-none z-10 selection:bg-green-500 selection:text-black"
                spellcheck="true"
            ></textarea>

            <!-- Preview Mode -->
            <div 
                v-else
                class="flex-1 p-8 custom-scrollbar relative z-10"
                :class="(chatStore.isDrafting || chatStore.draftError) ? 'overflow-hidden' : 'overflow-y-auto'"
            >
                <div v-if="localContent" class="portfolio-preview max-w-none">
                    <!-- Simplified Metadata Header (KEY : VALUE) -->
                    <div v-if="parsedContent.metadata" class="mb-14 border-b-2 border-white/5 pb-8 font-mono">
                        <div class="space-y-2">
                            <div v-for="(val, key) in parsedContent.metadata" :key="key" class="flex items-start gap-4 group">
                                <span class="text-[9px] font-black uppercase tracking-[0.25em] text-neutral-500 w-32 shrink-0 pt-0.5">
                                    {{ key.replace(/_/g, ' ') }} :
                                </span>
                                <span class="text-[11px] font-bold tracking-widest text-white/90 uppercase flex-1">
                                    {{ val.toString().replace(/[\[\]"]/g, '') }}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Body Content -->
                    <div v-html="renderMarkdown(parsedContent.body)"></div>
                </div>

                <div v-else class="h-full flex flex-col items-center justify-center text-neutral-600">
                    <div class="border border-dashed border-neutral-800 p-8 rounded-lg flex flex-col items-center">
                         <span class="text-4xl opacity-20 mb-2">∅</span>
                        <span class="text-[10px] tracking-[0.2em] font-bold uppercase">NO DATA AVAILABLE</span>
                        <span class="text-[9px] mt-1">Generate a draft or enter edit mode</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Terminal Footer -->
        <div class="px-4 py-2 bg-[#05080a] border-t border-white/5 text-[9px] font-mono text-neutral-600 flex justify-between uppercase tracking-widest">
            <div class="flex items-center gap-4">
                <span>Ln 1, Col 1</span>
                <span>{{ isEditing ? 'MODE: INSERT' : 'MODE: VIEW' }}</span>
            </div>
            <div class="flex items-center gap-4">
                <span>{{ localContent.length }} Chars</span>
                <span>UTF-8</span>
                <span>Markdown</span>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Portfolio Preview Styles */
.portfolio-preview {
    font-family: 'Montserrat', system-ui, sans-serif;
    color: #D4D4D4;
    line-height: 1.8;
    counter-reset: h2-counter;
}

:deep(.portfolio-preview h1) {
    display: none; /* Page title handled by layout */
}

:deep(.portfolio-preview h2) {
    font-family: 'Space Grotesk', 'Courier New', monospace;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #FFFFFF;
    margin-top: 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    counter-increment: h2-counter;
}

:deep(.portfolio-preview h2::before) {
    content: counter(h2-counter, decimal-leading-zero) " / ";
    color: #25BCC0;
    font-size: 0.85em;
    font-weight: 300;
}

:deep(.portfolio-preview h3) {
    font-family: 'Space Grotesk', system-ui, sans-serif;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #FFFFFF;
    margin-top: 2rem;
    margin-bottom: 1rem;
    border: none;
    padding: 0;
    font-size: 1.1rem;
}

:deep(.portfolio-preview h4) {
    font-family: 'Space Grotesk', system-ui, sans-serif;
    font-weight: 700;
    color: #EEEEEE;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

:deep(.portfolio-preview p) {
    margin-bottom: 1.5rem;
    font-weight: 400;
}

:deep(.portfolio-preview strong) {
    color: #FFFFFF;
    font-weight: 700;
}

:deep(.portfolio-preview code) {
    font-family: 'Space Grotesk', ui-monospace, monospace;
    color: #25BCC0;
    background: rgba(37, 188, 192, 0.1);
    padding: 0.1em 0.3em;
    border-radius: 2px;
    font-size: 0.95em;
}

:deep(.portfolio-preview pre) {
    background: #000000;
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 1.5rem;
    margin: 2rem 0;
    overflow-x: auto;
    position: relative;
}

:deep(.portfolio-preview pre::before) {
    content: "CODE_BLOCK";
    position: absolute;
    top: 0;
    right: 0;
    font-size: 8px;
    color: rgba(255, 255, 255, 0.2);
    padding: 4px 8px;
    letter-spacing: 2px;
}

:deep(.portfolio-preview pre code) {
    background: transparent;
    padding: 0;
    color: #E2E8F0;
    font-size: 0.85rem;
}

:deep(.portfolio-preview a) {
    color: #25BCC0;
    text-decoration: none;
    border-bottom: 1px solid rgba(37, 188, 192, 0.3);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.portfolio-preview a:hover) {
    border-bottom-color: #25BCC0;
    background: rgba(37, 188, 192, 0.1);
}

:deep(.portfolio-preview hr) {
    border: none;
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 4rem 0;
}

:deep(.portfolio-preview hr::after) {
    content: "◆ ◆ ◆";
    color: #D4442F;
    font-size: 1.1rem;
    letter-spacing: 1.2rem;
    opacity: 0.8;
}

:deep(.portfolio-preview blockquote) {
    border-left: 4px solid #D4442F;
    background: rgba(212, 68, 47, 0.03);
    padding: 1.5rem 2rem;
    margin: 2.5rem 0;
    font-style: italic;
    color: #A3A3A3;
}

/* Alert Patterns */
:deep(.portfolio-preview blockquote p strong:first-child) {
    color: #D4442F;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-style: normal;
    margin-right: 0.5rem;
}

:deep(.portfolio-preview ul) {
    margin-bottom: 1.5rem;
    padding-left: 1.5rem;
    list-style: none;
}

:deep(.portfolio-preview ul li) {
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.75rem;
}

:deep(.portfolio-preview ul li::before) {
    content: "▪";
    position: absolute;
    left: 0;
    color: #25BCC0;
    font-size: 1rem;
    line-height: 1;
}

:deep(.portfolio-preview ol) {
    margin-bottom: 1.5rem;
    padding-left: 1.5rem;
    counter-reset: ol-counter;
}

:deep(.portfolio-preview ol li) {
    counter-increment: ol-counter;
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.75rem;
}

:deep(.portfolio-preview ol li::before) {
    content: counter(ol-counter) ".";
    position: absolute;
    left: 0;
    color: #25BCC0;
    font-weight: bold;
}

:deep(.portfolio-preview table) {
    width: 100%;
    border-collapse: collapse;
    margin: 3rem 0;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

:deep(.portfolio-preview th) {
    text-align: left;
    background: rgba(255, 255, 255, 0.02);
    border-bottom: 2px solid #25BCC0;
    padding: 1rem;
    color: #FFFFFF;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem;
}

:deep(.portfolio-preview td) {
    padding: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    font-size: 0.85rem;
}

@keyframes loading {
    0% { width: 0; left: 0; }
    50% { width: 100%; left: 0; }
    100% { width: 0; left: 100%; }
}
</style>

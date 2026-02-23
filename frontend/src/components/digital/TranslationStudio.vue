<script setup>
import { ref, computed } from 'vue'
import { useProjectStore } from '../../stores/project'
import { useChatStore } from '../../stores/chat'

const props = defineProps({
    collection: { type: String, required: true },
    slug: { type: String, required: true }
})

const projectStore = useProjectStore()
const chatStore = useChatStore()

const emit = defineEmits(['draft-generated'])
const fromScratch = ref(false)
const instruction = ref('')

const isGenerating = computed(() => chatStore.isDrafting)

const handleAction = async () => {
    if (isGenerating.value) return
    
    const response = await chatStore.translateDraft(props.collection, props.slug, {
        from_scratch: fromScratch.value,
        instruction: instruction.value,
        current_draft: projectStore.currentTranslation?.content || ''
    })
    
    if (response && response.content) {
        emit('draft-generated', response.content)
    }
    
    // Clear instruction after successful refinement (if user wants)
    if (!fromScratch.value) {
        instruction.value = ''
    }
}

const translationSource = computed(() => projectStore.currentTranslation?.source || 'empty')
const docStatus = computed(() => projectStore.currentProject?.doc_status || 'borrador')

</script>

<template>
    <div class="flex flex-col h-full bg-[#050505] text-blue-100/80 font-mono text-xs overflow-hidden border-r border-white/5 shadow-2xl">
        <!-- Header -->
        <div class="p-6 border-b border-white/10 bg-blue-900/10">
            <div class="flex items-center gap-3 mb-2">
                <div class="w-1.5 h-4 bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div>
                <h2 class="text-[11px] font-black tracking-[0.3em] uppercase text-blue-400">English Translation Studio</h2>
            </div>
            <p class="text-[9px] text-neutral-500 uppercase tracking-widest">Protocol: Section D.264 / Bilingual Scribe</p>
        </div>

        <div class="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">

            <!-- Configuration -->
            <div class="space-y-6 bg-white/5 p-6 border border-white/10 rounded-sm">
                <!-- From Scratch Switch -->
                <div class="flex items-center justify-between group cursor-pointer" @click="fromScratch = !fromScratch">
                    <div class="flex flex-col gap-1">
                        <span class="text-[10px] font-bold tracking-widest uppercase text-white group-hover:text-blue-400 transition-colors">Translate From Scratch</span>
                        <span class="text-[9px] text-neutral-500 font-normal">Ignore existing draft and re-translate source content.</span>
                    </div>
                    <div :class="['w-10 h-5 border transition-all relative flex items-center px-1', fromScratch ? 'border-blue-500 bg-blue-500/20' : 'border-neutral-700 bg-black']">
                        <div :class="['w-3 h-3 transition-all', fromScratch ? 'translate-x-5 bg-blue-400 shadow-glow-blue' : 'bg-neutral-700']"></div>
                    </div>
                </div>

                <div class="h-px bg-white/5"></div>

                <!-- Instruction Input -->
                <div class="space-y-3">
                    <label class="text-[10px] font-bold tracking-widest uppercase text-white flex items-center justify-between">
                        <span>Refinement Instructions</span>
                        <span v-if="fromScratch" class="text-[8px] text-red-500/50">[ IGNORED IN FROM SCRATCH MODE ]</span>
                    </label>
                    <textarea 
                        v-model="instruction"
                        :disabled="fromScratch || isGenerating"
                        placeholder="e.g., 'Make it more professional', 'Focus on technical accuracy', 'Fix tone issues'..."
                        class="w-full h-32 bg-black border border-white/10 p-4 text-xs text-blue-200/80 focus:outline-none focus:border-blue-500/50 resize-none font-mono selection:bg-blue-500 selection:text-white disabled:opacity-30 transition-all"
                    ></textarea>
                </div>
            </div>

            <!-- Generate Button -->
            <button 
                @click="handleAction"
                :disabled="isGenerating || (fromScratch === false && !instruction.trim() && translationSource === 'empty')"
                class="w-full py-4 bg-blue-600 text-white font-bold tracking-[0.4em] uppercase text-[10px] hover:bg-blue-500 transition-all shadow-[0_0_20px_rgba(37,99,235,0.2)] disabled:opacity-30 disabled:cursor-not-allowed group relative overflow-hidden"
            >
                <div v-if="isGenerating" class="absolute inset-0 bg-blue-700 flex items-center justify-center">
                    <span class="animate-pulse">PROCESSING...</span>
                </div>
                <span v-else>{{ fromScratch ? 'Generate Full Translation' : 'Refine Current Draft' }}</span>
            </button>

            <!-- Usage Note -->
            <div class="p-4 border border-blue-500/10 bg-blue-500/5">
                <p class="text-[9px] text-blue-300/60 leading-relaxed uppercase tracking-wider">
                    The <span class="text-blue-400 font-bold underline">Bilingual Scribe</span> will analyze your Spanish source and instructions to produce a technical translation that complies with the portfolio schema.
                </p>
            </div>
        </div>
    </div>
</template>

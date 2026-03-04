<script setup>
import { ref, onMounted } from 'vue'
import { UI_TEXTS } from '../../constants/uiTexts'

const texts = UI_TEXTS.REFINEMENT_MODAL
const commonTexts = UI_TEXTS.COMMON

const props = defineProps({
    isOpen: Boolean,
    title: { type: String, default: 'INSTRUCCIONES DE REFINAMIENTO' },
    placeholder: { type: String, default: 'Describe qué ajustes necesitas en la traducción...' }
})

const emit = defineEmits(['close', 'confirm'])
const instruction = ref('')
const textareaRef = ref(null)

onMounted(() => {
    if (textareaRef.value) textareaRef.value.focus()
})

const handleConfirm = () => {
    emit('confirm', instruction.value)
    instruction.value = ''
}

const handleCancel = () => {
    emit('close')
    instruction.value = ''
}
</script>

<template>
    <div v-if="isOpen" class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
        <div class="w-full max-w-lg bg-[#050505] border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)] flex flex-col">
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-white/5">
                <div class="flex items-center gap-3">
                    <div class="w-1.5 h-4 bg-blue-500"></div>
                    <span class="text-[10px] font-black tracking-[0.3em] uppercase">{{ title }}</span>
                </div>
                <button @click="handleCancel" class="text-neutral-500 hover:text-white transition-colors">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
            </div>

            <!-- Body -->
            <div class="p-6">
                <p class="text-[11px] text-neutral-400 font-mono mb-4 leading-relaxed">
                    {{ texts.HELP_TEXT.split('Bilingual Scribe')[0] }}<span class="text-blue-400">Bilingual Scribe</span>{{ texts.HELP_TEXT.split('Bilingual Scribe')[1] }}
                </p>
                <textarea 
                    ref="textareaRef"
                    v-model="instruction"
                    @keydown.meta.enter="handleConfirm"
                    @keydown.ctrl.enter="handleConfirm"
                    :placeholder="placeholder"
                    class="w-full h-32 bg-black border border-white/10 p-4 text-sm text-blue-200/80 focus:outline-none focus:border-blue-500/50 resize-none font-mono selection:bg-blue-500 selection:text-white"
                ></textarea>
                <div class="mt-2 text-[9px] text-neutral-600 uppercase tracking-widest text-right">
                    {{ texts.SUBMIT_HINT }}
                </div>
            </div>

            <!-- Footer -->
            <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-white/5 bg-white/5">
                <button 
                    @click="handleCancel"
                    class="px-4 py-2 text-[10px] uppercase font-bold tracking-widest text-neutral-500 hover:text-white transition-colors">
                    {{ commonTexts.CANCEL }}
                </button>
                <button 
                    @click="handleConfirm"
                    class="px-6 py-2 text-[10px] uppercase font-bold tracking-widest bg-blue-600 text-white hover:bg-blue-500 transition-all shadow-[0_0_15px_rgba(37,99,235,0.2)]">
                    {{ texts.BTN_REFINE }}
                </button>
            </div>
        </div>
    </div>
</template>

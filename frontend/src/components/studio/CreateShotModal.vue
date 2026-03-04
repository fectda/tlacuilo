<script setup>
import { ref, computed, defineEmits } from 'vue'
import { SHOT_TYPES, ATMOSPHERES } from '../../constants/studio'
import { UI_TEXTS } from '../../constants/uiTexts'

const texts = UI_TEXTS.CREATE_SHOT_MODAL
const commonTexts = UI_TEXTS.COMMON

const emit = defineEmits(['close', 'submit'])

const types = SHOT_TYPES
const atmospheres = ATMOSPHERES

const title = ref('')
const description = ref('')
const type = ref('macro')
const focus = ref('')
const atmosphere = ref('turquesa')

const isValid = computed(() => title.value.trim() && atmosphere.value && focus.value.trim() && description.value.trim())

const handleSubmit = () => {
    if (!isValid.value) return
    emit('submit', {
        title: title.value.trim(),
        description: description.value.trim(),
        type: type.value,
        focus: focus.value.trim(),
        atmosphere: atmosphere.value,
    })
}
</script>

<template>
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm" @click.self="emit('close')">
        <div class="w-full max-w-lg bg-[#050505] border border-white/10 font-mono">
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-white/10">
                <div class="flex items-center gap-3">
                    <div class="w-1.5 h-4 bg-cyan-500"></div>
                    <h2 class="text-[11px] font-black tracking-[0.3em] uppercase text-cyan-400">{{ texts.TITLE }}</h2>
                </div>
                <button @click="emit('close')" class="text-neutral-600 hover:text-white text-sm transition-colors">✕</button>
            </div>

            <!-- Form -->
            <div class="p-6 space-y-5">
                <!-- Title -->
                <div class="space-y-1.5">
                    <label class="text-[9px] uppercase tracking-widest text-neutral-500 font-bold">{{ texts.LABEL_TITLE }} <span class="text-red-500">*</span></label>
                    <input
                        v-model="title"
                        :placeholder="texts.PLACEHOLDER_TITLE"
                        class="w-full bg-black border border-white/10 px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500/50 font-mono"
                    />
                </div>

                <!-- Focus / Protagonist -->
                <div class="space-y-1.5">
                    <label class="text-[9px] uppercase tracking-widest text-neutral-500 font-bold">{{ texts.LABEL_PROTAGONIST }} <span class="text-red-500">*</span></label>
                    <input
                        v-model="focus"
                        :placeholder="texts.PLACEHOLDER_PROTAGONIST"
                        class="w-full bg-black border border-white/10 px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500/50 font-mono"
                    />
                    <p class="text-[8px] text-neutral-700">{{ texts.PROTAGONIST_HELP }}</p>
                </div>

                <!-- Description -->
                <div class="space-y-1.5">
                    <label class="text-[9px] uppercase tracking-widest text-neutral-500 font-bold">{{ texts.LABEL_DESCRIPTION }} <span class="text-red-500">*</span></label>
                    <textarea
                        v-model="description"
                        rows="2"
                        :placeholder="texts.PLACEHOLDER_DESCRIPTION"
                        class="w-full bg-black border border-white/10 px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500/50 font-mono resize-none"
                    ></textarea>
                </div>

                <!-- Type -->                
                <div class="space-y-2">
                    <label class="text-[9px] uppercase tracking-widest text-neutral-500 font-bold">{{ texts.LABEL_TYPE }}</label>
                    <div class="space-y-1">
                        <button
                            v-for="t in types" :key="t.value"
                            @click="type = t.value"
                            type="button"
                            :class="[
                                'w-full text-left px-3 py-2.5 border transition-all flex gap-3 items-start',
                                type === t.value
                                    ? 'border-white/40 bg-white/5'
                                    : 'border-white/8 hover:border-white/15 border-[rgba(255,255,255,0.06)]'
                            ]"
                        >
                            <span class="text-neutral-400 text-[13px] shrink-0 leading-none mt-0.5">{{ t.icon }}</span>
                            <div class="min-w-0">
                                <p class="text-[10px] font-black uppercase tracking-wider text-white">{{ t.label }}</p>
                                <p class="text-[8px] text-neutral-500 leading-relaxed mt-0.5">{{ t.desc }}</p>
                            </div>
                            <div class="ml-auto shrink-0 mt-1 w-2 h-2 rounded-full border transition-colors"
                                :class="type === t.value ? 'bg-white border-white' : 'border-neutral-700'"
                            ></div>
                        </button>
                    </div>
                </div>

                <!-- Atmosphere -->
                <div class="space-y-2">
                    <label class="text-[9px] uppercase tracking-widest text-neutral-500 font-bold">{{ texts.LABEL_ATMOSPHERE }} <span class="text-red-500">*</span></label>
                    <div class="space-y-1">
                        <button
                            v-for="a in atmospheres" :key="a.value"
                            @click="atmosphere = a.value"
                            type="button"
                            :class="[
                                'w-full text-left px-3 py-2.5 border transition-all flex gap-3 items-start',
                                atmosphere === a.value
                                    ? 'border-white/40 bg-white/5'
                                    : 'border-[rgba(255,255,255,0.06)] hover:border-white/15'
                            ]"
                        >
                            <div class="w-2 h-2 rounded-full shrink-0 mt-1" :style="{ background: a.dot, boxShadow: `0 0 6px ${a.dot}` }"></div>
                            <div class="min-w-0">
                                <p class="text-[10px] font-black uppercase tracking-wider" :style="{ color: atmosphere === a.value ? a.dot : 'white' }">{{ a.label }}</p>
                                <p class="text-[8px] text-neutral-500 leading-relaxed mt-0.5">{{ a.desc }}</p>
                            </div>
                            <div class="ml-auto shrink-0 mt-1 w-2 h-2 rounded-full border transition-colors"
                                :class="atmosphere === a.value ? 'bg-white border-white' : 'border-neutral-700'"
                            ></div>
                        </button>
                    </div>
                </div>

            </div><!-- /form -->

            <div class="px-6 pb-5 flex gap-3 justify-end">
                <button @click="emit('close')" class="text-[10px] border border-white/10 text-neutral-500 hover:text-white px-4 py-2 transition-all uppercase tracking-widest">
                    {{ commonTexts.CANCEL }}
                </button>
                <button
                    @click="handleSubmit"
                    :disabled="!isValid"
                    class="text-[10px] bg-white text-black hover:bg-neutral-200 px-4 py-2 transition-all uppercase tracking-widest font-black disabled:opacity-30 disabled:cursor-not-allowed"
                >
                    {{ texts.BTN_CREATE }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useStudioStore } from '../../stores/studio'
import StudioService from '../../services/StudioService'
import { SHOT_TYPES, ATMOSPHERES, ATMOSPHERE_STYLES } from '../../constants/studio'
import { UI_TEXTS } from '../../constants/uiTexts'

const texts = UI_TEXTS.SHOT_DETAIL
const commonTexts = UI_TEXTS.COMMON

const props = defineProps({
    collection: { type: String, required: true },
    slug: { type: String, required: true },
})

const emit = defineEmits(['delete-shot'])

const studioStore = useStudioStore()
const shot = computed(() => studioStore.currentShot)

const types = SHOT_TYPES
const atmospheres = ATMOSPHERES

const fileInput = ref(null)
const correctionText = ref('')
const isEditingMeta = ref(false)
const metaEdit = ref({})
const selectedComflyId = ref(null)
const pollingInterval = ref(null)
const cacheBuster = ref(Date.now())

// --- Polling logic ---
const startPolling = () => {
    if (pollingInterval.value) return
    console.log('Starting polling for shot:', shot.value?.shot_id)
    pollingInterval.value = setInterval(async () => {
        if (!shot.value) {
            stopPolling()
            return
        }
        const images = await studioStore.pollShotStatus(props.collection, props.slug, shot.value.shot_id)
        const stillQueued = (images || []).some(img => img.status === 'queue')
        if (!stillQueued) {
            console.log('All images processed, stopping polling.')
            cacheBuster.value = Date.now() // Refresh images once finished
            stopPolling()
        }
    }, 3000)
}

const stopPolling = () => {
    if (pollingInterval.value) {
        clearInterval(pollingInterval.value)
        pollingInterval.value = null
    }
}

// Watch for any image in queue to start/stop polling
watch(() => shot.value?.images, (images) => {
    const hasQueuedImages = (images || []).some(img => img.status === 'queue')
    if (hasQueuedImages) {
        startPolling()
    } else {
        if (pollingInterval.value) cacheBuster.value = Date.now()
        stopPolling()
    }
}, { immediate: true, deep: true })

// Watch images to keep selection in sync but NOT force edit mode on every update
watch(() => shot.value?.images, (images) => {
    if (!images || !images.length) {
        selectedComflyId.value = null
        return
    }
    
    // If we have an approved one, ensure it's selected (priority)
    const approvedImg = images.find(img => img.status === 'approved')
    if (approvedImg && selectedComflyId.value !== approvedImg.id) {
        selectedComflyId.value = approvedImg.id
        return
    }

    // If current selection is no longer in the list, clear it
    if (selectedComflyId.value && !images.find(img => img.id === selectedComflyId.value)) {
        selectedComflyId.value = null
    }
}, { immediate: true })

// --- BUGFIX: Reset edit mode when shot selection changes ---
watch(() => studioStore.currentShot?.shot_id, () => {
    isEditingMeta.value = false
    correctionText.value = ''
    selectedComflyId.value = null
    stopPolling()
})

// Accent color for atmosphere
const accent = computed(() => ATMOSPHERE_STYLES[shot.value?.atmosphere]?.accent || '#6b7280')

// Image URL helper with cache buster
const getImageUrl = (id) => {
    const baseUrl = StudioService.getShotImageUrl(props.collection, props.slug, shot.value.shot_id, id)
    return `${baseUrl}?t=${cacheBuster.value}`
}

// Original image URL
const originalUrl = computed(() =>
    shot.value?.has_original
        ? StudioService.getOriginalImageUrl(props.collection, props.slug, shot.value.shot_id)
        : null
)

// Status
const statusLabel = texts.STATUS

// Edit metadata
const startEdit = () => {
    metaEdit.value = {
        title: shot.value.title,
        description: shot.value.description,
        type: shot.value.type,
        focus: shot.value.focus,
        atmosphere: shot.value.atmosphere,
    }
    isEditingMeta.value = true
}
const cancelEdit = () => { isEditingMeta.value = false }
const saveEdit = async () => {
    await studioStore.updateShot(props.collection, props.slug, shot.value.shot_id, metaEdit.value)
    isEditingMeta.value = false
}

// Upload
const triggerUpload = () => fileInput.value?.click()
const handleFileSelected = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    await studioStore.uploadAndGenerate(props.collection, props.slug, shot.value.shot_id, file)
    e.target.value = ''
}

// Correct
const handleCorrect = async () => {
    if (!correctionText.value.trim() || !selectedComflyId.value) return
    await studioStore.correctShot(props.collection, props.slug, shot.value.shot_id, correctionText.value.trim(), selectedComflyId.value)
    correctionText.value = ''
}

// Approve
const handleApprove = async () => {
    if (!selectedComflyId.value) return
    await studioStore.approveShot(props.collection, props.slug, shot.value.shot_id, selectedComflyId.value)
}

// Delete Variant
const handleDeleteVariant = async (comflyId) => {
    if (confirm(texts.CONFIRM_DELETE_VARIANT)) {
        await studioStore.deleteImage(props.collection, props.slug, shot.value.shot_id, comflyId)
        if (selectedComflyId.value === comflyId) selectedComflyId.value = null
    }
}
</script>

<template>
    <div class="flex flex-col h-full bg-[#050505] font-mono text-xs overflow-hidden">

        <!-- Empty state -->
        <div v-if="!shot" class="flex-1 flex flex-col items-center justify-center gap-3">
            <div class="text-5xl opacity-10 select-none">⌀</div>
            <p class="text-[10px] uppercase tracking-[0.3em] text-neutral-600">{{ texts.EMPTY_STATE }}</p>
        </div>

        <template v-else>
            <!-- Header -->
            <div class="px-6 py-4 border-b border-white/10 bg-[#080808] shrink-0">
                <div class="flex items-center gap-3 mb-1.5">
                    <div class="w-1 h-5 shrink-0" :style="{ background: accent }"></div>
                    <h2 class="text-[13px] font-black tracking-widest uppercase text-white flex-1">{{ shot.title }}</h2>
                    
                    <!-- Manual Polling Trigger -->
                    <button
                        v-if="shot.images?.some(img => img.status === 'queue') && !pollingInterval"
                        @click="startPolling"
                        class="px-2 py-1 bg-amber-500/10 border border-amber-500/40 text-amber-500 text-[9px] font-black uppercase tracking-widest hover:bg-amber-500 hover:text-black transition-all"
                    >
                        ↻ {{ texts.RESUME_POLLING }}
                    </button>

                    <button
                        @click="emit('delete-shot', shot.shot_id)"
                        title="Eliminar shot"
                        class="text-neutral-600 hover:text-red-400 text-[11px] font-bold uppercase tracking-widest border border-neutral-800 hover:border-red-500/40 px-2 py-1 transition-all"
                    >✕ DEL</button>
                </div>
                <div class="flex items-center gap-3 pl-4">
                    <span class="text-[9px] text-neutral-400 uppercase tracking-wider">{{ shot.type }}</span>
                    <span class="text-[9px] font-bold uppercase" :style="{ color: accent }">{{ shot.atmosphere }}</span>
                    <span class="ml-auto text-[9px] uppercase tracking-widest font-bold" :style="{ color: accent }">
                        {{ statusLabel[shot.status] || shot.status }}
                    </span>
                </div>
            </div>

            <!-- Scrollable body -->
            <div class="flex-1 overflow-y-auto custom-scrollbar">
                <div class="p-6 space-y-7">

                    <!-- ── Metadata ───────────────────────────────────── -->
                    <section class="space-y-3">
                        <div class="flex items-center justify-between">
                            <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">{{ texts.SECTION_METADATA }}</p>
                            <button
                                v-if="!isEditingMeta"
                                @click="startEdit"
                                class="text-[9px] font-black uppercase tracking-widest px-3 py-1 border border-white/20 text-white hover:bg-white hover:text-black transition-all"
                            >
                                {{ texts.BTN_EDIT }}
                            </button>
                        </div>

                        <!-- Display -->
                        <div v-show="!isEditingMeta" class="border border-white/10 divide-y divide-white/5">
                            <div class="p-3 space-y-0.5">
                                <p class="text-[8px] text-neutral-500 uppercase tracking-wider">{{ texts.LABEL_TITLE }}</p>
                                <p class="text-[11px] text-white leading-relaxed font-bold">{{ shot.title || '—' }}</p>
                            </div>
                            <div class="grid grid-cols-2 divide-x divide-white/5">
                                <div class="p-3 space-y-0.5">
                                    <p class="text-[8px] text-neutral-500 uppercase tracking-wider">{{ texts.LABEL_TYPE }}</p>
                                    <p class="text-[10px] text-neutral-200 uppercase tracking-widest">{{ shot.type || '—' }}</p>
                                </div>
                                <div class="p-3 space-y-0.5">
                                    <p class="text-[8px] text-neutral-500 uppercase tracking-wider">{{ texts.LABEL_ATMOSPHERE }}</p>
                                    <div class="flex items-center gap-2">
                                        <div class="w-1.5 h-1.5 rounded-full" :style="{ background: accent }"></div>
                                        <p class="text-[10px] font-bold uppercase" :style="{ color: accent }">{{ shot.atmosphere || '—' }}</p>
                                    </div>
                                </div>
                            </div>
                            <div class="p-3 space-y-0.5">
                                <p class="text-[8px] text-neutral-500 uppercase tracking-wider">{{ texts.LABEL_DESCRIPTION }}</p>
                                <p class="text-[11px] text-neutral-200 leading-relaxed">{{ shot.description || '—' }}</p>
                            </div>
                            <div class="p-3 space-y-0.5">
                                <p class="text-[8px] text-neutral-500 uppercase tracking-wider">{{ texts.LABEL_PROTAGONIST }}</p>
                                <p class="text-[11px] text-neutral-200 leading-relaxed">{{ shot.focus || '—' }}</p>
                            </div>
                        </div>

                        <!-- Edit form -->
                        <div v-show="isEditingMeta" class="border border-white/20 divide-y divide-white/10">
                            <div class="p-3 space-y-1">
                                <p class="text-[8px] text-neutral-400 uppercase tracking-wider">{{ texts.LABEL_TITLE }}</p>
                                <input v-model="metaEdit.title"
                                    name="shot_title_edit"
                                    autocomplete="off"
                                    class="w-full bg-transparent text-[11px] text-white focus:outline-none border-b border-white/20 focus:border-white pb-1" />
                            </div>
                            <div class="p-3 space-y-1">
                                <p class="text-[8px] text-neutral-400 uppercase tracking-wider">{{ texts.LABEL_DESCRIPTION }}</p>
                                <textarea v-model="metaEdit.description" rows="2"
                                    name="shot_desc_edit"
                                    autocomplete="off"
                                    spellcheck="false"
                                    class="w-full bg-transparent text-[11px] text-white focus:outline-none resize-none border-b border-white/20 focus:border-white pb-1"></textarea>
                            </div>
                            <div class="p-3 space-y-1">
                                <p class="text-[8px] text-neutral-400 uppercase tracking-wider">{{ texts.LABEL_PROTAGONIST }}</p>
                                <input v-model="metaEdit.focus"
                                    name="shot_focus_edit"
                                    autocomplete="off"
                                    class="w-full bg-transparent text-[11px] text-white focus:outline-none border-b border-white/20 focus:border-white pb-1" />
                            </div>
                            <div class="p-3 bg-black/10">
                                <div class="grid grid-cols-2 gap-4">
                                    <div class="space-y-2">
                                        <p class="text-[8px] text-neutral-400 uppercase tracking-wider">{{ texts.LABEL_TYPE }}</p>
                                        <div class="space-y-1">
                                            <button
                                                v-for="t in types" :key="t.value"
                                                @click="metaEdit.type = t.value"
                                                type="button"
                                                :class="[
                                                    'w-full text-left px-2 py-2 border transition-all flex gap-2 items-start',
                                                    metaEdit.type === t.value
                                                        ? 'border-white/40 bg-white/5'
                                                        : 'border-white/8 hover:border-white/15 border-[rgba(255,255,255,0.06)]'
                                                ]"
                                            >
                                                <span class="text-neutral-400 text-[11px] shrink-0 leading-none mt-0.5">{{ t.icon }}</span>
                                                <div class="min-w-0">
                                                    <p class="text-[9px] font-black uppercase tracking-wider text-white leading-tight">{{ t.label }}</p>
                                                    <p class="text-[7px] text-neutral-500 leading-tight mt-0.5 line-clamp-2">{{ t.desc }}</p>
                                                </div>
                                                <div class="ml-auto shrink-0 mt-1 w-1.5 h-1.5 rounded-full border transition-colors"
                                                    :class="metaEdit.type === t.value ? 'bg-white border-white' : 'border-neutral-700'"
                                                ></div>
                                            </button>
                                        </div>
                                    </div>

                                    <div class="space-y-2">
                                        <p class="text-[8px] text-neutral-400 uppercase tracking-wider">{{ texts.LABEL_ATMOSPHERE }}</p>
                                        <div class="space-y-1">
                                            <button
                                                v-for="a in atmospheres" :key="a.value"
                                                @click="metaEdit.atmosphere = a.value"
                                                type="button"
                                                :class="[
                                                    'w-full text-left px-2 py-2 border transition-all flex gap-2 items-start',
                                                    metaEdit.atmosphere === a.value
                                                        ? 'border-white/40 bg-white/5'
                                                        : 'border-[rgba(255,255,255,0.06)] hover:border-white/15'
                                                ]"
                                            >
                                                <div class="w-1.5 h-1.5 rounded-full shrink-0 mt-1" :style="{ background: a.dot, boxShadow: `0 0 4px ${a.dot}` }"></div>
                                                <div class="min-w-0">
                                                    <p class="text-[9px] font-black uppercase tracking-wider leading-tight" :style="{ color: metaEdit.atmosphere === a.value ? a.dot : 'white' }">{{ a.label }}</p>
                                                    <p class="text-[7px] text-neutral-500 leading-tight mt-0.5 line-clamp-2">{{ a.desc }}</p>
                                                </div>
                                                <div class="ml-auto shrink-0 mt-1 w-1.5 h-1.5 rounded-full border transition-colors"
                                                    :class="metaEdit.atmosphere === a.value ? 'bg-white border-white' : 'border-neutral-700'"
                                                ></div>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="p-3 flex gap-2">
                                    <button @click="cancelEdit"
                                        class="text-[9px] font-black uppercase tracking-widest px-3 py-1.5 border border-white/20 text-neutral-400 hover:text-white transition-all">
                                        {{ commonTexts.CANCEL }}
                                    </button>
                                    <button @click="saveEdit"
                                        class="text-[9px] font-black uppercase tracking-widest px-4 py-1.5 bg-white text-black hover:bg-neutral-200 transition-all">
                                        {{ texts.BTN_SAVE }}
                                    </button>
                            </div>
                        </div>
                    </section>

                    <!-- ── Visual Prompt ──────────────────────────────── -->
                    <section v-if="shot.visual_prompt" class="space-y-2">
                        <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">{{ texts.LABEL_VISUAL_PROMPT }}</p>
                        <div class="border-l-2 pl-4 py-1" :style="{ borderColor: accent }">
                            <p class="text-[10px] leading-relaxed" style="color: rgba(200,240,255,0.7)">{{ shot.visual_prompt }}</p>
                        </div>
                    </section>

                    <!-- ── Reference Photo (Only if no variants) ───────────────────────────── -->
                    <section v-if="originalUrl && (!shot.images || !shot.images.length)" class="space-y-2">
                        <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">{{ texts.LABEL_REF_PHOTO }}</p>
                        <div class="aspect-[3/2] bg-black border border-white/10 overflow-hidden">
                            <img :src="originalUrl" alt="original" class="w-full h-full object-cover" />
                        </div>
                    </section>

                    <!-- ── Workspace Gallery ────────────────────────────── -->
                    <section v-if="shot.images && shot.images.length" class="space-y-3">
                        <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">{{ texts.LABEL_GEN_VARIANTS }}</p>
                        <div class="grid grid-cols-2 gap-4">
                            <div
                                v-for="img in shot.images"
                                :key="img.id"
                                :class="[
                                    'relative aspect-[3/2] border transition-all overflow-hidden flex flex-col bg-black',
                                    selectedComflyId === img.id ? 'border-white ring-1 ring-white' : 'border-white/10 hover:border-white/20'
                                ]"
                            >
                                <!-- Loading state (Always shows if queued, regardless of selection) -->
                                <div v-if="img.status === 'queue'" class="absolute inset-0 flex flex-col items-center justify-center gap-2 z-30 bg-black/60 backdrop-blur-[2px]">
                                    <div class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></div>
                                    <span class="text-[8px] text-amber-500 font-black tracking-widest uppercase">{{ texts.LABEL_PROCESSING }}</span>
                                </div>

                                <!-- View Layer (Image) -->
                                <div 
                                    v-show="selectedComflyId !== img.id" 
                                    @click="selectedComflyId = img.id"
                                    class="absolute inset-0 cursor-pointer group"
                                >
                                    <img :src="getImageUrl(img.id)"
                                         class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                                    <!-- Mini Badges -->
                                    <div v-if="img.status === 'approved'" class="absolute top-2 right-2 bg-cyan-500 text-black px-1.5 py-0.5 text-[7px] font-black uppercase">Approved ✓</div>
                                </div>

                                <!-- Action Layer (Overlay when selected) -->
                                <div v-show="selectedComflyId === img.id && img.status !== 'queue'" class="absolute inset-0 bg-[#080808] flex flex-col z-20">
                                    <!-- Focused Image Preview (small background) -->
                                    <div class="absolute inset-0 opacity-10 pointer-events-none">
                                        <img :src="getImageUrl(img.id)" class="w-full h-full object-cover blur-sm" />
                                    </div>
                                    
                                    <!-- Header -->
                                    <div class="relative flex items-center justify-between px-3 py-2 border-b border-white/5 shrink-0 z-10 bg-black/40">
                                        <span class="text-[8px] text-neutral-500 font-bold uppercase tracking-widest">{{ img.id.split('-')[0] }}</span>
                                        <button @click.stop="selectedComflyId = null" class="text-neutral-500 hover:text-white text-[9px] font-black uppercase">{{ texts.BTN_CLOSE }}</button>
                                    </div>

                                    <!-- Body: Correction -->
                                    <div class="relative flex-1 p-3 flex flex-col min-h-0 space-y-2 overflow-y-auto custom-scrollbar z-10">
                                        <div class="space-y-2 flex-1 flex flex-col pt-1">
                                            <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.2em]">{{ texts.LABEL_REFINEMENT }}</p>
                                            <textarea
                                                v-model="correctionText" rows="2"
                                                autocomplete="off"
                                                spellcheck="false"
                                                data-lpignore="true"
                                                data-form-type="other"
                                                placeholder="Describe changes (e.g. 'more contrast', 'focus on chip')..."
                                                class="flex-1 w-full bg-[#111] border-2 border-white/20 p-2.5 text-[11px] text-white focus:outline-none focus:border-white/60 resize-none placeholder-neutral-600 shadow-inner"
                                            ></textarea>
                                            <button
                                                @click="handleCorrect"
                                                :disabled="studioStore.isGenerating || !correctionText.trim()"
                                                class="w-full py-2.5 text-black text-[10px] font-black uppercase tracking-[0.25em] transition-all disabled:opacity-20 disabled:grayscale shrink-0 shadow-[0_4px_0_0_rgba(0,0,0,0.3)] active:translate-y-0.5 active:shadow-none"
                                                :style="{ background: accent }"
                                            >
                                                {{ texts.BTN_REGENERATE }}
                                            </button>
                                        </div>
                                    </div>

                                    <!-- Footer: Status Actions (Approve & Discard) -->
                                    <div class="flex border-t border-white/10 shrink-0 bg-black/40">
                                        <!-- State: Approved -->
                                        <div v-if="img.status === 'approved'"
                                            class="flex-1 py-2 bg-cyan-500 text-black text-[8px] font-black uppercase tracking-widest border-r border-white/10 text-center flex items-center justify-center"
                                        >
                                            Approved ✓
                                        </div>

                                        <!-- State: Generated -->
                                        <button
                                            v-else-if="img.status === 'generated'"
                                            @click="handleApprove"
                                            class="flex-1 py-2 bg-emerald-950/20 text-emerald-500 text-[8px] font-black uppercase tracking-widest border-r border-white/10 hover:bg-emerald-600 hover:text-white transition-all"
                                        >
                                            ✓ {{ texts.BTN_APPROVE }}
                                        </button>

                                        <button
                                            @click="handleDeleteVariant(img.id)"
                                            class="flex-1 py-2 text-neutral-600 hover:text-red-500 text-[8px] font-black uppercase tracking-widest hover:bg-red-950/30 transition-all"
                                        >
                                            ✕ {{ texts.DISCARD }}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                    <!-- ── Upload ────────────────────────────────────── -->
                    <section class="space-y-3">
                        <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">
                            {{ shot.has_original ? 'Re-Upload & Restart' : 'Upload Reference Photo' }}
                        </p>

                        <div v-if="!shot.focus || !shot.atmosphere"
                            class="px-4 py-3 border border-amber-500/40 bg-amber-500/10 text-[9px] text-amber-300">
                            ⚠ Completa <strong>Focus</strong> y <strong>Atmosphere</strong> antes de subir.
                        </div>

                        <input ref="fileInput" id="shot_file_input" type="file" accept="image/png,image/jpeg" class="hidden" @change="handleFileSelected" />

                        <button
                            type="button"
                            @click="triggerUpload"
                            :disabled="studioStore.isGenerating || !shot.focus || !shot.atmosphere"
                            :class="[
                                'w-full py-3 border text-[10px] font-black uppercase tracking-[0.25em] transition-all disabled:opacity-30 disabled:cursor-not-allowed',
                                studioStore.isGenerating ? 'border-white/10 bg-white/5 text-neutral-500' : 'border-white/25 text-white hover:bg-white/5'
                            ]"
                        >
                            {{ studioStore.isGenerating ? texts.LABEL_PROCESSING + '…' : (shot.has_original ? texts.RE_UPLOAD_RESTART : texts.UPLOAD_GENERATE) }}
                        </button>
                    </section>

                </div>
            </div>
        </template>
    </div>
</template>

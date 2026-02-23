<script setup>
import { ref, computed, watch } from 'vue'
import { useStudioStore } from '../../stores/studio'
import StudioService from '../../services/StudioService'

const props = defineProps({
    collection: { type: String, required: true },
    slug: { type: String, required: true },
})

const emit = defineEmits(['delete-shot'])

const studioStore = useStudioStore()
const shot = computed(() => studioStore.currentShot)

const types = [
    { value: 'macro',       icon: '⌀', label: 'Macro',       desc: 'Close-up extremo de un componente: junta de soldadura, conector, área de PCB.' },
    { value: 'context',     icon: '◫', label: 'Context',     desc: 'Plano medio o abierto que muestra el objeto en su entorno de operación real.' },
    { value: 'conceptual',  icon: '◈', label: 'Conceptual',  desc: 'Toma abstracta que comunica el concepto central del proyecto (escala, power glow, contraste orgánico vs. electrónico).' },
]

const atmospheres = [
    { value: 'rojo',     dot: '#D4442F', label: 'Rojo',     desc: 'Estados activos, encendido, componentes de alta energía (LEDs, rieles de poder, soldadura).' },
    { value: 'turquesa', dot: '#00A6B6', label: 'Turquesa', desc: 'Estados idle, RF/datos, sensores, partes electrónicas de precisión.' },
    { value: 'ambar',    dot: '#F59E0B', label: 'Ámbar',    desc: 'Eventos térmicos, materiales orgánicos, contextos vintage o cálidos.' },
]

const fileInput = ref(null)
const correctionText = ref('')
const isEditingMeta = ref(false)
const metaEdit = ref({})

// --- BUGFIX: Reset edit mode when shot selection changes ---
watch(() => studioStore.currentShot?.shot_id, () => {
    isEditingMeta.value = false
    correctionText.value = ''
})

// Accent color for atmosphere
const atmosphereAccent = { rojo: '#D4442F', turquesa: '#00A6B6', ambar: '#F59E0B' }
const accent = computed(() => atmosphereAccent[shot.value?.atmosphere] || '#6b7280')

// Original image URL
const originalUrl = computed(() =>
    shot.value?.has_original
        ? StudioService.getOriginalImageUrl(props.collection, props.slug, shot.value.shot_id)
        : null
)

// Status
const statusLabel = {
    pending_upload: 'Pending Upload',
    queued: 'Queued in ComfyUI…',
    generated: 'Generated — awaiting approval',
    approved: 'Approved ✓',
}

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
    if (!correctionText.value.trim()) return
    await studioStore.correctShot(props.collection, props.slug, shot.value.shot_id, correctionText.value.trim())
    correctionText.value = ''
}

// Approve
const handleApprove = async () => {
    const filename = shot.value.approved_filename || 'generated.png'
    await studioStore.approveShot(props.collection, props.slug, shot.value.shot_id, filename)
}
</script>

<template>
    <div class="flex flex-col h-full bg-[#050505] font-mono text-xs overflow-hidden">

        <!-- Empty state -->
        <div v-if="!shot" class="flex-1 flex flex-col items-center justify-center gap-3">
            <div class="text-5xl opacity-10 select-none">⌀</div>
            <p class="text-[10px] uppercase tracking-[0.3em] text-neutral-600">Select a shot</p>
        </div>

        <template v-else>
            <!-- Header -->
            <div class="px-6 py-4 border-b border-white/10 bg-[#080808] shrink-0">
                <div class="flex items-center gap-3 mb-1.5">
                    <div class="w-1 h-5 shrink-0" :style="{ background: accent }"></div>
                    <h2 class="text-[13px] font-black tracking-widest uppercase text-white flex-1">{{ shot.title }}</h2>
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
                            <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">Metadata</p>
                            <button
                                v-if="!isEditingMeta"
                                @click="startEdit"
                                class="text-[9px] font-black uppercase tracking-widest px-3 py-1 border border-white/20 text-white hover:bg-white hover:text-black transition-all"
                            >
                                Edit
                            </button>
                        </div>

                        <!-- Display -->
                        <div v-if="!isEditingMeta" class="border border-white/10 divide-y divide-white/5">
                            <div class="p-3 space-y-0.5">
                                <p class="text-[8px] text-neutral-500 uppercase tracking-wider">Title</p>
                                <p class="text-[11px] text-white leading-relaxed font-bold">{{ shot.title || '—' }}</p>
                            </div>
                            <div class="grid grid-cols-2 divide-x divide-white/5">
                                <div class="p-3 space-y-0.5">
                                    <p class="text-[8px] text-neutral-500 uppercase tracking-wider">Type</p>
                                    <p class="text-[10px] text-neutral-200 uppercase tracking-widest">{{ shot.type || '—' }}</p>
                                </div>
                                <div class="p-3 space-y-0.5">
                                    <p class="text-[8px] text-neutral-500 uppercase tracking-wider">Atmosphere</p>
                                    <div class="flex items-center gap-2">
                                        <div class="w-1.5 h-1.5 rounded-full" :style="{ background: accent }"></div>
                                        <p class="text-[10px] font-bold uppercase" :style="{ color: accent }">{{ shot.atmosphere || '—' }}</p>
                                    </div>
                                </div>
                            </div>
                            <div class="p-3 space-y-0.5">
                                <p class="text-[8px] text-neutral-500 uppercase tracking-wider">Description</p>
                                <p class="text-[11px] text-neutral-200 leading-relaxed">{{ shot.description || '—' }}</p>
                            </div>
                            <div class="p-3 space-y-0.5">
                                <p class="text-[8px] text-neutral-500 uppercase tracking-wider">Protagonist / Focus</p>
                                <p class="text-[11px] text-neutral-200 leading-relaxed">{{ shot.focus || '—' }}</p>
                            </div>
                        </div>

                        <!-- Edit form -->
                        <div v-else class="border border-white/20 divide-y divide-white/10">
                            <div class="p-3 space-y-1">
                                <p class="text-[8px] text-neutral-400 uppercase tracking-wider">Title</p>
                                <input v-model="metaEdit.title"
                                    class="w-full bg-transparent text-[11px] text-white focus:outline-none border-b border-white/20 focus:border-white pb-1" />
                            </div>
                            <div class="p-3 space-y-1">
                                <p class="text-[8px] text-neutral-400 uppercase tracking-wider">Description</p>
                                <textarea v-model="metaEdit.description" rows="2"
                                    class="w-full bg-transparent text-[11px] text-white focus:outline-none resize-none border-b border-white/20 focus:border-white pb-1"></textarea>
                            </div>
                            <div class="p-3 space-y-1">
                                <p class="text-[8px] text-neutral-400 uppercase tracking-wider">Focus</p>
                                <input v-model="metaEdit.focus"
                                    class="w-full bg-transparent text-[11px] text-white focus:outline-none border-b border-white/20 focus:border-white pb-1" />
                            </div>
                            <div class="p-3 bg-black/10">
                                <div class="grid grid-cols-2 gap-4">
                                    <div class="space-y-2">
                                        <p class="text-[8px] text-neutral-400 uppercase tracking-wider">Type</p>
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
                                        <p class="text-[8px] text-neutral-400 uppercase tracking-wider">Atmosphere</p>
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
                                    Cancel
                                </button>
                                <button @click="saveEdit"
                                    class="text-[9px] font-black uppercase tracking-widest px-4 py-1.5 bg-white text-black hover:bg-neutral-200 transition-all">
                                    Save
                                </button>
                            </div>
                        </div>
                    </section>

                    <!-- ── Visual Prompt ──────────────────────────────── -->
                    <section v-if="shot.visual_prompt" class="space-y-2">
                        <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">Visual Prompt</p>
                        <div class="border-l-2 pl-4 py-1" :style="{ borderColor: accent }">
                            <p class="text-[10px] leading-relaxed" style="color: rgba(200,240,255,0.7)">{{ shot.visual_prompt }}</p>
                        </div>
                    </section>

                    <!-- ── Reference Photo ───────────────────────────── -->
                    <section v-if="originalUrl" class="space-y-2">
                        <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">Reference Photo</p>
                        <img :src="originalUrl" alt="original" class="w-full border border-white/10 object-cover" />
                    </section>

                    <!-- ── Upload ────────────────────────────────────── -->
                    <section class="space-y-3">
                        <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">
                            {{ shot.has_original ? 'Re-Upload & Regenerate' : 'Upload Reference Photo' }}
                        </p>

                        <div v-if="!shot.focus || !shot.atmosphere"
                            class="px-4 py-3 border border-amber-500/40 bg-amber-500/10 text-[9px] text-amber-300">
                            ⚠ Completa <strong>Focus</strong> y <strong>Atmosphere</strong> antes de subir.
                        </div>

                        <input ref="fileInput" type="file" accept="image/png,image/jpeg" class="hidden" @change="handleFileSelected" />

                        <button
                            @click="triggerUpload"
                            :disabled="studioStore.isGenerating || !shot.focus || !shot.atmosphere"
                            class="w-full py-3 border text-[10px] font-black uppercase tracking-[0.25em] transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                            style="border-color: rgba(255,255,255,0.25); color: white;"
                            onmouseenter="this.style.background='rgba(255,255,255,0.06)'"
                            onmouseleave="this.style.background='transparent'"
                        >
                            <span v-if="studioStore.isGenerating">PROCESANDO…</span>
                            <span v-else>{{ shot.has_original ? '↺ RE-UPLOAD & GENERATE' : '↑ UPLOAD & GENERATE' }}</span>
                        </button>
                    </section>

                    <!-- ── Queued State ───────────────────────────────── -->
                    <section v-if="shot.status === 'queued'"
                        class="py-6 border border-amber-500/30 bg-amber-500/5 text-center space-y-3">
                        <div class="flex justify-center gap-1.5">
                            <div v-for="i in 3" :key="i"
                                class="w-2 h-2 rounded-full bg-amber-400 animate-bounce"
                                :style="{ animationDelay: (i * 0.2) + 's' }"></div>
                        </div>
                        <p class="text-[10px] font-black tracking-[0.3em] text-amber-400 uppercase">Procesando en ComfyUI</p>
                        <p class="text-[8px] text-neutral-500">prompt_id: {{ shot.prompt_id }}</p>
                    </section>

                    <!-- ── Correction ─────────────────────────────────── -->
                    <section v-if="shot.status === 'generated' || shot.status === 'approved'" class="space-y-3">
                        <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">Correction Loop</p>
                        <textarea
                            v-model="correctionText" rows="2"
                            placeholder="e.g. Darker background, sharper focus on solder joints…"
                            :disabled="studioStore.isGenerating"
                            class="w-full bg-[#0a0a0a] border border-white/20 p-3 text-[11px] text-white focus:outline-none focus:border-white resize-none placeholder-neutral-600 disabled:opacity-40"
                        ></textarea>
                        <button
                            @click="handleCorrect"
                            :disabled="studioStore.isGenerating || !correctionText.trim()"
                            class="w-full py-2.5 text-[10px] font-black uppercase tracking-[0.25em] border transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                            :style="{ borderColor: accent + '60', color: accent }"
                        >
                            APPLY CORRECTION
                        </button>
                    </section>

                    <!-- ── Approve ─────────────────────────────────────── -->
                    <section v-if="shot.status === 'generated'" class="space-y-3">
                        <p class="text-[9px] text-neutral-300 font-black uppercase tracking-[0.25em]">Approve Result</p>
                        <button
                            @click="handleApprove"
                            class="w-full py-3 text-[10px] font-black uppercase tracking-[0.25em] border border-emerald-500/40 text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 transition-all"
                        >
                            ✓ APPROVE SHOT
                        </button>
                    </section>

                    <!-- ── Approved Badge ──────────────────────────────── -->
                    <section v-if="shot.status === 'approved'"
                        class="py-5 border border-cyan-500/30 bg-cyan-500/5 text-center space-y-1">
                        <p class="text-[11px] font-black tracking-[0.3em] text-cyan-400 uppercase">Shot Approved</p>
                        <p class="text-[8px] text-neutral-500">{{ shot.approved_filename }}</p>
                    </section>

                </div>
            </div>
        </template>
    </div>
</template>

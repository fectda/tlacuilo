<script setup>
import { computed } from 'vue'

const props = defineProps({
    shot: { type: Object, required: true },
    isSelected: { type: Boolean, default: false },
})

const emit = defineEmits(['select', 'delete'])

const statusConfig = {
    pending_upload: { label: 'PENDING UPLOAD', textColor: '#6b7280', dotColor: '#4b5563' },
    queued:         { label: 'QUEUED',          textColor: '#f59e0b', dotColor: '#f59e0b' },
    generated:      { label: 'GENERATED',       textColor: '#10b981', dotColor: '#10b981' },
    approved:       { label: 'APPROVED ✓',      textColor: '#22d3ee', dotColor: '#22d3ee' },
}

const atmosphereStyle = {
    rojo:     { bg: 'rgba(212,68,47,0.25)',  text: '#f87171', border: 'rgba(212,68,47,0.4)' },
    turquesa: { bg: 'rgba(0,166,182,0.2)',   text: '#22d3ee', border: 'rgba(0,166,182,0.4)' },
    ambar:    { bg: 'rgba(245,158,11,0.2)',  text: '#fbbf24', border: 'rgba(245,158,11,0.4)' },
}

const typeIcon = { macro: '⌀', context: '◫', conceptual: '◈' }

const status = computed(() => statusConfig[props.shot.status] || statusConfig.pending_upload)
const atm = computed(() => atmosphereStyle[props.shot.atmosphere] || null)
</script>

<template>
    <div
        @click="emit('select', shot)"
        :style="{
            borderColor: isSelected ? 'rgba(255,255,255,0.25)' : 'rgba(255,255,255,0.06)',
            background: isSelected ? 'rgba(255,255,255,0.05)' : 'transparent',
        }"
        class="group cursor-pointer border p-4 transition-all hover:border-white/15 hover:bg-white/[0.03]"
    >
        <!-- Title row -->
        <div class="flex items-start justify-between gap-2 mb-3">
            <div class="flex items-center gap-2 min-w-0">
                <span class="text-neutral-400 text-[11px] shrink-0">{{ typeIcon[shot.type] || '◇' }}</span>
                <span class="text-[11px] font-bold text-white truncate uppercase tracking-wider">{{ shot.title }}</span>
            </div>
            <button
                @click.stop="emit('delete', shot.shot_id)"
                class="text-neutral-600 hover:text-red-400 transition-colors text-[12px] shrink-0 leading-none"
            >✕</button>
        </div>

        <!-- Status row -->
        <div class="flex items-center gap-2 mb-3">
            <div class="w-1.5 h-1.5 rounded-full shrink-0" :style="{ background: status.dotColor, boxShadow: `0 0 4px ${status.dotColor}` }"></div>
            <span class="text-[9px] font-bold tracking-[0.15em] uppercase" :style="{ color: status.textColor }">
                {{ status.label }}
            </span>
        </div>

        <!-- Tags row -->
        <div class="flex items-center gap-2 flex-wrap">
            <span
                v-if="shot.atmosphere && atm"
                class="text-[9px] px-2 py-0.5 font-bold uppercase tracking-widest border"
                :style="{ background: atm.bg, color: atm.text, borderColor: atm.border }"
            >
                {{ shot.atmosphere }}
            </span>
            <span class="text-[9px] text-neutral-400 uppercase tracking-widest">{{ shot.type }}</span>
            <span v-if="shot.has_original" class="ml-auto text-[8px] text-emerald-500/80 font-bold">IMG ✓</span>
        </div>
    </div>
</template>

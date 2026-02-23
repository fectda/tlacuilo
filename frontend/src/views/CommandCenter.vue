<script setup>
import { useRouter } from 'vue-router'
import ProjectGrid from '../components/ProjectGrid.vue'
import SystemVitals from '../components/SystemVitals.vue'
import BaseIcon from '../components/BaseIcon.vue'
import { UI_STRINGS } from '../constants/uiStrings'

const router = useRouter()
</script>

<template>
  <div class="h-full flex flex-col bg-background overflow-hidden">
    <header class="p-4 border-b border-white/5 flex justify-between items-center bg-background shrink-0 z-50">
      <h1 class="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
        TLACUILO
      </h1>
      <div class="text-sm text-neutral-600 font-mono">v1.2.0</div>
    </header>

    <main class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="container mx-auto p-4 space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <!-- Hero Section -->
        <section class="relative overflow-hidden p-8 rounded-3xl glass-card bg-gradient-refined border-white/5">
          <div class="absolute top-0 right-0 -m-32 w-96 h-96 bg-accent/5 rounded-full blur-[120px]"></div>
          <div class="absolute bottom-0 left-0 -m-20 w-80 h-80 bg-primary/5 rounded-full blur-[100px]"></div>
          
          <div class="relative z-10">
            <h1 class="text-6xl font-black tracking-tighter mb-4 text-white uppercase italic">
              {{ UI_STRINGS.common.command_center }}
            </h1>
            <p class="text-neutral-400 text-lg max-w-xl leading-relaxed font-light">
              {{ UI_STRINGS.common.welcome_message }}
              <span class="text-accent font-bold uppercase tracking-widest text-sm">Tlacuilo</span>. 
              {{ UI_STRINGS.common.hero_description }}
            </p>
          </div>
        </section>

        <!-- Main Grid -->
        <ProjectGrid />
        
        <!-- System & Activity Footer -->
        <section class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-4 pb-12">
          <SystemVitals />

          <div class="glass-card p-6 border-l-4 border-l-primary shadow-glow-primary/10">
            <h3 class="text-xl font-bold mb-6 flex items-center gap-2">
              <BaseIcon name="history" class="text-primary" />
              {{ UI_STRINGS.common.telemetry }}
            </h3>
            <div class="flex flex-col items-center justify-center py-6 text-neutral-600 italic">
              <BaseIcon name="archive" class="w-12 h-12 mb-2 opacity-20" />
              <span class="text-sm">{{ UI_STRINGS.common.no_activity }}</span>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

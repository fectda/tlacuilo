<script setup>
import { UI_TEXTS } from './constants/uiTexts'
import SystemVitals from './components/SystemVitals.vue'

const texts = UI_TEXTS.APP
</script>

<template>
  <div class="bg-black h-screen overflow-hidden text-white font-sans flex justify-center">
    <div class="w-full max-w-[1400px] h-full bg-background border-x border-white/5 flex flex-col relative shadow-[0_0_100px_rgba(0,0,0,0.5)]">
       <div class="flex-1 overflow-hidden relative">
         <router-view></router-view>
       </div>
       <footer class="shrink-0 border-t border-white/5 p-4 bg-background z-50">
         <SystemVitals />
       </footer>
    </div>
  </div>
</template>

<style scoped>
</style>

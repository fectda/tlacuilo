<script setup>
import { UI_TEXTS } from './constants/uiTexts'

const texts = UI_TEXTS.APP
</script>

<template>
  <div class="bg-black h-screen overflow-hidden text-white font-sans flex justify-center">
    <div class="w-full max-w-[1400px] h-full bg-background border-x border-white/5 relative shadow-[0_0_100px_rgba(0,0,0,0.5)]">
       <router-view></router-view>
    </div>
  </div>
</template>

<style scoped>
</style>

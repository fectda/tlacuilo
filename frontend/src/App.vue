<script setup>
import { UI_TEXTS } from './constants/uiTexts'

const texts = UI_TEXTS.APP
</script>

<template>
  <div class="bg-background min-h-screen text-white font-sans">
    <header class="p-4 border-b border-primary/20 flex justify-between items-center">
      <h1 class="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
        {{ texts.TITLE }}
      </h1>
      <div class="text-sm text-gray-500">{{ texts.VERSION }}</div>
    </header>
    
    <main class="container mx-auto p-4">
      <router-view></router-view>
    </main>
  </div>
</template>

<style scoped>
</style>

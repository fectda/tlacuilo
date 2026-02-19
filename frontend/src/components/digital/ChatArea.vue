<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import { useChatStore } from '../../stores/chat'
import { marked } from 'marked'

const props = defineProps({
  collection: {
    type: String,
    required: true
  },
  slug: {
    type: String,
    required: true
  }
})

const chatStore = useChatStore()
const messageInput = ref('')
const messagesContainer = ref(null)

const scrollToBottom = async () => {
    await nextTick()
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
}

// Watch for new messages to scroll
watch(() => chatStore.history, () => {
    scrollToBottom()
}, { deep: true })

onMounted(() => {
    scrollToBottom()
})

const handleSend = async () => {
    if (!messageInput.value.trim() || chatStore.isTyping) return
    
    const text = messageInput.value
    messageInput.value = ''
    
    await chatStore.sendMessage(props.collection, props.slug, text)
}

const renderMarkdown = (text) => {
    return marked(text)
}
</script>

<template>
    <div class="flex flex-col h-full bg-[#050505] text-gray-300 font-mono text-xs relative">
        <!-- Messages Area -->
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar pb-32">
            <template v-if="chatStore.history.length === 0">
                 <div class="flex flex-col items-center justify-center h-full text-neutral-600 opacity-50">
                    <span class="mb-2 text-2xl tracking-[0.2em] font-bold">TLACUILO</span>
                    <p class="text-[10px]">INICIA LA CONVERSACIÓN...</p>
                 </div>
            </template>
            
            <div v-for="(msg, index) in chatStore.history" :key="index" 
                 class="flex flex-col gap-1 max-w-2xl mx-auto"
                 :class="msg.role === 'user' ? 'items-end' : 'items-start'">
                
                <span class="text-[9px] uppercase tracking-[0.2em] text-neutral-600 mb-1">
                    {{ msg.role === 'user' ? '// USUARIO' : '// TLACUILO' }}
                </span>
                
                <div class="p-4 border max-w-[90%] transition-colors duration-300"
                     :class="msg.role === 'user' 
                        ? 'bg-neutral-900 border-neutral-800 text-neutral-300' 
                        : 'bg-transparent border-neutral-900 text-neutral-400 hover:border-neutral-800'">
                    <div class="prose prose-invert prose-xs max-w-none leading-relaxed" v-html="renderMarkdown(msg.content)"></div>
                </div>
            </div>

            <!-- Typing Indicator -->
             <div v-if="chatStore.isTyping" class="flex flex-col gap-1 max-w-2xl mx-auto items-start animate-pulse">
                <span class="text-[9px] uppercase tracking-[0.2em] text-neutral-700 mb-1">// TLACUILO</span>
                <div class="p-4 border border-neutral-900 bg-transparent text-neutral-600">
                    <span class="text-[9px] tracking-[0.3em]">ESCRIBIENDO...</span>
                </div>
            </div>
            
             <!-- Error Message -->
            <div v-if="chatStore.error" class="max-w-2xl mx-auto mt-4 p-3 border border-red-900/50 bg-red-900/10 text-red-500 text-[10px] text-center tracking-widest uppercase">
                ERROR: {{ chatStore.error }}
            </div>
        </div>

        <!-- Input Area -->
        <div class="absolute bottom-0 left-0 w-full bg-black/80 backdrop-blur-md border-t border-white/5 p-6 shadow-[0_-10px_20px_rgba(0,0,0,0.5)]">
            <div class="max-w-2xl mx-auto relative group">
                <input 
                    v-model="messageInput"
                    @keydown.enter="handleSend"
                    type="text" 
                    placeholder="COMANDO / MENSAJE..."
                    class="w-full bg-[#0a0a0a] border border-neutral-900 p-4 pr-12 text-neutral-300 placeholder-neutral-700 focus:outline-none focus:border-white/20 focus:bg-[#0f0f0f] transition-all font-mono text-xs tracking-wider"
                    :disabled="chatStore.isTyping"
                />
                <button 
                    @click="handleSend"
                    :disabled="!messageInput.trim() || chatStore.isTyping"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-700 hover:text-white disabled:opacity-30 disabled:hover:text-neutral-700 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                    </svg>
                </button>
            </div>
             <div class="max-w-2xl mx-auto mt-3 flex justify-between items-center px-1">
                 <div class="flex items-center gap-3">
                    <span class="text-[9px] text-neutral-700 uppercase tracking-[0.2em] flex items-center gap-2">
                        <span class="w-1 h-1 bg-neutral-800 rounded-full animate-pulse"></span>
                        MODO: {{ chatStore.mode }}
                    </span>
                 </div>
                  <button 
                        @click="chatStore.generateDraft(collection, slug)"
                        :disabled="chatStore.isTyping"
                        class="text-[9px] font-bold px-3 py-1 border border-neutral-800 text-neutral-500 hover:text-neutral-200 hover:border-neutral-600 hover:bg-neutral-900 disabled:opacity-30 disabled:cursor-not-allowed transition-all uppercase tracking-[0.2em]"
                    >
                        GENERAR BORRADOR
                    </button>
             </div>
        </div>
    </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: #050505;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #262626;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #404040;
}
</style>

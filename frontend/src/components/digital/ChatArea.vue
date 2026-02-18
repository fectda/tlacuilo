<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useChatStore } from '../../stores/chat'
import { useRoute } from 'vue-router'

const props = defineProps(['projectId'])
const chatStore = useChatStore()
const messageInput = ref('')
const chatContainer = ref(null)

const scrollToBottom = async () => {
    await nextTick()
    if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
}

watch(() => chatStore.history.length, scrollToBottom)

const sendMessage = async () => {
    if (!messageInput.value.trim() || chatStore.isTyping) return
    
    const msg = messageInput.value
    messageInput.value = ''
    
    await chatStore.sendMessage(props.projectId, msg)
}

// Auto-resize textarea
const adjustHeight = (el) => {
    el.style.height = 'auto'
    el.style.height = el.scrollHeight + 'px'
}
</script>

<template>
    <div class="flex flex-col h-full bg-neutral-900 border-r border-white/10">
        <!-- Chat History -->
        <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-6">
            <div v-if="chatStore.history.length === 0" class="text-center text-neutral-500 mt-10">
                <p>Iniciando entrevista...</p>
            </div>
            
            <div v-for="(msg, index) in chatStore.history" :key="index" 
                 class="flex flex-col max-w-3xl mx-auto animate-fade-in"
                 :class="msg.role === 'user' ? 'items-end' : 'items-start'">
                
                <div class="text-xs text-neutral-500 mb-1 uppercase tracking-wider font-mono">
                    {{ msg.role === 'user' ? 'Tú' : 'Tlacuilo' }}
                </div>
                
                <div class="p-4 rounded-lg max-w-[90%] text-sm leading-relaxed whitespace-pre-wrap"
                     :class="msg.role === 'user' ? 'bg-neutral-800 text-white' : 'bg-transparent border border-white/10 text-neutral-200'">
                    <!-- TODO: Add proper Markdown rendering here -->
                    {{ msg.content }}
                </div>
            </div>

            <div v-if="chatStore.isTyping" class="flex flex-col items-start max-w-3xl mx-auto">
                 <div class="text-xs text-neutral-500 mb-1 uppercase tracking-wider font-mono">Tlacuilo</div>
                 <div class="p-4 rounded-lg bg-transparent border border-white/10 text-neutral-400 italic">
                     Escribiendo...
                 </div>
            </div>
             <div v-if="chatStore.error" class="text-center text-red-500 text-sm mt-4">
                {{ chatStore.error }}
            </div>
        </div>

        <!-- Input Area -->
        <div class="p-6 border-t border-white/10 bg-neutral-900 z-10">
            <div class="max-w-3xl mx-auto relative">
                <textarea 
                    v-model="messageInput"
                    @keydown.enter.exact.prevent="sendMessage"
                    @input="e => adjustHeight(e.target)"
                    :disabled="chatStore.isTyping"
                    placeholder="Escribe tu respuesta..."
                    class="w-full bg-neutral-800 text-white rounded-lg p-4 pr-12 resize-none focus:outline-none focus:ring-1 focus:ring-amber-500/50 disabled:opacity-50 min-h-[56px] max-h-48 scrollbar-hide"
                    rows="1"
                ></textarea>
                
                <button 
                    @click="sendMessage"
                    :disabled="!messageInput.trim() || chatStore.isTyping"
                    class="absolute right-3 bottom-3 p-2 text-neutral-400 hover:text-amber-500 disabled:text-neutral-600 transition-colors"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
            </div>
            
            <div class="max-w-3xl mx-auto flex justify-between items-center mt-2">
                <div class="text-xs text-neutral-600 font-mono">
                    ENTER para enviar
                </div>
                 <div class="flex gap-2">
                    <button 
                        @click="chatStore.generateDraft(projectId)"
                        :disabled="chatStore.isTyping"
                        class="text-xs font-mono px-3 py-1 rounded border border-amber-500/30 text-amber-500 hover:bg-amber-500/10 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                    >
                        [GENERATE DRAFT]
                    </button>
                    <!-- RESET MEMORY BUTTON logic not fully implemented in UI but requested in docs -->
                     <button class="text-xs font-mono px-3 py-1 rounded border border-red-500/30 text-red-500 hover:bg-red-500/10 transition-all opacity-50 hover:opacity-100">
                        [RESET]
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
    display: none;
}
.animate-fade-in {
    animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>

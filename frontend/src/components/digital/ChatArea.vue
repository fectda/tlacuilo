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
const isMonologueMode = ref(false)

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

onMounted(async () => {
    scrollToBottom()
})

const handleSend = async () => {
    if (!messageInput.value.trim() || chatStore.isTyping) return
    
    const text = messageInput.value
    messageInput.value = ''
    
    // Reset textarea height after sending
    const textarea = document.getElementById('chat-input')
    if (textarea) textarea.style.height = 'auto'
    
    await chatStore.sendMessage(props.collection, props.slug, text, false, isMonologueMode.value)
}

const handleKeydown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSend()
    }
}

const autoResize = (e) => {
    const textarea = e.target
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
}

const renderMarkdown = (text) => {
    if (!text) return ''
    return marked(text)
}
</script>

<template>
    <div class="flex flex-col h-full bg-[#020202] text-gray-300 font-mono text-xs relative overflow-hidden">
        <!-- Scanline Effect Overlay -->
        <div class="absolute inset-0 pointer-events-none z-0 opacity-[0.03] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%]"></div>

        <!-- Messages Area -->
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar pb-32 relative z-10">
            <template v-if="chatStore.history.length === 0 && !chatStore.isTyping && !chatStore.loading">
                 <div class="flex flex-col items-center justify-center h-full text-neutral-600">
                    <div class="border border-primary/30 p-8 bg-primary/5 shadow-glow-primary/20 backdrop-blur-sm">
                        <span class="mb-2 text-3xl tracking-[0.3em] font-bold text-primary animate-pulse">TLACUILO</span>
                        <p class="text-[10px] text-accent/80 text-center mt-2 font-bold tracking-widest">SYSTEM ONLINE</p>
                        <p class="text-[9px] text-neutral-500 text-center mt-1">Awaiting Input...</p>
                    </div>
                 </div>
            </template>
            
            <div v-for="(msg, index) in chatStore.history" :key="index" 
                 class="flex flex-col gap-1 max-w-2xl mx-auto w-full"
                 :class="msg.role === 'user' ? 'items-end' : 'items-start'">
                
                <div class="flex items-center gap-2 mb-1">
                    <span class="w-2 h-2 rounded-sm" :class="msg.role === 'user' ? 'bg-primary shadow-glow-primary' : 'bg-cyan-500 shadow-glow-cyan'"></span>
                    <span class="text-[10px] uppercase tracking-[0.2em] font-bold"
                        :class="msg.role === 'user' ? 'text-primary' : 'text-cyan-400'">
                        {{ msg.role === 'user' ? 'OPERATOR' : 'TLACUILO_AI' }}
                    </span>
                    <span class="text-[9px] text-neutral-600">[{{ new Date(msg.timestamp).toLocaleTimeString() }}]</span>
                </div>
                
                <div class="p-6 border-l-4 w-full transition-all duration-300 shadow-xl relative overflow-hidden group"
                     :class="msg.role === 'user' 
                        ? 'bg-gradient-to-r from-primary/10 to-transparent border-primary/50 text-white rounded-r-lg' 
                        : 'bg-gradient-to-r from-cyan-900/20 to-transparent border-cyan-500/50 text-cyan-100 rounded-r-lg'">
                    
                    <!-- Decoraciones de esquina -->
                    <div class="absolute top-0 right-0 p-1">
                         <svg class="w-3 h-3 opacity-50" :class="msg.role === 'user' ? 'text-primary' : 'text-cyan-500'" viewBox="0 0 10 10"><path d="M0 0 L10 0 L10 10" fill="none" stroke="currentColor"/></svg>
                    </div>

                    <div class="prose prose-invert prose-sm max-w-none leading-relaxed 
                        prose-headings:font-bold prose-headings:tracking-wider prose-headings:uppercase
                        prose-p:text-opacity-90 prose-strong:text-white"
                        :class="msg.role === 'user' ? 'prose-headings:text-primary prose-code:text-primary prose-a:text-primary' : 'prose-headings:text-cyan-400 prose-code:text-cyan-300 prose-a:text-cyan-400'"
                        v-html="renderMarkdown(msg.content)">
                    </div>
                </div>
            </div>

            <!-- Loading indicator -->
             <div v-if="chatStore.loading" class="flex flex-col items-center justify-center py-10 opacity-70">
                <div class="flex items-center gap-3 text-cyan-500">
                    <span class="w-2 h-2 bg-cyan-500 animate-ping"></span>
                    <span class="text-[10px] tracking-[0.3em] font-bold">ACCESSING MEMORY BANKS...</span>
                </div>
            </div>

            <!-- Typing Indicator -->
             <div v-if="chatStore.isTyping" class="flex flex-col gap-1 max-w-2xl mx-auto items-start w-full">
                <div class="flex items-center gap-2 mb-1">
                     <span class="w-2 h-2 rounded-sm bg-accent shadow-glow-accent animate-pulse"></span>
                     <span class="text-[10px] uppercase tracking-[0.2em] text-accent font-bold">TLACUILO_AI</span>
                </div>
                <div class="p-4 border border-accent/30 bg-accent/5 text-accent shadow-glow-accent/20 w-full max-w-[200px] skew-x-[-10deg]">
                    <div class="flex items-center gap-1">
                        <span class="w-1 h-4 bg-accent animate-pulse"></span>
                        <span class="text-[10px] tracking-[0.2em] font-bold">PROCESSING DATA</span>
                    </div>
                </div>
            </div>
            
             <!-- Error Message -->
            <div v-if="chatStore.chatError" class="max-w-2xl mx-auto mt-4 p-4 border-2 border-error bg-error/20 text-white text-[10px] text-center tracking-widest uppercase shadow-glow-error animate-pulse font-bold">
                [CRITICAL ERROR]: {{ chatStore.chatError }}
            </div>
        </div>

        <!-- Input Area -->
        <div class="relative z-20 border-t border-white/10 bg-[#0a0a0a]">
             <!-- Status Bar Decoration -->
             <div class="h-[2px] w-full bg-gradient-to-r from-primary via-accent to-cyan-500 opacity-50"></div>
             
             <div class="p-6">
                <div class="max-w-4xl mx-auto">
                    <div class="relative group">
                        <!-- Input Glow -->
                        <div class="absolute -inset-0.5 bg-gradient-to-r from-primary to-accent rounded-lg blur opacity-20 group-focus-within:opacity-50 transition duration-1000 group-focus-within:duration-200"></div>
                        
                        <div class="relative flex items-center bg-black rounded-lg border border-white/10 overflow-hidden">
                             <div class="pl-4 pr-2 text-neutral-500">
                                <span class="text-primary font-bold">❯</span>
                             </div>
                            <textarea 
                                id="chat-input"
                                v-model="messageInput"
                                @keydown="handleKeydown"
                                @input="autoResize"
                                placeholder="ENTER COMMAND OR MESSAGE..."
                                class="w-full bg-transparent p-4 text-white placeholder-neutral-600 focus:outline-none font-mono text-sm tracking-wide resize-none min-h-[52px] max-h-[200px] custom-scrollbar"
                                :disabled="chatStore.isTyping"
                                spellcheck="true"
                                rows="1"
                            ></textarea>
                            <button 
                                @click="handleSend"
                                :disabled="!messageInput.trim() || chatStore.isTyping"
                                class="p-3 m-1 text-neutral-500 hover:text-white hover:bg-white/10 rounded transition-colors disabled:opacity-30">
                                <span class="text-[10px] font-bold tracking-widest uppercase">SEND</span>
                            </button>
                        </div>
                    </div>
                    
                    <div class="mt-4 flex justify-between items-center px-1">
                        <div class="flex items-center gap-4 w-full justify-between">
                            <span class="text-[10px] text-neutral-500 uppercase tracking-[0.2em] flex items-center gap-2">
                                <span class="w-1.5 h-1.5 rounded-full" :class="chatStore.isTyping ? 'bg-accent animate-ping' : 'bg-green-500 shadow-glow-success'"></span>
                                STATUS: {{ chatStore.isTyping ? 'BUSY' : 'READY' }}
                            </span>
                            <div class="flex items-center gap-4">
                                <button 
                                    @click="isMonologueMode = !isMonologueMode"
                                    class="text-[10px] uppercase tracking-[0.2em] flex items-center gap-2 transition-colors"
                                    :class="isMonologueMode ? 'text-accent shadow-glow-accent' : 'text-neutral-500 hover:text-white'">
                                    <span class="w-2 h-2 rounded-sm border" :class="isMonologueMode ? 'bg-accent border-accent' : 'border-neutral-500'"></span>
                                    MODO MONÓLOGO
                                </button>
                                <span class="text-[10px] text-neutral-500 uppercase tracking-[0.2em]">
                                    MODE: {{ chatStore.mode }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: #020202;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #333;
    border-radius: 2px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #D4442F;
}
.shadow-glow-cyan {
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
}
</style>

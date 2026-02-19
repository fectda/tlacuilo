import api from './api';

export default {
    /**
     * Trigger session initialization.
     * @param {string} collection - atoms | bits | mind
     * @param {string} slug - project slug
     */
    async initSession(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/init`);
            return response.data;
        } catch (error) {
            console.error('Error initializing session:', error);
            throw error;
        }
    },

    /**
     * Send a message to the AI.
     * @param {string} collection - atoms | bits | mind
     * @param {string} slug - project slug
     * @param {Object} payload - { content, system_only, response_system_only }
     */
    async sendMessage(collection, slug, payload) {
        try {
            const response = await api.post(`/${collection}/${slug}/message`, payload);
            return response.data;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    },

    /**
     * Get chat history for a project.
     * @param {string} collection - atoms | bits | mind
     * @param {string} slug - project slug
     */
    async getHistory(collection, slug) {
        try {
            const response = await api.get(`/${collection}/${slug}/chat/history`);
            return response.data; // { messages: [...] }
        } catch (error) {
            console.error('Error fetching chat history:', error);
            throw error;
        }
    },

    /**
     * Generate a draft based on the conversation history.
     * @param {string} collection - atoms | bits | mind
     * @param {string} slug - project slug
     */
    async generateDraft(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/draft`);
            return response.data; // { content, status }
        } catch (error) {
            console.error('Error generating draft:', error);
            throw error;
        }
    },

    /**
     * Generate or refine an English translation.
     * @param {string} collection - atoms | bits | mind
     * @param {string} slug - project slug
     * @param {Object} payload - { from_scratch, instruction, current_draft }
     */
    async translateDraft(collection, slug, payload) {
        try {
            const response = await api.post(`/${collection}/${slug}/translate/draft`, payload);
            return response.data;
        } catch (error) {
            console.error('Error generating translation draft:', error);
            throw error;
        }
    }
};

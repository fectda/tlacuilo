import api from './api';

export default {


    async sendMessage(collection, slug, message) {
        try {
            const response = await api.post(`/${collection}/${slug}/message`, {
                message
            });
            return response.data;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    },

    async getHistory(collection, slug) {
        try {
            const response = await api.get(`/${collection}/${slug}/chat/history`);
            return response.data;
        } catch (error) {
            console.error('Error fetching chat history:', error);
            throw error;
        }
    },

    async generateDraft(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/draft`);
            return response.data;
        } catch (error) {
            console.error('Error generating draft:', error);
            throw error;
        }
    },

    async translateProject(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/translate`);
            return response.data;
        } catch (error) {
            console.error('Error starting translation:', error);
            throw error;
        }
    },

    async refineTranslation(collection, slug, message) {
        try {
            const response = await api.post(`/${collection}/${slug}/translate/refine`, {
                message
            });
            return response.data;
        } catch (error) {
            console.error('Error refining translation:', error);
            throw error;
        }
    }
};

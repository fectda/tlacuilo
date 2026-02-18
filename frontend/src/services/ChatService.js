import api from './api';

export default {
    async startChat(projectId) {
        try {
            const response = await api.post(`/chat/start/${projectId}`);
            return response.data;
        } catch (error) {
            console.error('Error starting chat:', error);
            throw error;
        }
    },

    async sendMessage(projectId, message, mode = 'interview') {
        try {
            const response = await api.post('/chat/message', {
                project_id: projectId,
                message,
                mode
            });
            return response.data;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    },

    async getHistory(projectId) {
        try {
            const response = await api.get(`/chat/history/${projectId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching chat history:', error);
            throw error;
        }
    },

    async generateDraft(projectId) {
        try {
            const response = await api.post('/chat/draft', { project_id: projectId });
            return response.data;
        } catch (error) {
            console.error('Error generating draft:', error);
            throw error;
        }
    }
};

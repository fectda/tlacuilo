import api from './api';

export default {
    async listProjects() {
        try {
            const response = await api.get('/projects/');
            return response.data;
        } catch (error) {
            console.error('Error fetching projects:', error);
            throw error;
        }
    },

    async createProject(name, collection, slug = null) {
        try {
            const response = await api.post('/projects/', {
                name,
                collection,
                slug
            });
            return response.data;
        } catch (error) {
            console.error('Error creating project:', error);
            throw error;
        }
    },

    async forgetProject(collection, slug) {
        try {
            const response = await api.post(`/projects/forget/${collection}/${slug}`);
            return response.data;
        } catch (error) {
            console.error('Error forgetting project:', error);
            throw error;
        }
    },

    async resurrectProject(collection, slug) {
        try {
            const response = await api.post(`/projects/resurrect/${collection}/${slug}`);
            return response.data;
        } catch (error) {
            console.error('Error resurrecting project:', error);
            throw error;
        }
    }
};

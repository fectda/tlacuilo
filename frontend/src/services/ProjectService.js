import api from './api';

export default {
    async getProject(collection, slug) {
        try {
            const response = await api.get(`/${collection}/${slug}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching project:', error);
            throw error;
        }
    },

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

    async updateContent(collection, slug, content, metadata = null) {
        try {
            const response = await api.put(`/${collection}/${slug}`, {
                content,
                metadata
            });
            return response.data;
        } catch (error) {
            console.error('Error updating project content:', error);
            throw error;
        }
    },

    async getProjectContent(collection, slug) {
        try {
            const response = await api.get(`/${collection}/${slug}/content`);
            return response.data;
        } catch (error) {
            console.error('Error fetching project content:', error);
            throw error;
        }
    },

    async forgetProject(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/forget`);
            return response.data;
        } catch (error) {
            console.error('Error forgetting project:', error);
            throw error;
        }
    },

    async resurrectProject(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/resurrect`);
            return response.data;
        } catch (error) {
            console.error('Error resurrecting project:', error);
            throw error;
        }
    },

    async revertProject(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/revert`);
            return response.data;
        } catch (error) {
            console.error('Error reverting project:', error);
            throw error;
        }
    },

    async persistDraft(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/persist`);
            return response.data;
        } catch (error) {
            console.error('Error persisting draft:', error);
            throw error;
        }
    },

    async publishProject(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/publish`);
            return response.data;
        } catch (error) {
            console.error('Error publishing project:', error);
            throw error;
        }
    },

    async getTranslation(collection, slug) {
        try {
            const response = await api.get(`/${collection}/${slug}/translate`);
            return response.data;
        } catch (error) {
            console.error('Error fetching translation:', error);
            throw error;
        }
    },

    async updateTranslation(collection, slug, content) {
        try {
            const response = await api.put(`/${collection}/${slug}/translate`, {
                content
            });
            return response.data;
        } catch (error) {
            console.error('Error updating translation:', error);
            throw error;
        }
    },

    async publishTranslation(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/publish-en`);
            return response.data;
        } catch (error) {
            console.error('Error publishing translation:', error);
            throw error;
        }
    }
};

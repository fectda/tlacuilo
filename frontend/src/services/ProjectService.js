import api from './api';

export default {
    /**
     * List all projects across collections.
     */
    async listProjects() {
        try {
            const response = await api.get('/projects/');
            return response.data;
        } catch (error) {
            console.error('Error fetching projects:', error);
            throw error;
        }
    },

    /**
     * Create a new project.
     */
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

    /**
     * Get the markdown content of a project (Working Copy rules).
     */
    async getProjectContent(collection, slug) {
        try {
            const response = await api.get(`/${collection}/${slug}/content`);
            return response.data; // { content: "..." }
        } catch (error) {
            console.error('Error fetching project content:', error);
            throw error;
        }
    },

    /**
     * Persist manual or generated changes to the working copy.
     */
    async persistContent(collection, slug, content) {
        try {
            const response = await api.post(`/${collection}/${slug}/persist`, {
                content
            });
            return response.data;
        } catch (error) {
            console.error('Error persisting content:', error);
            throw error;
        }
    },

    /**
     * Promote the working copy to the portfolio.
     */
    async promoteProject(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/promote`);
            return response.data;
        } catch (error) {
            console.error('Error promoting project:', error);
            throw error;
        }
    },

    /**
     * Forget internal memory.
     */
    async forgetProject(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/forget`);
            return response.data;
        } catch (error) {
            console.error('Error forgetting project:', error);
            throw error;
        }
    },

    /**
     * Resurrect from internal memory.
     */
    async resurrectProject(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/resurrect`);
            return response.data;
        } catch (error) {
            console.error('Error resurrecting project:', error);
            throw error;
        }
    },

    /**
     * Revert working copy to portfolio version.
     */
    async revertProject(collection, slug) {
        try {
            const response = await api.post(`/${collection}/${slug}/revert`);
            return response.data;
        } catch (error) {
            console.error('Error reverting project:', error);
            throw error;
        }
    },

    /**
     * Get the English translation content.
     */
    async getTranslation(collection, slug) {
        try {
            const response = await api.get(`/${collection}/${slug}/translate`);
            return response.data;
        } catch (error) {
            console.error('Error fetching translation:', error);
            throw error;
        }
    },

    /**
     * Persist changes to the English translation.
     */
    async persistTranslation(collection, slug, content) {
        try {
            const response = await api.post(`/${collection}/${slug}/translate/persist`, {
                content
            });
            return response.data;
        } catch (error) {
            console.error('Error persisting translation:', error);
            throw error;
        }
    },

    /**
     * Final publication for English translation (Localization Cycle).
     */
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

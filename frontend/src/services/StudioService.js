import api from './api';

export default {
    // ---- Shot CRUD ----

    async listShots(collection, slug) {
        const response = await api.get(`/${collection}/${slug}/studio/shots`);
        return response.data;
    },

    async suggestShots(collection, slug) {
        const response = await api.post(`/${collection}/${slug}/studio/suggest`);
        return response.data;
    },

    async createShot(collection, slug, payload) {
        const response = await api.post(`/${collection}/${slug}/studio/shots`, payload);
        return response.data;
    },

    async getShot(collection, slug, shotId) {
        const response = await api.get(`/${collection}/${slug}/studio/shots/${shotId}`);
        return response.data;
    },

    async updateShot(collection, slug, shotId, payload) {
        const response = await api.patch(`/${collection}/${slug}/studio/shots/${shotId}`, payload);
        return response.data;
    },

    async deleteShot(collection, slug, shotId) {
        await api.delete(`/${collection}/${slug}/studio/shots/${shotId}`);
    },

    // ---- Generation Pipeline ----

    async uploadAndGenerate(collection, slug, shotId, file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post(
            `/${collection}/${slug}/studio/shots/${shotId}/upload`,
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
        );
        return response.data;
    },

    async correctShot(collection, slug, shotId, instruction) {
        const response = await api.post(
            `/${collection}/${slug}/studio/shots/${shotId}/correct`,
            { instruction }
        );
        return response.data;
    },

    async approveShot(collection, slug, shotId, filename) {
        const response = await api.post(
            `/${collection}/${slug}/studio/shots/${shotId}/approve`,
            { filename }
        );
        return response.data;
    },

    // ---- Utilities ----

    getShotImageUrl(collection, slug, shotId, filename) {
        const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
        return `${base}/${collection}/${slug}/studio/shots/${shotId}/image/${filename}`;
    },

    getOriginalImageUrl(collection, slug, shotId) {
        return this.getShotImageUrl(collection, slug, shotId, 'original.png');
    },
};

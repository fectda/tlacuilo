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

    async uploadAndGenerate(collection, slug, shot_id, file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post(
            `/${collection}/${slug}/studio/shots/${shot_id}/upload`,
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
        );
        return response.data;
    },

    async getShotStatus(collection, slug, shot_id) {
        const response = await api.get(`/${collection}/${slug}/studio/shots/${shot_id}/status`);
        return response.data;
    },

    async correctShot(collection, slug, shot_id, instruction, comfly_id) {
        const response = await api.post(
            `/${collection}/${slug}/studio/shots/${shot_id}/correct`,
            { instruction, comfly_id }
        );
        return response.data;
    },

    async approveShot(collection, slug, shot_id, comfly_id) {
        const response = await api.post(
            `/${collection}/${slug}/studio/shots/${shot_id}/approve`,
            { comfly_id }
        );
        return response.data;
    },

    async deleteImage(collection, slug, shot_id, comfly_id) {
        const response = await api.delete(`/${collection}/${slug}/studio/shots/${shot_id}/image/${comfly_id}`);
        return response.data;
    },

    // ---- Utilities ----

    getShotImageUrl(collection, slug, shot_id, comfly_id) {
        const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
        return `${base}/${collection}/${slug}/studio/shots/${shot_id}/image/${comfly_id}`;
    },

    getOriginalImageUrl(collection, slug, shot_id) {
        // According to section 3.E.2, we have a binary endpoint per comfly_id.
        // We use 'original' as a reserved ID for the base photo.
        return this.getShotImageUrl(collection, slug, shot_id, 'original');
    },
};

import { apiClient } from './apiClient';

const ENDPOINT = '/alerts';

export const alertService = {
  async fetchAll(filters = {}) {
    return apiClient.get(ENDPOINT, filters);
  },

  async fetchById(alertId) {
    return apiClient.get(`${ENDPOINT}/${alertId}`);
  },

  async update(alertId, updates) {
    return apiClient.patch(`${ENDPOINT}/${alertId}`, updates);
  },

  async updateStatus(alertId, status) {
    return apiClient.patch(`${ENDPOINT}/${alertId}`, { status });
  },

  async addNotes(alertId, notes) {
    return apiClient.patch(`${ENDPOINT}/${alertId}`, { investigation_notes: notes });
  },

  async assign(alertId, userId) {
    return apiClient.post(`${ENDPOINT}/${alertId}/assign?user_id=${userId}`);
  },

  async getStats() {
    return apiClient.get(`${ENDPOINT}/stats/summary`);
  },
};

export default alertService;

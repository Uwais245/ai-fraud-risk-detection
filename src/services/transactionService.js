import { apiClient } from './apiClient';

const ENDPOINT = '/transactions';

export const transactionService = {
  async fetchAll(filters = {}) {
    return apiClient.get(ENDPOINT, filters);
  },

  async fetchById(transactionId) {
    return apiClient.get(`${ENDPOINT}/${transactionId}`);
  },

  async search(query, limit = 20) {
    return apiClient.get(`${ENDPOINT}/search`, { q: query, limit });
  },

  async create(transactionData) {
    return apiClient.post(ENDPOINT, transactionData);
  },

  async createBatch(transactions) {
    return apiClient.post(`${ENDPOINT}/batch`, { transactions });
  },

  async update(transactionId, updates) {
    return apiClient.patch(`${ENDPOINT}/${transactionId}`, updates);
  },

  async importCSV(file) {
    return apiClient.uploadFile(`${ENDPOINT}/import/csv`, file);
  },

  async downloadTemplate() {
    const response = await fetch(`${apiClient.baseUrl}${ENDPOINT}/import/csv/template`, {
      headers: apiClient.getHeaders(),
    });
    if (!response.ok) throw new Error('Failed to download template');
    return response.blob();
  },
};

export default transactionService;

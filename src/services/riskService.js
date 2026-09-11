import { apiClient } from './apiClient';

const ENDPOINT = '/risk';

export const riskService = {
  async scoreTransaction(transactionData) {
    return apiClient.post(`${ENDPOINT}/score`, transactionData);
  },

  async scoreBatch(transactions) {
    return apiClient.post(`${ENDPOINT}/batch`, { transactions });
  },

  async getRiskFlags() {
    return apiClient.get(`${ENDPOINT}/flags`);
  },
};

export default riskService;

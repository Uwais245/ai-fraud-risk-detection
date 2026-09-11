import { apiClient } from './apiClient';

const ENDPOINT = '/risk/network';

export const networkService = {
  async getGraph(filters = {}) {
    return apiClient.get(`${ENDPOINT}/graph`, filters);
  },

  async getGraphPost(request) {
    return apiClient.post(`${ENDPOINT}/graph`, request);
  },

  async getClusters(minSize = 3, riskThreshold = 'HIGH') {
    return apiClient.get(`${ENDPOINT}/clusters`, {
      min_size: minSize,
      risk_threshold: riskThreshold,
    });
  },
};

export default networkService;

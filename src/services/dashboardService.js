import { apiClient } from './apiClient';

const ENDPOINT = '/dashboard';

export const dashboardService = {
  async getStats(days = 7) {
    return apiClient.get(`${ENDPOINT}/stats`, { days });
  },

  async getTrends(days = 7, interval = '1d') {
    return apiClient.get(`${ENDPOINT}/trends`, { days, interval });
  },

  async getRiskDistribution() {
    return apiClient.get(`${ENDPOINT}/risk-distribution`);
  },

  async getSuspiciousCustomers(limit = 10) {
    return apiClient.get(`${ENDPOINT}/suspicious-customers`, { limit });
  },

  async getSuspiciousDevices(limit = 10) {
    return apiClient.get(`${ENDPOINT}/suspicious-devices`, { limit });
  },

  async getRecentAlerts(limit = 20, status = null) {
    const params = { limit };
    if (status) params.status = status;
    return apiClient.get(`${ENDPOINT}/alerts`, params);
  },
};

export default dashboardService;

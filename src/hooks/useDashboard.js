import { useState, useCallback } from 'react';
import { dashboardService } from '../services';

export function useDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [trends, setTrends] = useState([]);
  const [riskDistribution, setRiskDistribution] = useState(null);
  const [suspiciousCustomers, setSuspiciousCustomers] = useState([]);
  const [suspiciousDevices, setSuspiciousDevices] = useState([]);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDashboardData = useCallback(async (days = 7) => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardService.getStats(days);
      setDashboardData(data);
      setTrends(data.trends?.trends || []);
      setRiskDistribution(data.risk_distribution);
      setSuspiciousCustomers(data.suspicious_customers?.customers || []);
      setSuspiciousDevices(data.suspicious_devices?.devices || []);
      setRecentAlerts(data.recent_alerts?.alerts || []);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchTrends = useCallback(async (days = 7) => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardService.getTrends(days);
      setTrends(data.trends || []);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchRiskDistribution = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardService.getRiskDistribution();
      setRiskDistribution(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSuspiciousCustomers = useCallback(async (limit = 10) => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardService.getSuspiciousCustomers(limit);
      setSuspiciousCustomers(data.customers || []);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSuspiciousDevices = useCallback(async (limit = 10) => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardService.getSuspiciousDevices(limit);
      setSuspiciousDevices(data.devices || []);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchRecentAlerts = useCallback(async (limit = 20) => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardService.getRecentAlerts(limit);
      setRecentAlerts(data.alerts || []);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    dashboardData,
    trends,
    riskDistribution,
    suspiciousCustomers,
    suspiciousDevices,
    recentAlerts,
    loading,
    error,
    fetchDashboardData,
    fetchTrends,
    fetchRiskDistribution,
    fetchSuspiciousCustomers,
    fetchSuspiciousDevices,
    fetchRecentAlerts,
  };
}

export default useDashboard;

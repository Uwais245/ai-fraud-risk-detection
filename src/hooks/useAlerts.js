import { useState, useCallback } from 'react';
import { alertService } from '../services';

export function useAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    perPage: 20,
    totalPages: 0,
  });

  const fetchAlerts = useCallback(async (filters = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await alertService.fetchAll(filters);
      setAlerts(response.alerts || []);
      setPagination({
        total: response.total || 0,
        page: response.page || 1,
        perPage: response.per_page || 20,
        totalPages: response.total_pages || 0,
      });
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchAlertById = useCallback(async (alertId) => {
    setLoading(true);
    setError(null);
    try {
      const alert = await alertService.fetchById(alertId);
      return alert;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateAlertStatus = useCallback(async (alertId, status) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await alertService.updateStatus(alertId, status);
      setAlerts(prev => 
        prev.map(a => a.id === alertId ? updated : a)
      );
      return updated;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const addAlertNotes = useCallback(async (alertId, notes) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await alertService.addNotes(alertId, notes);
      setAlerts(prev => 
        prev.map(a => a.id === alertId ? updated : a)
      );
      return updated;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const assignAlert = useCallback(async (alertId, userId) => {
    setLoading(true);
    setError(null);
    try {
      const result = await alertService.assign(alertId, userId);
      if (result.alert) {
        setAlerts(prev => 
          prev.map(a => a.id === alertId ? result.alert : a)
        );
      }
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const statsData = await alertService.getStats();
      setStats(statsData);
      return statsData;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    alerts,
    loading,
    error,
    stats,
    pagination,
    fetchAlerts,
    fetchAlertById,
    updateAlertStatus,
    addAlertNotes,
    assignAlert,
    fetchStats,
    clearError,
  };
}

export default useAlerts;

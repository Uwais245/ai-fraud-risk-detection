import { useState, useCallback } from 'react';
import { networkService } from '../services';

export function useNetwork() {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchGraph = useCallback(async (filters = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await networkService.getGraph(filters);
      setGraphData(data || { nodes: [], edges: [] });
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchGraphPost = useCallback(async (request) => {
    setLoading(true);
    setError(null);
    try {
      const data = await networkService.getGraphPost(request);
      setGraphData(data || { nodes: [], edges: [] });
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchClusters = useCallback(async (minSize = 3, riskThreshold = 'HIGH') => {
    setLoading(true);
    setError(null);
    try {
      const data = await networkService.getClusters(minSize, riskThreshold);
      setClusters(data.clusters || []);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchGraphByCustomer = useCallback(async (customerId, depth = 2) => {
    return fetchGraph({ customer_id: customerId, depth });
  }, [fetchGraph]);

  const fetchGraphByTransaction = useCallback(async (transactionId, depth = 2) => {
    return fetchGraph({ transaction_id: transactionId, depth });
  }, [fetchGraph]);

  const fetchGraphByDevice = useCallback(async (deviceId, depth = 2) => {
    return fetchGraph({ device_id: deviceId, depth });
  }, [fetchGraph]);

  return {
    graphData,
    clusters,
    loading,
    error,
    fetchGraph,
    fetchGraphPost,
    fetchClusters,
    fetchGraphByCustomer,
    fetchGraphByTransaction,
    fetchGraphByDevice,
  };
}

export default useNetwork;

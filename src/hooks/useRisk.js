import { useState, useCallback } from 'react';
import { riskService } from '../services';

export function useRisk() {
  const [riskResult, setRiskResult] = useState(null);
  const [riskFlags, setRiskFlags] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const scoreTransaction = useCallback(async (transactionData) => {
    setLoading(true);
    setError(null);
    try {
      const result = await riskService.scoreTransaction(transactionData);
      setRiskResult(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const scoreBatch = useCallback(async (transactions) => {
    setLoading(true);
    setError(null);
    try {
      const results = await riskService.scoreBatch(transactions);
      return results;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchRiskFlags = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await riskService.getRiskFlags();
      setRiskFlags(data.flags || []);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    riskResult,
    riskFlags,
    loading,
    error,
    scoreTransaction,
    scoreBatch,
    fetchRiskFlags,
  };
}

export default useRisk;

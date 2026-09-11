import { useState, useCallback } from 'react';
import { transactionService } from '../services';

export function useTransactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    perPage: 20,
    totalPages: 0,
  });

  const fetchTransactions = useCallback(async (filters = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await transactionService.fetchAll(filters);
      setTransactions(response.transactions || []);
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

  const searchTransactions = useCallback(async (query, limit = 20) => {
    setLoading(true);
    setError(null);
    try {
      const results = await transactionService.search(query, limit);
      setTransactions(results || []);
      return results;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchTransactionById = useCallback(async (transactionId) => {
    setLoading(true);
    setError(null);
    try {
      const transaction = await transactionService.fetchById(transactionId);
      return transaction;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createTransaction = useCallback(async (transactionData) => {
    setLoading(true);
    setError(null);
    try {
      const newTransaction = await transactionService.create(transactionData);
      setTransactions(prev => [newTransaction, ...prev]);
      return newTransaction;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateTransaction = useCallback(async (transactionId, updates) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await transactionService.update(transactionId, updates);
      setTransactions(prev => 
        prev.map(t => t.transaction_id === transactionId ? updated : t)
      );
      return updated;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const importCSV = useCallback(async (file) => {
    setLoading(true);
    setError(null);
    try {
      const result = await transactionService.importCSV(file);
      return result;
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
    transactions,
    loading,
    error,
    pagination,
    fetchTransactions,
    searchTransactions,
    fetchTransactionById,
    createTransaction,
    updateTransaction,
    importCSV,
    clearError,
  };
}

export default useTransactions;

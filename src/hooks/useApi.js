import { useState, useCallback, useEffect, useRef } from 'react';

export function useApi(apiFunction, immediate = false, initialParams = null) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const apiFunctionRef = useRef(apiFunction);
  
  useEffect(() => {
    apiFunctionRef.current = apiFunction;
  }, [apiFunction]);

  const execute = useCallback(async (params) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFunctionRef.current(params);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (immediate && initialParams !== null) {
      const runAsync = async () => {
        try {
          await execute(initialParams);
        } catch {
          // Error already handled by execute
        }
      };
      runAsync();
    }
  }, [immediate, initialParams, execute]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    data,
    loading,
    error,
    execute,
    reset,
    setData,
  };
}

export default useApi;

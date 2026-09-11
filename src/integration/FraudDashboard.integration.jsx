import React, { useEffect, useState } from 'react';
import { useDashboard, useTransactions, useAlerts, useNetwork } from '../hooks';
import FraudDashboard from '../FraudDashboard';

export function FraudDashboardIntegration() {
  const {
    dashboardData,
    trends,
    riskDistribution,
    suspiciousCustomers,
    suspiciousDevices,
    recentAlerts,
    loading: dashboardLoading,
    error: dashboardError,
    fetchDashboardData,
  } = useDashboard();

  const {
    transactions,
    loading: txLoading,
    error: txError,
    fetchTransactions,
    searchTransactions,
    pagination,
  } = useTransactions();

  const {
    alerts,
    loading: alertsLoading,
    error: alertsError,
    fetchAlerts,
    updateAlertStatus,
  } = useAlerts();

  const {
    graphData,
    loading: networkLoading,
    fetchGraph,
  } = useNetwork();

  const [searchQuery, setSearchQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState('All');

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([
        fetchDashboardData(14),
        fetchAlerts({ per_page: 20 }),
        fetchGraph({ depth: 2, limit: 200 }),
      ]);
    };
    loadData();
  }, [fetchDashboardData, fetchAlerts, fetchGraph]);

  useEffect(() => {
    fetchTransactions({
      page: 1,
      per_page: 20,
      risk_level: riskFilter !== 'All' ? riskFilter.toUpperCase() : undefined,
    });
  }, [riskFilter, fetchTransactions]);

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.length > 2) {
      await searchTransactions(query);
    } else if (query.length === 0) {
      await fetchTransactions({ page: 1, per_page: 20 });
    }
  };

  const handleFilterChange = (filter) => {
    setRiskFilter(filter);
  };

  const handleAlertStatusUpdate = async (alertId, newStatus) => {
    await updateAlertStatus(alertId, newStatus);
    await fetchAlerts({ per_page: 20 });
  };

  if (dashboardLoading || txLoading || alertsLoading || networkLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (dashboardError || txError || alertsError) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-red-500">
          Error: {dashboardError || txError || alertsError}
        </div>
      </div>
    );
  }

  return (
    <FraudDashboard
      dashboardData={dashboardData}
      trends={trends}
      riskDistribution={riskDistribution}
      suspiciousCustomers={suspiciousCustomers}
      suspiciousDevices={suspiciousDevices}
      recentAlerts={recentAlerts}
      transactions={transactions}
      alerts={alerts}
      networkData={graphData}
      pagination={pagination}
      searchQuery={searchQuery}
      riskFilter={riskFilter}
      onSearch={handleSearch}
      onFilterChange={handleFilterChange}
      onAlertStatusUpdate={handleAlertStatusUpdate}
    />
  );
}

export default FraudDashboardIntegration;

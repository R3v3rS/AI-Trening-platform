import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getProfile } from '../lib/api/profile';
import { getLoadMetrics } from '../lib/api/metrics';
import StatCard from '../components/StatCard/StatCard';
import styles from './DashboardPage.module.css';

const DashboardPage: React.FC = () => {
  const {
    data: profile,
    isLoading: isLoadingProfile,
    error: profileError,
  } = useQuery({
    queryKey: ['profile'],
    queryFn: getProfile,
  });

  const {
    data: metrics,
    isLoading: isLoadingMetrics,
    error: metricsError,
  } = useQuery({
    queryKey: ['metrics', 'today', 'today'], // Przykładowe daty
    queryFn: () => getLoadMetrics('today', 'today'),
  });

  if (isLoadingProfile || isLoadingMetrics) {
    return <div className={styles.loading}>Ładowanie...</div>;
  }

  if (profileError || metricsError) {
    return (
      <div className={styles.error}>
        Błąd pobierania danych:{' '}
        {profileError?.message || metricsError?.message}
      </div>
    );
  }

  // Wyszukaj najnowszy element z tablicy metrics
  const latestMetric = metrics && metrics.length > 0 
    ? [...metrics].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())[0] 
    : null;

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Dashboard</h1>
      
      <div className={styles.grid}>
        <StatCard label="FTP" value={profile?.ftp || 0} unit="W" color="var(--primary-color)" />
        <StatCard label="Waga" value={profile?.weight || 0} unit="kg" />
        <StatCard label="HR Max" value={profile?.hr_max || 0} unit="bpm" color="var(--danger-color)" />
        <StatCard label="CTL (Fitness)" value={latestMetric?.ctl || 0} color="var(--primary-color)" />
        <StatCard label="ATL (Fatigue)" value={latestMetric?.atl || 0} color="var(--danger-color)" />
        <StatCard 
          label="TSB (Form)" 
          value={latestMetric?.tsb || 0} 
          color={(latestMetric?.tsb || 0) > 0 ? 'var(--success-color)' : 'var(--warning-color)'} 
        />
      </div>
    </div>
  );
};

export default DashboardPage;

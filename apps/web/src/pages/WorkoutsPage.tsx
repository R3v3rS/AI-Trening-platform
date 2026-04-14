import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getWorkouts } from '../lib/api/workouts';
import { WorkoutType, WorkoutStatus, GetWorkoutsParams } from '../types';
import { formatDate } from '../utils/dateFormatter';
import styles from './WorkoutsPage.module.css';

const WorkoutsPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [typeFilter, setTypeFilter] = useState<WorkoutType | ''>('');
  const [statusFilter, setStatusFilter] = useState<WorkoutStatus | ''>('');
  
  const limit = 10;

  const queryParams: GetWorkoutsParams = {
    page,
    limit,
    ...(typeFilter && { type: typeFilter }),
    ...(statusFilter && { status: statusFilter }),
  };

  const {
    data: paginatedData,
    isLoading,
    error,
    isPlaceholderData,
  } = useQuery({
    queryKey: ['workouts', queryParams],
    queryFn: () => getWorkouts(queryParams),
    placeholderData: (previousData) => previousData,
  });

  const getStatusClass = (status: WorkoutStatus) => {
    switch (status) {
      case WorkoutStatus.COMPLETED:
        return styles.statusCompleted;
      case WorkoutStatus.PLANNED:
        return styles.statusPlanned;
      case WorkoutStatus.MISSED:
        return styles.statusMissed;
      default:
        return '';
    }
  };

  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTypeFilter(e.target.value as WorkoutType | '');
    setPage(1); // Reset na pierwszą stronę po zmianie filtru
  };

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value as WorkoutStatus | '');
    setPage(1);
  };

  const totalPages = paginatedData ? Math.ceil(paginatedData.total / limit) : 0;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Workouts</h1>
      </div>

      <div className={styles.filters}>
        <div className={styles.filterGroup}>
          <label className={styles.filterLabel} htmlFor="type-filter">Typ:</label>
          <select 
            id="type-filter" 
            className={styles.select}
            value={typeFilter}
            onChange={handleTypeChange}
          >
            <option value="">Wszystkie</option>
            {Object.values(WorkoutType).map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel} htmlFor="status-filter">Status:</label>
          <select 
            id="status-filter" 
            className={styles.select}
            value={statusFilter}
            onChange={handleStatusChange}
          >
            <option value="">Wszystkie</option>
            {Object.values(WorkoutStatus).map(status => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
        </div>
      </div>

      {error ? (
        <div className={styles.error}>Błąd pobierania treningów: {error.message}</div>
      ) : isLoading ? (
        <div className={styles.loading}>Ładowanie treningów...</div>
      ) : paginatedData?.data.length === 0 ? (
        <div className={styles.emptyState}>
          Nie znaleziono żadnych treningów spełniających kryteria.
        </div>
      ) : (
        <>
          <div className={styles.list}>
            {paginatedData?.data.map((workout) => (
              <div key={workout.id} className={styles.workoutItem}>
                <div className={styles.workoutDetails}>
                  <span className={styles.workoutDate}>{formatDate(workout.date)}</span>
                  <span className={styles.workoutTitle}>{workout.title || workout.type}</span>
                  <div className={styles.workoutMeta}>
                    <span>{workout.duration} min</span>
                    <span>{workout.type}</span>
                  </div>
                </div>
                <div className={`${styles.workoutStatus} ${getStatusClass(workout.status)}`}>
                  {workout.status}
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className={styles.pagination}>
              <button 
                className={styles.pageButton}
                onClick={() => setPage(old => Math.max(old - 1, 1))}
                disabled={page === 1 || isPlaceholderData}
              >
                Poprzednia
              </button>
              <span className={styles.pageInfo}>
                Strona {page} z {totalPages}
              </span>
              <button 
                className={styles.pageButton}
                onClick={() => setPage(old => Math.min(old + 1, totalPages))}
                disabled={page === totalPages || isPlaceholderData}
              >
                Następna
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default WorkoutsPage;

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getCalendar } from '../lib/api/calendar';
import { WorkoutStatus } from '../types';
import styles from './CalendarPage.module.css';

const CalendarPage: React.FC = () => {
  const from = '2023-10-01'; // Przykładowe daty (zwykle użyłoby się np. date-fns)
  const to = '2023-10-31';

  const {
    data: workouts,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['calendar', from, to],
    queryFn: () => getCalendar(from, to),
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

  if (isLoading) {
    return <div className={styles.loading}>Ładowanie kalendarza...</div>;
  }

  if (error) {
    return <div className={styles.error}>Błąd pobierania kalendarza: {error.message}</div>;
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Calendar</h1>
      <div className={styles.list}>
        {workouts && workouts.length > 0 ? (
          workouts.map((workout) => (
            <div key={workout.id} className={styles.workoutItem}>
              <div className={styles.workoutDetails}>
                <span className={styles.workoutDate}>{new Date(workout.date).toLocaleDateString()}</span>
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
          ))
        ) : (
          <div className={styles.loading}>Brak zaplanowanych treningów na ten miesiąc.</div>
        )}
      </div>
    </div>
  );
};

export default CalendarPage;

import React from 'react';
import styles from './WorkoutsPage.module.css';

const WorkoutsPage: React.FC = () => {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Workouts</h1>
      <div className={styles.placeholderBox}>
        Tu będzie lista wszystkich treningów (wkrótce)
      </div>
    </div>
  );
};

export default WorkoutsPage;

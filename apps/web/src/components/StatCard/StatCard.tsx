import React from 'react';
import styles from './StatCard.module.css';

interface StatCardProps {
  label: string;
  value: number | string;
  unit?: string;
  color?: string;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, unit, color }) => {
  return (
    <div className={styles.card}>
      <span className={styles.label}>{label}</span>
      <div className={styles.valueContainer}>
        <span className={styles.value} style={{ color: color || 'var(--text-primary)' }}>
          {value}
        </span>
        {unit && <span className={styles.unit}>{unit}</span>}
      </div>
    </div>
  );
};

export default StatCard;

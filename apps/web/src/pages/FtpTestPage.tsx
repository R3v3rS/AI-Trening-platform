import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { submitManualFtpTest, acceptFtpTest, FtpTestResult } from '../lib/api/ftp';
import styles from './FtpTestPage.module.css';

const FtpTestPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [protocol, setProtocol] = useState<string>('20min');
  const [avgPower, setAvgPower] = useState<number>(0);
  const [testResult, setTestResult] = useState<FtpTestResult | null>(null);
  const [accepted, setAccepted] = useState(false);

  const calculateMutation = useMutation({
    mutationFn: () => submitManualFtpTest(protocol, avgPower),
    onSuccess: (data) => {
      setTestResult(data);
      setAccepted(false);
    },
  });

  const acceptMutation = useMutation({
    mutationFn: () => acceptFtpTest(testResult?.test_id || ''),
    onSuccess: () => {
      setAccepted(true);
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });

  const handleCalculate = (e: React.FormEvent) => {
    e.preventDefault();
    calculateMutation.mutate();
  };

  const handleAccept = () => {
    if (testResult) {
      acceptMutation.mutate();
    }
  };

  const handleReset = () => {
    setTestResult(null);
    setAccepted(false);
    setAvgPower(0);
    calculateMutation.reset();
    acceptMutation.reset();
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Wprowadź wynik testu FTP</h1>

      {accepted && (
        <div className={styles.success}>
          Nowe FTP zostało zaakceptowane i zaktualizowane w Twoim profilu!
        </div>
      )}

      {calculateMutation.isError && (
        <div className={styles.error}>
          Błąd obliczeń: {calculateMutation.error.message}
        </div>
      )}

      {acceptMutation.isError && (
        <div className={styles.error}>
          Błąd zapisu: {acceptMutation.error.message}
        </div>
      )}

      <div className={styles.card}>
        <form onSubmit={handleCalculate} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className={styles.formGroup}>
            <label className={styles.label} htmlFor="protocol">Protokół testowy</label>
            <select
              id="protocol"
              className={styles.input}
              value={protocol}
              onChange={(e) => setProtocol(e.target.value)}
              disabled={!!testResult}
              required
            >
              <option value="20min">20 minut (95% średniej mocy)</option>
              <option value="ramp">Ramp Test (75% mocy z ostatniej minuty)</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label} htmlFor="avgPower">Średnia moc (W)</label>
            <input
              id="avgPower"
              type="number"
              className={styles.input}
              value={avgPower || ''}
              onChange={(e) => setAvgPower(Number(e.target.value))}
              disabled={!!testResult}
              required
            />
          </div>

          {!testResult && (
            <button 
              type="submit" 
              className={styles.button}
              disabled={calculateMutation.isPending || avgPower <= 0}
            >
              {calculateMutation.isPending ? 'Obliczanie...' : 'Oblicz sugerowane FTP'}
            </button>
          )}
        </form>

        {testResult && (
          <div className={styles.resultBox}>
            <span className={styles.resultTitle}>Sugerowane FTP</span>
            <span className={styles.resultValue}>{testResult.suggested_ftp} W</span>
            
            {!accepted && (
              <div className={styles.resultActions}>
                <button 
                  className={`${styles.button} ${styles.buttonSecondary}`} 
                  onClick={handleReset}
                  disabled={acceptMutation.isPending}
                >
                  Odrzuć / Spróbuj ponownie
                </button>
                <button 
                  className={styles.button} 
                  onClick={handleAccept}
                  disabled={acceptMutation.isPending}
                >
                  {acceptMutation.isPending ? 'Zapisywanie...' : 'Zapisz i aktualizuj profil'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FtpTestPage;

import React, { useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getProfile, updateProfile } from '../lib/api/profile';
import { Profile, ProfileSchema } from '../types';
import styles from './ProfilePage.module.css';

const ProfilePage: React.FC = () => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<Record<string, string | number>>({
    ftp: '',
    weight: '',
    hr_max: '',
    hr_threshold: '',
    experience_level: '',
    weekly_hours: '',
  });
  const [validationError, setValidationError] = useState<string | null>(null);

  const { data: profile, isLoading, error: fetchError } = useQuery({
    queryKey: ['profile'],
    queryFn: getProfile,
  });

  useEffect(() => {
    if (profile) {
      setFormData(profile);
    }
  }, [profile]);

  const mutation = useMutation({
    mutationFn: (data: Partial<Profile>) => updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      setValidationError(null);
    },
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? '' : Number(value)) : value,
    }));
    setValidationError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const result = ProfileSchema.safeParse(formData);
    
    if (!result.success) {
      setValidationError(result.error.errors[0].message);
      return;
    }

    mutation.mutate(result.data);
  };

  if (isLoading) {
    return <div className={styles.loading}>Ładowanie profilu...</div>;
  }

  if (fetchError) {
    return <div className={styles.error}>Błąd ładowania profilu: {fetchError.message}</div>;
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Profile</h1>
      
      {mutation.isSuccess && (
        <div className={styles.success}>Profil został zaktualizowany!</div>
      )}
      
      {validationError && (
        <div className={styles.error}>Błąd walidacji: {validationError}</div>
      )}

      {mutation.isError && (
        <div className={styles.error}>Błąd aktualizacji: {mutation.error.message}</div>
      )}

      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="ftp">FTP (W)</label>
          <input
            id="ftp"
            name="ftp"
            type="number"
            className={styles.input}
            value={formData.ftp ?? ''}
            onChange={handleChange}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="weight">Waga (kg)</label>
          <input
            id="weight"
            name="weight"
            type="number"
            className={styles.input}
            value={formData.weight ?? ''}
            onChange={handleChange}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="hr_max">HR Max (bpm)</label>
          <input
            id="hr_max"
            name="hr_max"
            type="number"
            className={styles.input}
            value={formData.hr_max ?? ''}
            onChange={handleChange}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="hr_threshold">Próg HR (bpm)</label>
          <input
            id="hr_threshold"
            name="hr_threshold"
            type="number"
            className={styles.input}
            value={formData.hr_threshold ?? ''}
            onChange={handleChange}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="experience_level">Poziom doświadczenia</label>
          <select
            id="experience_level"
            name="experience_level"
            className={styles.input}
            value={formData.experience_level ?? ''}
            onChange={handleChange}
            required
          >
            <option value="" disabled>Wybierz poziom</option>
            <option value="beginner">Początkujący</option>
            <option value="intermediate">Średniozaawansowany</option>
            <option value="advanced">Zaawansowany</option>
            <option value="pro">Pro</option>
          </select>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="weekly_hours">Tygodniowe godziny treningu</label>
          <input
            id="weekly_hours"
            name="weekly_hours"
            type="number"
            className={styles.input}
            value={formData.weekly_hours ?? ''}
            onChange={handleChange}
            required
          />
        </div>

        <button 
          type="submit" 
          className={styles.button}
          disabled={mutation.isPending}
        >
          {mutation.isPending ? 'Zapisywanie...' : 'Zapisz profil'}
        </button>
      </form>
    </div>
  );
};

export default ProfilePage;

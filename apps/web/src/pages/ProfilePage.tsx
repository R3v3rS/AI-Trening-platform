import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useState, useEffect } from 'react';

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      try {
        const res = await api.get('/profile');
        return res.data;
      } catch (err: any) {
        if (err.response?.status === 404) return null;
        throw err;
      }
    }
  });

  const [formData, setFormData] = useState({
    ftp_watts: '',
    weight_kg: '',
    hr_max: '',
    hr_threshold: '',
    experience_level: 'intermediate',
    indoor_vs_outdoor_preference: 'mixed'
  });

  useEffect(() => {
    if (profile) {
      setFormData({
        ftp_watts: profile.ftp_watts || '',
        weight_kg: profile.weight_kg || '',
        hr_max: profile.hr_max || '',
        hr_threshold: profile.hr_threshold || '',
        experience_level: profile.experience_level || 'intermediate',
        indoor_vs_outdoor_preference: profile.indoor_vs_outdoor_preference || 'mixed'
      });
    }
  }, [profile]);

  const mutation = useMutation({
    mutationFn: (newProfile: any) => api.put('/profile', newProfile),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      alert('Zapisano profil!');
    },
    onError: () => {
      alert('Błąd podczas zapisywania profilu.');
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      ftp_watts: Number(formData.ftp_watts),
      weight_kg: Number(formData.weight_kg),
      hr_max: Number(formData.hr_max),
      hr_threshold: Number(formData.hr_threshold),
      experience_level: formData.experience_level,
      indoor_vs_outdoor_preference: formData.indoor_vs_outdoor_preference
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  if (isLoading) {
    return <div className="text-center py-12 animate-pulse text-muted-foreground">Wczytywanie profilu...</div>;
  }

  return (
    <div className="bg-card p-8 rounded-lg border border-border shadow-sm max-w-2xl mx-auto">
      <h2 className="font-heading text-3xl font-bold mb-8 text-foreground">Profil Kolarza</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">FTP (Waty)</label>
            <input 
              type="number" 
              name="ftp_watts"
              value={formData.ftp_watts}
              onChange={handleChange}
              className="w-full bg-background border border-border rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              required 
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Waga (kg)</label>
            <input 
              type="number" 
              name="weight_kg"
              step="0.1"
              value={formData.weight_kg}
              onChange={handleChange}
              className="w-full bg-background border border-border rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              required 
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Tętno Maksymalne (BPM)</label>
            <input 
              type="number" 
              name="hr_max"
              value={formData.hr_max}
              onChange={handleChange}
              className="w-full bg-background border border-border rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              required 
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Tętno Progowe (BPM)</label>
            <input 
              type="number" 
              name="hr_threshold"
              value={formData.hr_threshold}
              onChange={handleChange}
              className="w-full bg-background border border-border rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
              required 
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Poziom zaawansowania</label>
            <select 
              name="experience_level"
              value={formData.experience_level}
              onChange={handleChange}
              className="w-full bg-background border border-border rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="beginner">Początkujący</option>
              <option value="intermediate">Średniozaawansowany</option>
              <option value="advanced">Zaawansowany</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Środowisko</label>
            <select 
              name="indoor_vs_outdoor_preference"
              value={formData.indoor_vs_outdoor_preference}
              onChange={handleChange}
              className="w-full bg-background border border-border rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="indoor">Głównie Trenażer (Indoor)</option>
              <option value="outdoor">Głównie Szosa (Outdoor)</option>
              <option value="mixed">Mieszane</option>
            </select>
          </div>
        </div>

        <div className="pt-4">
          <button 
            type="submit" 
            disabled={mutation.isPending}
            className="w-full md:w-auto px-8 py-3 bg-z5 hover:bg-z5/90 text-white font-bold rounded-md transition-colors disabled:opacity-50 uppercase tracking-wider"
          >
            {mutation.isPending ? 'Zapisywanie...' : 'Zapisz Profil'}
          </button>
        </div>
      </form>
    </div>
  );
}
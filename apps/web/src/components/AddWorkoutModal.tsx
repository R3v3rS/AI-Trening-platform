import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { PlusCircle } from 'lucide-react';
import * as Dialog from '@radix-ui/react-dialog';

export function AddWorkoutModal({ date, isOpen, onOpenChange }: { date: string, isOpen: boolean, onOpenChange: (open: boolean) => void }) {
  const queryClient = useQueryClient();
  const [type, setType] = useState('z2');
  const [duration, setDuration] = useState('60');
  const [notes, setNotes] = useState('');

  const mutation = useMutation({
    mutationFn: async () => {
      const payload = {
        planned_date: date,
        type,
        duration_sec: Number(duration) * 60,
        notes
      };
      await api.post('/planned-workouts', payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar'] });
      onOpenChange(false);
      // reset form
      setType('z2');
      setDuration('60');
      setNotes('');
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate();
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border border-border bg-card p-6 shadow-lg sm:rounded-lg">
          <Dialog.Title className="text-lg font-bold font-heading">
            Zaplanuj trening na {date}
          </Dialog.Title>
          
          <form onSubmit={handleSubmit} className="space-y-4 mt-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Typ Treningu</label>
              <select 
                value={type} 
                onChange={e => setType(e.target.value)}
                className="w-full bg-background border border-border rounded-md px-3 py-2"
              >
                <option value="recovery">Aktywna Regeneracja (Recovery)</option>
                <option value="z2">Baza Tlenowa (Z2)</option>
                <option value="tempo">Tempo (Z3)</option>
                <option value="vo2max">Interwały VO2Max</option>
                <option value="long_ride">Długa Jazda (Long Ride)</option>
                <option value="ftp_test">Test FTP</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Czas trwania (minuty)</label>
              <input 
                type="number" 
                value={duration} 
                onChange={e => setDuration(e.target.value)}
                min="10"
                step="5"
                className="w-full bg-background border border-border rounded-md px-3 py-2"
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Notatki dla siebie / trenera</label>
              <textarea 
                value={notes} 
                onChange={e => setNotes(e.target.value)}
                className="w-full bg-background border border-border rounded-md px-3 py-2 min-h-[80px]"
                placeholder="Np. skupić się na kadencji powyżej 90 RPM"
              />
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-border mt-6">
              <button 
                type="button" 
                onClick={() => onOpenChange(false)}
                className="px-4 py-2 border border-border rounded hover:bg-muted transition-colors"
              >
                Anuluj
              </button>
              <button 
                type="submit"
                disabled={mutation.isPending}
                className="px-4 py-2 bg-z5 hover:bg-z5/90 text-white rounded font-medium disabled:opacity-50"
              >
                {mutation.isPending ? 'Zapisywanie...' : 'Zaplanuj'}
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
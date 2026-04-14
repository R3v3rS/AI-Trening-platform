import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { format, subMonths, addMonths } from 'date-fns';

export default function WorkoutsPage() {
  const currentDate = new Date();
  const fromDate = format(subMonths(currentDate, 3), 'yyyy-MM-dd');
  const toDate = format(addMonths(currentDate, 1), 'yyyy-MM-dd');

  const { data: workouts, isLoading } = useQuery({
    queryKey: ['workouts', fromDate, toDate],
    queryFn: async () => {
      const res = await api.get(`/workouts?from=${fromDate}&to=${toDate}`);
      return res.data;
    }
  });

  return (
    <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
      <h2 className="font-heading text-2xl font-bold mb-6">Historia Treningów</h2>
      
      {isLoading ? (
        <div className="flex items-center justify-center p-12 text-muted-foreground animate-pulse">
          Ładowanie historii...
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs uppercase bg-muted text-muted-foreground">
              <tr>
                <th className="px-6 py-3">Data</th>
                <th className="px-6 py-3">Źródło</th>
                <th className="px-6 py-3">Czas (min)</th>
                <th className="px-6 py-3">TSS</th>
                <th className="px-6 py-3">NP (W)</th>
                <th className="px-6 py-3">Śr. Moc (W)</th>
                <th className="px-6 py-3">IF</th>
              </tr>
            </thead>
            <tbody>
              {workouts?.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-muted-foreground">
                    Brak wykonanych treningów w wybranym okresie.
                  </td>
                </tr>
              ) : (
                workouts?.map((w: any) => (
                  <tr key={w.id} className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="px-6 py-4 font-medium whitespace-nowrap">
                      {format(new Date(w.started_at), 'yyyy-MM-dd HH:mm')}
                    </td>
                    <td className="px-6 py-4 capitalize">{w.source}</td>
                    <td className="px-6 py-4">{Math.round(w.duration_sec / 60)}</td>
                    <td className="px-6 py-4 font-bold text-z5">{Math.round(w.tss || 0)}</td>
                    <td className="px-6 py-4 text-z2 font-semibold">{Math.round(w.np_power || 0)}</td>
                    <td className="px-6 py-4">{Math.round(w.avg_power || 0)}</td>
                    <td className="px-6 py-4">{(w.if_value || 0).toFixed(2)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Trash2, Dumbbell } from 'lucide-react';

export default function TemplatesPage() {
  const queryClient = useQueryClient();

  const { data: templates, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: async () => {
      const res = await api.get('/templates');
      return res.data;
    }
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/templates/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    }
  });

  return (
    <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
      <h2 className="font-heading text-2xl font-bold mb-6">Baza Treningów (Szablony)</h2>
      
      {isLoading ? (
        <div className="flex items-center justify-center p-12 text-muted-foreground animate-pulse">
          Ładowanie szablonów...
        </div>
      ) : templates?.length === 0 ? (
        <div className="text-center p-12 border-2 border-dashed border-border rounded-lg text-muted-foreground">
          Brak zapisanych szablonów. Możesz stworzyć szablon podczas dodawania nowego treningu w Kalendarzu.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates?.map((t: any) => {
            let stepsCount = 0;
            if (t.structured_steps) {
              try {
                stepsCount = JSON.parse(t.structured_steps).length;
              } catch (e) {}
            }
            
            return (
              <div key={t.id} className="bg-background border border-border rounded-lg p-5 flex flex-col hover:border-z5/50 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-lg text-foreground truncate" title={t.name}>{t.name}</h3>
                  <button 
                    onClick={() => {
                      if (window.confirm('Czy na pewno chcesz usunąć ten szablon?')) {
                        deleteMutation.mutate(t.id);
                      }
                    }}
                    className="text-muted-foreground hover:text-destructive transition-colors"
                    title="Usuń szablon"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="text-sm text-muted-foreground mb-4 flex-1">
                  <p className="mb-2 line-clamp-2">{t.description || 'Brak opisu.'}</p>
                  <div className="flex gap-2 items-center">
                    <span className="bg-muted px-2 py-1 rounded text-xs font-medium uppercase">{t.type}</span>
                    {stepsCount > 0 && (
                      <span className="flex items-center gap-1 text-xs text-z5 font-medium">
                        <Dumbbell className="w-3 h-3" /> {stepsCount} kroków
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { format, subMonths, addMonths } from 'date-fns';
import { useState } from 'react';
import { AddWorkoutModal } from '../components/AddWorkoutModal';
import * as Dialog from '@radix-ui/react-dialog';
import { Download, CheckCircle, XCircle, MoveRight } from 'lucide-react';

export default function CalendarPage() {
  const queryClient = useQueryClient();
  const [currentDate, setCurrentDate] = useState(new Date());
  
  // Modal states
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [selectedDateStr, setSelectedDateStr] = useState<string>('');
  
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<any>(null);

  const fromDate = format(subMonths(currentDate, 1), 'yyyy-MM-dd');
  const toDate = format(addMonths(currentDate, 1), 'yyyy-MM-dd');

  const { data, isLoading } = useQuery({
    queryKey: ['calendar', fromDate, toDate],
    queryFn: async () => {
      const res = await api.get(`/calendar?from=${fromDate}&to=${toDate}`);
      return res.data;
    }
  });

  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: number, status: string }) => {
      await api.patch(`/planned-workouts/${id}/status`, { status });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar'] });
      setDetailsModalOpen(false);
    }
  });

  const handleDateClick = (arg: any) => {
    setSelectedDateStr(arg.dateStr);
    setAddModalOpen(true);
  };

  const handleEventClick = (arg: any) => {
    setSelectedEvent(arg.event.extendedProps);
    setDetailsModalOpen(true);
  };

  const downloadZwo = (id: number) => {
    window.open(`/api/v1/planned-workouts/${id}/export/zwo`, '_blank');
  };

  const events = data ? [
    ...data.completed.map((w: any) => ({
      id: `w-${w.id}`,
      title: `Trening (${Math.round(w.duration_sec / 60)}m)`,
      date: w.started_at,
      backgroundColor: '#3b82f6', // blue
      borderColor: '#2563eb',
      extendedProps: { ...w, isPlanned: false }
    })),
    ...data.planned.map((w: any) => ({
      id: `p-${w.id}`,
      title: w.type.toUpperCase(),
      date: w.planned_date,
      backgroundColor: w.status === 'completed' ? '#22c55e' : (w.status === 'skipped' ? '#ef4444' : '#f97316'),
      borderColor: w.status === 'completed' ? '#16a34a' : (w.status === 'skipped' ? '#dc2626' : '#ea580c'),
      extendedProps: { ...w, isPlanned: true }
    }))
  ] : [];

  return (
    <div className="bg-card p-6 rounded-lg border border-border shadow-sm h-[800px]">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-heading text-2xl font-bold text-foreground">Kalendarz Mikrocyklu</h2>
        <button 
          onClick={() => {
            setSelectedDateStr(format(new Date(), 'yyyy-MM-dd'));
            setAddModalOpen(true);
          }}
          className="px-4 py-2 bg-z5 hover:bg-z5/90 text-white rounded font-medium text-sm transition-colors"
        >
          Dodaj Plan Ręcznie
        </button>
      </div>

      {isLoading ? (
        <div className="h-full flex items-center justify-center text-muted-foreground animate-pulse">
          Ładowanie kalendarza...
        </div>
      ) : (
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="dayGridMonth"
          events={events}
          height="100%"
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
          }}
          datesSet={(arg) => setCurrentDate(arg.view.currentStart)}
          dateClick={handleDateClick}
          eventClick={handleEventClick}
          eventContent={(arg) => {
            const isCompleted = arg.event.extendedProps.type === 'completed' || arg.event.extendedProps.status === 'completed';
            return (
              <div className="p-1 px-2 text-xs font-medium w-full overflow-hidden truncate cursor-pointer">
                <div className="font-bold">{arg.event.title}</div>
                {isCompleted && arg.event.extendedProps.tss > 0 && (
                  <div className="opacity-90">TSS: {Math.round(arg.event.extendedProps.tss)}</div>
                )}
              </div>
            );
          }}
        />
      )}

      {/* Modal Dodawania Treningu */}
      <AddWorkoutModal 
        date={selectedDateStr} 
        isOpen={addModalOpen} 
        onOpenChange={setAddModalOpen} 
      />

      {/* Modal Szczegółów Treningu */}
      <Dialog.Root open={detailsModalOpen} onOpenChange={setDetailsModalOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50" />
          <Dialog.Content className="fixed left-[50%] top-[50%] z-50 grid w-full max-w-md translate-x-[-50%] translate-y-[-50%] gap-4 border border-border bg-card p-6 shadow-lg sm:rounded-lg">
            {selectedEvent && (
              <>
                <Dialog.Title className="text-xl font-bold font-heading">
                  {selectedEvent.isPlanned ? 'Zaplanowany Trening' : 'Wykonany Trening'}
                </Dialog.Title>
                
                <div className="space-y-4 text-sm mt-2">
                  <div className="grid grid-cols-2 gap-2 border-b border-border pb-4">
                    <span className="text-muted-foreground">Data:</span>
                    <span className="font-medium">{selectedEvent.isPlanned ? selectedEvent.planned_date : format(new Date(selectedEvent.started_at), 'yyyy-MM-dd')}</span>
                    
                    <span className="text-muted-foreground">Typ/Źródło:</span>
                    <span className="font-medium uppercase">{selectedEvent.type || selectedEvent.source}</span>
                    
                    <span className="text-muted-foreground">Czas trwania:</span>
                    <span className="font-medium">{Math.round(selectedEvent.duration_sec / 60)} min</span>

                    {selectedEvent.isPlanned && (
                      <>
                        <span className="text-muted-foreground">Status:</span>
                        <span className="font-medium uppercase">{selectedEvent.status}</span>
                      </>
                    )}
                    
                    {!selectedEvent.isPlanned && (
                      <>
                        <span className="text-muted-foreground">TSS:</span>
                        <span className="font-medium">{Math.round(selectedEvent.tss || 0)}</span>
                        <span className="text-muted-foreground">NP:</span>
                        <span className="font-medium">{Math.round(selectedEvent.np_power || 0)} W</span>
                      </>
                    )}
                  </div>

                  {selectedEvent.isPlanned && selectedEvent.notes && (
                    <div className="pt-2">
                      <span className="text-muted-foreground block mb-1">Notatki:</span>
                      <p className="bg-muted p-3 rounded-md">{selectedEvent.notes}</p>
                    </div>
                  )}

                  {selectedEvent.isPlanned && (
                    <div className="flex flex-col gap-3 pt-4">
                      {/* Przycisk eksportu ZWO */}
                      <button
                        onClick={() => downloadZwo(selectedEvent.id)}
                        className="w-full py-2 bg-z2 hover:bg-z2/90 text-white rounded-md flex items-center justify-center gap-2 transition-colors font-medium"
                      >
                        <Download className="w-4 h-4" />
                        Pobierz Plik ZWO (Dla Garmin / Zwift)
                      </button>

                      {/* Przyciski zmiany statusu */}
                      {selectedEvent.status === 'planned' && (
                        <div className="flex gap-2 w-full mt-2">
                          <button
                            onClick={() => updateStatusMutation.mutate({ id: selectedEvent.id, status: 'completed' })}
                            className="flex-1 py-2 bg-z3 hover:bg-z3/90 text-white rounded-md flex items-center justify-center gap-1 text-xs"
                          >
                            <CheckCircle className="w-3 h-3" /> Zrobione
                          </button>
                          <button
                            onClick={() => updateStatusMutation.mutate({ id: selectedEvent.id, status: 'skipped' })}
                            className="flex-1 py-2 bg-destructive hover:bg-destructive/90 text-white rounded-md flex items-center justify-center gap-1 text-xs"
                          >
                            <XCircle className="w-3 h-3" /> Pomiń
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="flex justify-end pt-4 mt-2">
                  <button 
                    onClick={() => setDetailsModalOpen(false)}
                    className="px-4 py-2 border border-border rounded hover:bg-muted transition-colors"
                  >
                    Zamknij
                  </button>
                </div>
              </>
            )}
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
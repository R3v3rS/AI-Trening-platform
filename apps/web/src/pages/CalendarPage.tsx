import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { format, subMonths, addMonths } from 'date-fns';
import { useState } from 'react';

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  
  const fromDate = format(subMonths(currentDate, 1), 'yyyy-MM-dd');
  const toDate = format(addMonths(currentDate, 1), 'yyyy-MM-dd');

  const { data, isLoading } = useQuery({
    queryKey: ['calendar', fromDate, toDate],
    queryFn: async () => {
      const res = await api.get(`/calendar?from=${fromDate}&to=${toDate}`);
      return res.data;
    }
  });

  const events = data ? [
    ...data.completed.map((w: any) => ({
      id: `w-${w.id}`,
      title: `Trening (${Math.round(w.duration_sec / 60)}m)`,
      date: w.started_at,
      backgroundColor: '#3b82f6', // blue
      borderColor: '#2563eb',
      extendedProps: { ...w }
    })),
    ...data.planned.map((w: any) => ({
      id: `p-${w.id}`,
      title: w.type.toUpperCase(),
      date: w.planned_date,
      backgroundColor: w.status === 'completed' ? '#22c55e' : '#f97316',
      borderColor: w.status === 'completed' ? '#16a34a' : '#ea580c',
      extendedProps: { ...w }
    }))
  ] : [];

  return (
    <div className="bg-card p-6 rounded-lg border border-border shadow-sm h-[800px]">
      <h2 className="font-heading text-2xl font-bold mb-6 text-foreground">Kalendarz Mikrocyklu</h2>
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
          eventContent={(arg) => {
            const isCompleted = arg.event.extendedProps.type === 'completed' || arg.event.extendedProps.status === 'completed';
            return (
              <div className="p-1 px-2 text-xs font-medium w-full overflow-hidden truncate">
                <div className="font-bold">{arg.event.title}</div>
                {isCompleted && arg.event.extendedProps.tss > 0 && (
                  <div className="opacity-90">TSS: {Math.round(arg.event.extendedProps.tss)}</div>
                )}
              </div>
            );
          }}
        />
      )}
    </div>
  );
}
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { format, subDays, addDays } from 'date-fns';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Area
} from 'recharts';

export default function AnalyticsPage() {
  const currentDate = new Date();
  const fromDate = format(subDays(currentDate, 42), 'yyyy-MM-dd');
  const toDate = format(addDays(currentDate, 7), 'yyyy-MM-dd');

  // Query for Load Metrics
  const { data: loadData, isLoading: isLoadingLoad } = useQuery({
    queryKey: ['load_metrics', fromDate, toDate],
    queryFn: async () => {
      const res = await api.get(`/metrics/load?from=${fromDate}&to=${toDate}`);
      return res.data.map((d: any) => ({
        ...d,
        date: format(new Date(d.date), 'dd MMM'),
        tsb_positive: d.tsb >= 0 ? d.tsb : 0,
        tsb_negative: d.tsb < 0 ? d.tsb : 0
      }));
    }
  });

  // Query for Power Curve
  const { data: powerCurve, isLoading: isLoadingPower } = useQuery({
    queryKey: ['power_curve'],
    queryFn: async () => {
      const res = await api.get('/metrics/power-curve');
      const d = res.data;
      return [
        { duration: '5s', power: d.sec_5 },
        { duration: '1 min', power: d.sec_60 },
        { duration: '5 min', power: d.sec_300 },
        { duration: '20 min', power: d.sec_1200 },
      ];
    }
  });

  return (
    <div className="space-y-8">
      {/* Load Metrics Chart */}
      <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
        <h2 className="font-heading text-2xl font-bold mb-2">Trendy Obciążeń (PMC)</h2>
        <p className="text-sm text-muted-foreground mb-6">Wykres zarządzania kondycją: CTL (Kondycja), ATL (Zmęczenie), TSB (Świeżość)</p>
        
        <div className="h-[400px] w-full">
          {isLoadingLoad ? (
            <div className="h-full flex items-center justify-center text-muted-foreground animate-pulse">
              Ładowanie danych analitycznych...
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={loadData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="date" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                <YAxis yAxisId="left" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Legend />
                
                {/* TSB (Form) as Area */}
                <Area yAxisId="right" type="monotone" dataKey="tsb" name="TSB (Świeżość)" fill="#eab308" stroke="#eab308" fillOpacity={0.2} />
                
                {/* ATL (Fatigue) */}
                <Line yAxisId="left" type="monotone" dataKey="atl" name="ATL (Zmęczenie)" stroke="#ef4444" strokeWidth={2} dot={false} />
                
                {/* CTL (Fitness) */}
                <Line yAxisId="left" type="monotone" dataKey="ctl" name="CTL (Kondycja)" stroke="#3b82f6" strokeWidth={3} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Power Curve Chart */}
      <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
        <h2 className="font-heading text-2xl font-bold mb-2">Krzywa Mocy (Power Curve)</h2>
        <p className="text-sm text-muted-foreground mb-6">Twoje najlepsze wyniki średniej mocy w różnych przedziałach czasowych.</p>
        
        <div className="h-[300px] w-full">
          {isLoadingPower ? (
            <div className="h-full flex items-center justify-center text-muted-foreground animate-pulse">
              Obliczanie krzywej mocy...
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={powerCurve} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="duration" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} domain={['auto', 'auto']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                  formatter={(value) => [`${value} W`, 'Moc']}
                />
                <Line 
                  type="monotone" 
                  dataKey="power" 
                  name="Maksymalna Moc (W)" 
                  stroke="#f97316" 
                  strokeWidth={3} 
                  dot={{ r: 6, fill: '#f97316', stroke: '#0f172a', strokeWidth: 2 }} 
                  activeDot={{ r: 8 }} 
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
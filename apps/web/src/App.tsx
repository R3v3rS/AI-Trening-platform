import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Activity, Calendar, User, Upload } from 'lucide-react';
import CalendarPage from './pages/CalendarPage';
import WorkoutsPage from './pages/WorkoutsPage';
import ProfilePage from './pages/ProfilePage';
import ImportPage from './pages/ImportPage';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-background text-foreground font-sans">
          <header className="border-b border-border bg-card">
            <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="w-6 h-6 text-z5" />
                <h1 className="font-heading text-xl font-bold tracking-wide uppercase">Asystent Kolarza</h1>
              </div>
              <nav className="flex items-center gap-6">
                <Link to="/" className="flex items-center gap-2 text-sm font-medium hover:text-z5 transition-colors">
                  <Calendar className="w-4 h-4" /> Kalendarz
                </Link>
                <Link to="/workouts" className="flex items-center gap-2 text-sm font-medium hover:text-z5 transition-colors">
                  <Activity className="w-4 h-4" /> Treningi
                </Link>
                <Link to="/import" className="flex items-center gap-2 text-sm font-medium hover:text-z5 transition-colors">
                  <Upload className="w-4 h-4" /> Import
                </Link>
                <Link to="/profile" className="flex items-center gap-2 text-sm font-medium hover:text-z5 transition-colors">
                  <User className="w-4 h-4" /> Profil
                </Link>
              </nav>
            </div>
          </header>

          <main className="flex-1 max-w-7xl w-full mx-auto p-4 py-8">
            <Routes>
              <Route path="/" element={<CalendarPage />} />
              <Route path="/workouts" element={<WorkoutsPage />} />
              <Route path="/import" element={<ImportPage />} />
              <Route path="/profile" element={<ProfilePage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
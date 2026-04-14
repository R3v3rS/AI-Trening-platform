import { http, HttpResponse } from 'msw';
import { WorkoutType, WorkoutStatus, Profile, LoadMetric, CalendarData, PaginatedWorkouts } from '../types';

// Mock DB
let profile: Profile = {
  ftp: 250,
  weight: 75,
  hr_max: 190,
  hr_threshold: 170,
  experience_level: 'intermediate',
  weekly_hours: 8,
};

const metrics: LoadMetric[] = [
  { date: new Date().toISOString(), ctl: 65, atl: 70, tsb: -5 },
  { date: new Date(Date.now() - 86400000).toISOString(), ctl: 64, atl: 65, tsb: -1 },
  { date: new Date(Date.now() - 86400000 * 2).toISOString(), ctl: 63, atl: 60, tsb: 3 },
];

const generateWorkouts = (count: number): CalendarData[] => {
  return Array.from({ length: count }).map((_, i) => ({
    id: `workout-${i}`,
    date: new Date(Date.now() - Math.random() * 30 * 86400000).toISOString(),
    duration: Math.floor(Math.random() * 90) + 30,
    type: Object.values(WorkoutType)[Math.floor(Math.random() * Object.values(WorkoutType).length)],
    status: Object.values(WorkoutStatus)[Math.floor(Math.random() * Object.values(WorkoutStatus).length)],
    title: `Training Session ${i + 1}`,
  }));
};

let workouts = generateWorkouts(50);

const baseURL = '/api/v1';

export const handlers = [
  // Profile
  http.get(`${baseURL}/profile`, () => {
    return HttpResponse.json(profile);
  }),
  
  http.put(`${baseURL}/profile`, async ({ request }) => {
    const updatedProfile = await request.json() as Profile;
    profile = { ...profile, ...updatedProfile };
    return HttpResponse.json(profile);
  }),

  // Metrics
  http.get(`${baseURL}/metrics`, () => {
    return HttpResponse.json(metrics);
  }),

  // Calendar
  http.get(`${baseURL}/calendar`, ({ request }) => {
    const url = new URL(request.url);
    const from = url.searchParams.get('from');
    const to = url.searchParams.get('to');
    
    let filteredWorkouts = workouts;

    if (from) {
      const fromDate = new Date(from).getTime();
      filteredWorkouts = filteredWorkouts.filter(w => new Date(w.date).getTime() >= fromDate);
    }
    
    if (to) {
      const toDate = new Date(to);
      toDate.setHours(23, 59, 59, 999);
      filteredWorkouts = filteredWorkouts.filter(w => new Date(w.date).getTime() <= toDate.getTime());
    }

    return HttpResponse.json(filteredWorkouts); 
  }),

  // Workouts (paginated)
  http.get(`${baseURL}/workouts`, ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');
    const type = url.searchParams.get('type');
    const status = url.searchParams.get('status');

    let filtered = [...workouts];

    if (type) {
      filtered = filtered.filter(w => w.type === type);
    }
    if (status) {
      filtered = filtered.filter(w => w.status === status);
    }

    // Sort by date desc
    filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

    const start = (page - 1) * limit;
    const end = start + limit;
    const paginatedItems = filtered.slice(start, end);

    const response: PaginatedWorkouts = {
      data: paginatedItems,
      total: filtered.length,
      page,
      limit,
    };

    return HttpResponse.json(response);
  }),

  // FTP Test
  http.post(`${baseURL}/ftp-test/manual`, async ({ request }) => {
    const body = await request.json() as { protocol: string; avg_power: number };
    const suggested_ftp = body.protocol === '20min' ? Math.round(body.avg_power * 0.95) : Math.round(body.avg_power * 0.75);
    
    return HttpResponse.json({
      suggested_ftp,
      test_id: `test-${Date.now()}`
    });
  }),

  http.post(`${baseURL}/ftp-test/accept`, () => {
    return new HttpResponse(null, { status: 200 });
  }),
];

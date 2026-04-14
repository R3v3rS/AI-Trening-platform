import { apiClient } from './client';
import { CalendarData, PlannedWorkoutData, WorkoutStatus } from '../../types';

export const getCalendar = async (from: string, to: string): Promise<CalendarData[]> => {
  const { data } = await apiClient.get<CalendarData[]>('/calendar', {
    params: { from, to },
  });
  return data;
};

export const createPlannedWorkout = async (workoutData: PlannedWorkoutData): Promise<CalendarData> => {
  const { data } = await apiClient.post<CalendarData>('/calendar/planned', workoutData);
  return data;
};

export const updateWorkoutStatus = async (
  id: string,
  status: WorkoutStatus,
  moved_to_date?: string
): Promise<CalendarData> => {
  const { data } = await apiClient.patch<CalendarData>(`/calendar/${id}/status`, {
    status,
    moved_to_date,
  });
  return data;
};

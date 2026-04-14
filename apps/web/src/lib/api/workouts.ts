import { apiClient } from './client';
import { GetWorkoutsParams, PaginatedWorkouts } from '../../types';

export const getWorkouts = async (params: GetWorkoutsParams): Promise<PaginatedWorkouts> => {
  const { data } = await apiClient.get<PaginatedWorkouts>('/workouts', { params });
  return data;
};

import { apiClient } from './client';
import { LoadMetric } from '../../types';

export const getLoadMetrics = async (from: string, to: string): Promise<LoadMetric[]> => {
  const { data } = await apiClient.get<LoadMetric[]>('/metrics', {
    params: { from, to },
  });
  return data;
};

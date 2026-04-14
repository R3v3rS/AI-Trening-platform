import { apiClient } from './client';
import { Profile } from '../../types';

export const getProfile = async (): Promise<Profile> => {
  const { data } = await apiClient.get<Profile>('/profile');
  return data;
};

export const updateProfile = async (profileData: Partial<Profile>): Promise<Profile> => {
  const { data } = await apiClient.put<Profile>('/profile', profileData);
  return data;
};

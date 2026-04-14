import { apiClient } from './client';

export interface FtpTestResult {
  suggested_ftp: number;
  test_id: string;
}

export const submitManualFtpTest = async (protocol: string, avg_power: number): Promise<FtpTestResult> => {
  const { data } = await apiClient.post<FtpTestResult>('/ftp-test/manual', {
    protocol,
    avg_power,
  });
  return data;
};

export const acceptFtpTest = async (test_id: string): Promise<void> => {
  await apiClient.post(`/ftp-test/accept`, { test_id });
};

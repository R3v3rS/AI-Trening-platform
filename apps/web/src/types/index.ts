import { z } from 'zod';

export enum WorkoutType {
  CYCLING = 'CYCLING',
  RUNNING = 'RUNNING',
  SWIMMING = 'SWIMMING',
  STRENGTH = 'STRENGTH',
  OTHER = 'OTHER'
}

export enum WorkoutStatus {
  PLANNED = 'PLANNED',
  COMPLETED = 'COMPLETED',
  MISSED = 'MISSED'
}

export const ProfileSchema = z.object({
  ftp: z.number().min(0, "FTP musi być większe od 0"),
  weight: z.number().min(0, "Waga musi być większa od 0"),
  hr_max: z.number().min(0, "HR Max musi być większe od 0"),
  hr_threshold: z.number().min(0, "Próg HR musi być większy od 0"),
  experience_level: z.string().min(1, "Wybierz poziom doświadczenia"),
  weekly_hours: z.number().min(0, "Tygodniowe godziny muszą być nieujemne"),
});

export type Profile = z.infer<typeof ProfileSchema>;

export interface LoadMetric {
  date: string;
  ctl: number;
  atl: number;
  tsb: number;
}

export interface DashboardMetrics {
  ftp: number;
  weight: number;
  hr_max: number;
  ctl: number;
  atl: number;
  tsb: number;
}

export interface CalendarData {
  id: string;
  date: string;
  duration: number; // in minutes
  type: WorkoutType;
  status: WorkoutStatus;
  title?: string;
}

export interface PlannedWorkoutData {
  date: string;
  duration: number;
  type: WorkoutType;
  title?: string;
}

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
  ftp: z.coerce.number().positive("FTP musi być większe od 0"),
  weight: z.coerce.number().positive("Waga musi być większa od 0"),
  hr_max: z.coerce.number().positive("HR Max musi być większe od 0"),
  hr_threshold: z.coerce.number().positive("Próg HR musi być większy od 0"),
  experience_level: z.string().min(1, "Wybierz poziom doświadczenia"),
  weekly_hours: z.coerce.number().min(0, "Tygodniowe godziny muszą być nieujemne"),
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

export interface GetWorkoutsParams {
  page?: number;
  limit?: number;
  type?: WorkoutType | '';
  status?: WorkoutStatus | '';
}

export interface PaginatedWorkouts {
  data: CalendarData[];
  total: number;
  page: number;
  limit: number;
}

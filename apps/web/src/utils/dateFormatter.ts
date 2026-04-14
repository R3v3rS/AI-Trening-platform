/**
 * Format an ISO date string to a consistent localized date,
 * treating the date as UTC to prevent timezone offset issues
 * when displaying calendar days.
 */
export const formatDate = (isoDateString: string): string => {
  const date = new Date(isoDateString);
  
  // Use a consistent format or the user's locale, but force UTC 
  // so that midnight UTC doesn't shift to the previous day in other timezones.
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone: 'UTC'
  }).format(date);
};

/**
 * Returns the first and last day of the current UTC month in YYYY-MM-DD format.
 */
export const getCurrentMonthRange = (): { from: string; to: string } => {
  const now = new Date();
  
  const firstDay = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1));
  const lastDay = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 0));

  return {
    from: firstDay.toISOString().split('T')[0],
    to: lastDay.toISOString().split('T')[0]
  };
};

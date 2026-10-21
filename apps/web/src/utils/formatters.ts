export const formatSpeedMps = (mps: number): string => {
  const kph = (mps * 3.6).toFixed(1);
  return `${mps.toFixed(1)} m/s (${kph} km/h)`;
};

export const formatDurationSeconds = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const formatDistanceMeters = (meters: number): string => {
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(2)} km`;
  }
  return `${meters.toFixed(0)} m`;
};

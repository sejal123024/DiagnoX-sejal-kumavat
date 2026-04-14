/**
 * Utility functions for audio processing on the client side
 */

export const validateAudioFormat = (filename: string): boolean => {
  const validExtensions = ['.wav', '.mp3', '.ogg', '.m4a'];
  return validExtensions.some(ext => filename.toLowerCase().endsWith(ext));
};

export const formatAudioDuration = (seconds: number): string => {
  if (isNaN(seconds) || seconds < 0) return '0:00';
  
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export const bytesToMegabytes = (bytes: number): string => {
  if (bytes === 0) return '0 MB';
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(2)} MB`;
};

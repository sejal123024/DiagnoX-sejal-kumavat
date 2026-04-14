/**
 * Global frontend configuration and constants
 */

export const APP_NAME = "DiagnoX-VitaScan";
export const APP_VERSION = "1.0.0";
export const CONTACT_EMAIL = "support@vitascan-diagno.ai";

export const API_ENDPOINTS = {
  PREDICT: '/api/predict',
  HEALTH_CHECK: '/api/health',
  UPLOAD_AUDIO: '/api/audio/upload'
};

export const MAX_AUDIO_SIZE_MB = 25;
export const MAX_AUDIO_SIZE_BYTES = MAX_AUDIO_SIZE_MB * 1024 * 1024;
export const SUPPORTED_BROWSERS = ['Chrome', 'Firefox', 'Safari'];

/**
 * INSPECTRA - Formatting and Helper Utilities
 * Clean, pure transformation functions with no side effects.
 */

/**
 * Normalizes status string to standard 'PASS' | 'REJECT' | 'REVIEW' | 'UNKNOWN'
 * @param {string} status 
 * @returns {'PASS' | 'REJECT' | 'REVIEW' | 'UNKNOWN'}
 */
export function normalizeStatus(status) {
  if (!status) return 'UNKNOWN';
  const upper = String(status).trim().toUpperCase();
  if (upper === 'PASS' || upper === 'PASSED' || upper === 'OK' || upper === 'NORMAL') {
    return 'PASS';
  }
  if (upper === 'REJECT' || upper === 'REJECTED' || upper === 'DEFECT' || upper === 'ANOMALOUS' || upper === 'FAIL') {
    return 'REJECT';
  }
  if (upper === 'REVIEW' || upper === 'REQUIRES_REVIEW' || upper === 'WARNING' || upper === 'UNCERTAIN') {
    return 'REVIEW';
  }
  return upper;
}

/**
 * Formats an anomaly score from the backend exactly as a decimal.
 * Does NOT guess or convert to percentage unless explicitly requested.
 * @param {number|string} score 
 * @param {number} decimals 
 * @returns {string}
 */
export function formatScore(score, decimals = 4) {
  if (score === null || score === undefined || score === '') return '—';
  const num = Number(score);
  if (isNaN(num)) return String(score);
  return num.toFixed(decimals);
}

/**
 * Formats inference time in milliseconds
 * @param {number|string} timeMs 
 * @returns {string}
 */
export function formatInferenceTime(timeMs) {
  if (timeMs === null || timeMs === undefined || timeMs === '') return '—';
  const num = Number(timeMs);
  if (isNaN(num)) return String(timeMs);
  if (num < 1000) {
    return `${Math.round(num)} ms`;
  }
  return `${(num / 1000).toFixed(2)} s`;
}

/**
 * Formats file size in bytes to human-readable string (KB, MB)
 * @param {number} bytes 
 * @returns {string}
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes <= 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Formats ISO date string or timestamp into clean industrial format
 * e.g., "2026-10-31 14:05:22"
 * @param {string|number|Date} dateValue 
 * @returns {string}
 */
export function formatDateTime(dateValue) {
  if (!dateValue) return '—';
  try {
    const d = new Date(dateValue);
    if (isNaN(d.getTime())) return String(dateValue);

    const pad = (n) => String(n).padStart(2, '0');
    const year = d.getFullYear();
    const month = pad(d.getMonth() + 1);
    const day = pad(d.getDate());
    const hours = pad(d.getHours());
    const minutes = pad(d.getMinutes());
    const seconds = pad(d.getSeconds());

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch {
    return String(dateValue);
  }
}

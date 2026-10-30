/**
 * INSPECTRA - API Integration Service
 * Centralizes all network communication with the FastAPI backend.
 * Never mix styling or component-specific logic here.
 */

// Environment variable for backend URL, default to http://localhost:8000
export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, ''); // Strip trailing slash for consistency

// Configurable upload form-data field name (default: 'file')
export const UPLOAD_FIELD_NAME = 'file';

/**
 * Resolves an image path returned by the backend into a fully qualified URL.
 * Handles absolute URLs, data URIs, and relative backend paths.
 * 
 * @param {string} imagePath 
 * @returns {string} Fully qualified image URL
 */
export function resolveImageUrl(imagePath) {
  if (!imagePath) return '';
  if (typeof imagePath !== 'string') return '';
  
  // If already absolute or data URI or blob URL
  if (
    imagePath.startsWith('http://') ||
    imagePath.startsWith('https://') ||
    imagePath.startsWith('data:') ||
    imagePath.startsWith('blob:')
  ) {
    return imagePath;
  }

  // Prepend base URL with clean slash handling
  const cleanPath = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
  return `${API_BASE_URL}${cleanPath}`;
}

/**
 * Helper to normalize raw backend response objects into standardized Inspection records.
 * Protects components from schema drift or casing differences.
 */
export function normalizeInspectionRecord(raw) {
  if (!raw || typeof raw !== 'object') return null;

  return {
    id: raw.id ?? raw.inspection_id ?? null,
    product_id: raw.product_id ?? raw.productId ?? `INS-${String(raw.id || '000').padStart(3, '0')}`,
    anomaly_score: raw.anomaly_score !== undefined ? Number(raw.anomaly_score) : (raw.score !== undefined ? Number(raw.score) : null),
    status: (raw.status || 'UNKNOWN').toUpperCase(),
    original_image: raw.original_image || raw.originalImageUrl || raw.image_url || '',
    heatmap_image: raw.heatmap_image || raw.heatmapImageUrl || raw.heatmap || '',
    inference_time_ms: raw.inference_time_ms ?? raw.inferenceTime ?? raw.inference_ms ?? null,
    created_at: raw.created_at || raw.timestamp || raw.date || new Date().toISOString(),
    notes: raw.notes || raw.details || null
  };
}

/**
 * Normalizes list responses, whether backend returns:
 * - A direct array: [ {...}, {...} ]
 * - Wrapped object: { inspections: [...] }
 * - Wrapped object: { data: [...] }
 * - Wrapped object: { results: [...] }
 */
function normalizeInspectionList(responseJson) {
  if (Array.isArray(responseJson)) {
    return responseJson.map(normalizeInspectionRecord).filter(Boolean);
  }
  if (responseJson && typeof responseJson === 'object') {
    const list = responseJson.inspections || responseJson.data || responseJson.results || responseJson.items;
    if (Array.isArray(list)) {
      return list.map(normalizeInspectionRecord).filter(Boolean);
    }
  }
  return [];
}

/**
 * Pings the backend to check system connectivity and status.
 * @returns {Promise<{ isOnline: boolean, latencyMs?: number, info?: any }>}
 */
export async function checkSystemHealth() {
  const start = performance.now();
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    // Try / or /health or /docs depending on FastAPI standard conventions
    const res = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
      signal: controller.signal
    }).catch(async () => {
      return await fetch(`${API_BASE_URL}/docs`, { method: 'HEAD', signal: controller.signal });
    });

    clearTimeout(timeoutId);
    const latencyMs = Math.round(performance.now() - start);

    if (res.ok || res.status === 404) {
      // Server is listening and responded
      return { isOnline: true, latencyMs };
    }
    return { isOnline: false, latencyMs, error: `HTTP ${res.status}` };
  } catch (err) {
    return { isOnline: false, latencyMs: 0, error: err.message || 'Connection refused' };
  }
}

/**
 * Submits an image file to the inspection API.
 * Endpoint: POST /inspect
 * Sends multipart/form-data with field name 'file'.
 * 
 * @param {File|Blob} file 
 * @param {string} [productId] Optional custom product ID
 * @returns {Promise<Object>} Normalized inspection record
 */
export async function submitInspection(file, productId = '') {
  if (!file) {
    throw new Error('Please select or capture a valid image file before inspecting.');
  }

  const formData = new FormData();
  // Field name 'file' as specified in brief
  formData.append(UPLOAD_FIELD_NAME, file);

  if (productId && productId.trim()) {
    formData.append('product_id', productId.trim());
  }

  try {
    const controller = new AbortController();
    // Allow up to 30s for heavy AI model inference
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    // Note: Do NOT set Content-Type header. Browser sets it with multipart boundary automatically.
    const response = await fetch(`${API_BASE_URL}/inspect`, {
      method: 'POST',
      body: formData,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorDetail = `Inspection failed with HTTP ${response.status} (${response.statusText})`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorDetail = typeof errorJson.detail === 'string' 
            ? errorJson.detail 
            : JSON.stringify(errorJson.detail);
        } else if (errorJson.message) {
          errorDetail = errorJson.message;
        }
      } catch {
        // If not JSON, try text
        const text = await response.text();
        if (text) errorDetail = text.slice(0, 150);
      }
      throw new Error(errorDetail);
    }

    const data = await response.json();
    return normalizeInspectionRecord(data);
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Inspection request timed out. The AI model server took too long to respond.', { cause: err });
    }
    // Network error (e.g. backend server is not running)
    if (err.message && (err.message.includes('Failed to fetch') || err.message.includes('NetworkError') || err.message.includes('Load failed'))) {
      throw new Error(
        `Unable to connect to INSPECTRA Backend at ${API_BASE_URL}. Please ensure the FastAPI server is running.`,
        { cause: err }
      );
    }
    throw err;
  }
}

/**
 * Retrieves the list of previous inspection records.
 * Endpoint: GET /inspections
 * 
 * @returns {Promise<Array<Object>>} Normalized list of inspections
 */
export async function fetchInspections() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    const response = await fetch(`${API_BASE_URL}/inspections`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Failed to load inspections (HTTP ${response.status}: ${response.statusText})`);
    }

    const data = await response.json();
    return normalizeInspectionList(data);
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Inspection records request timed out.', { cause: err });
    }
    if (err.message && (err.message.includes('Failed to fetch') || err.message.includes('NetworkError') || err.message.includes('Load failed'))) {
      throw new Error(
        `Unable to reach backend at ${API_BASE_URL}. Ensure FastAPI server is accessible.`,
        { cause: err }
      );
    }
    throw err;
  }
}

/**
 * Retrieves a single inspection record by ID.
 * Endpoint: GET /inspections/{id}
 * 
 * @param {string|number} id 
 * @returns {Promise<Object>} Normalized inspection record
 */
export async function fetchInspectionById(id) {
  if (!id) {
    throw new Error('Inspection ID is required.');
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);

    const response = await fetch(`${API_BASE_URL}/inspections/${id}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (response.status === 404) {
      throw new Error(`Inspection record #${id} was not found on the server.`);
    }

    if (!response.ok) {
      throw new Error(`Failed to fetch inspection #${id} (HTTP ${response.status})`);
    }

    const data = await response.json();
    return normalizeInspectionRecord(data);
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error(`Request timed out while fetching inspection record #${id}.`, { cause: err });
    }
    if (err.message && (err.message.includes('Failed to fetch') || err.message.includes('NetworkError') || err.message.includes('Load failed'))) {
      throw new Error(
        `Unable to reach backend at ${API_BASE_URL}. Check your server connection.`,
        { cause: err }
      );
    }
    throw err;
  }
}

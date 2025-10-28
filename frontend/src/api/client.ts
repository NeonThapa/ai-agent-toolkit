export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8081";

interface JsonResponse<T> {
  kind: "json";
  data: T;
  response: Response;
}

interface FileResponse {
  kind: "file";
  blob: Blob;
  fileName: string;
  mimeType: string;
  response: Response;
}

export type ApiResponse<T> = JsonResponse<T> | FileResponse;

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

const parseFileName = (contentDisposition: string | null): string => {
  if (!contentDisposition) {
    return `download-${Date.now()}`;
  }
  const match = /filename\*?=([^;]+)/i.exec(contentDisposition);
  if (!match) {
    return `download-${Date.now()}`;
  }
  const value = match[1].trim();
  if (value.startsWith("UTF-8''")) {
    return decodeURIComponent(value.substring(7));
  }
  return value.replace(/["']/g, "");
};

const handleResponse = async <T>(response: Response): Promise<ApiResponse<T>> => {
  if (!response.ok) {
    let message = response.statusText;
    try {
      const body = await response.clone().json();
      if (body?.error) {
        message = body.error;
      }
    } catch (_) {
      const text = await response.clone().text();
      if (text) {
        message = text;
      }
    }
    throw new ApiError(message || "API request failed", response.status);
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    const data = (await response.json()) as T;
    return { kind: "json", data, response };
  }

  const blob = await response.blob();
  const mimeType = blob.type || contentType || "application/octet-stream";
  const fileName = parseFileName(response.headers.get("content-disposition"));
  return { kind: "file", blob, mimeType, fileName, response };
};

export const get = async <T>(path: string): Promise<T> => {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new ApiError(response.statusText, response.status);
  }
  return (await response.json()) as T;
};

export const postJson = async <T>(
  path: string,
  payload: unknown,
  init?: RequestInit
): Promise<ApiResponse<T>> => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    body: JSON.stringify(payload),
    ...init,
  });
  return handleResponse<T>(response);
};

export const postFormData = async <T>(
  path: string,
  formData: FormData,
  init?: RequestInit
): Promise<T> => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
    ...init,
  });
  if (!response.ok) {
    const message = await response.text();
    throw new ApiError(message || "Upload failed", response.status);
  }
  return (await response.json()) as T;
};

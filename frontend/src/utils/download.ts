import type { ApiResponse } from "../api/client";

export const downloadFromApi = async <T>(
  response: ApiResponse<T>
): Promise<T | void> => {
  if (response.kind === "json") {
    return response.data;
  }

  const blobUrl = window.URL.createObjectURL(response.blob);
  const link = document.createElement("a");
  link.href = blobUrl;
  link.download = response.fileName || `download-${Date.now()}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(blobUrl);
};

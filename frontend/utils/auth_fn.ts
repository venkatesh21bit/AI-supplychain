
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

const getAuthToken = (): string | null => {
  return localStorage.getItem("access_token");
};

const getRefreshToken = (): string | null => {
  return localStorage.getItem("refresh_token");
};

const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_URL}/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      console.error("Failed to refresh token");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      return null;
    }

    const data = await response.json();
    if (data.access) {
      localStorage.setItem("access_token", data.access);
      return data.access;
    }
  } catch (error) {
    console.error("Error refreshing token:", error);
  }

  return null;
};

const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
  let token = getAuthToken();
  if (!token) throw new Error("Authentication token not found. Please log in again.");

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (response.status === 401) {
    token = await refreshAccessToken();
    if (!token) throw new Error("Authentication token not found. Please log in again.");

    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
  }

  return response;
};

export { API_URL, getAuthToken, refreshAccessToken, fetchWithAuth };
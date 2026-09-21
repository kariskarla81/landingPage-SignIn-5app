import { api, API } from "@/lib/api";

const TOKEN_KEY = "elastech_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY) || "";
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

function handleUnauthorized() {
  clearToken();
  window.dispatchEvent(new Event("auth:unauthorized"));
}

let installed = false;

// Attach the session token to every backend request (axios + global fetch) and
// react to 401s by clearing the session and notifying the AuthProvider.
export function installAuthInterceptors() {
  if (installed) return;
  installed = true;

  // Shared axios instance (used by AuthContext)
  api.interceptors.request.use((config) => {
    const t = getToken();
    if (t) config.headers["X-Session-Token"] = t;
    return config;
  });
  api.interceptors.response.use(
    (r) => r,
    (error) => {
      const url = error?.config?.url || "";
      if (error?.response?.status === 401 && !url.includes("/auth/")) handleUnauthorized();
      return Promise.reject(error);
    }
  );

  // Global fetch (used by kht/dka/copper api helpers, react-query, uploads, image fetches)
  const origFetch = window.fetch.bind(window);
  window.fetch = async (input, init = {}) => {
    const url = typeof input === "string" ? input : (input && input.url) || "";
    const isApi = typeof url === "string" && url.startsWith(API);
    const isAuthEndpoint = isApi && url.startsWith(`${API}/auth/`);
    let nextInit = init;
    if (isApi) {
      const token = getToken();
      if (token) {
        const headers = new Headers(init.headers || {});
        headers.set("X-Session-Token", token);
        nextInit = { ...init, headers };
      }
    }
    const res = await origFetch(input, nextInit);
    if (isApi && !isAuthEndpoint && res.status === 401) handleUnauthorized();
    return res;
  };
}

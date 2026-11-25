const baseURL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "")
type Options = { params?: Record<string, string | number | undefined>; headers?: Record<string,string>; responseType?: "json" | "blob" }
async function request<T>(method: string, path: string, data?: unknown, options: Options = {}, retried = false): Promise<{data:T; headers:Headers}> {
  const params = new URLSearchParams()
  Object.entries(options.params || {}).forEach(([key,value]) => { if (value !== undefined && value !== "") params.set(key,String(value)) })
  const url = `${baseURL}${path.startsWith("/api/") ? path : `/api/v1${path}`}${params.size ? `?${params}` : ""}`
  const token = localStorage.getItem("access_token")
  const headers = new Headers(options.headers)
  if (token) headers.set("Authorization", `Bearer ${token}`)
  if (data && !(data instanceof FormData)) headers.set("Content-Type", "application/json")
  const response = await fetch(url, { method, headers, body: data instanceof FormData ? data : data === undefined ? undefined : JSON.stringify(data) })
  if (response.status === 401 && !retried && path !== "/auth/refresh") {
    const refreshToken = localStorage.getItem("refresh_token")
    if (refreshToken) {
      const renewed = await fetch(`${baseURL}/api/v1/auth/refresh`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({refresh_token:refreshToken}) })
      if (renewed.ok) {
        const tokens = await renewed.json()
        localStorage.setItem("access_token", tokens.access_token)
        localStorage.setItem("refresh_token", tokens.refresh_token)
        return request<T>(method, path, data, options, true)
      }
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
    }
  }
  if (!response.ok) { const body = await response.json().catch(() => null); const detail = body?.detail; throw new Error(typeof detail === "string" ? detail : `${response.status} ${response.statusText}`) }
  const value = options.responseType === "blob" ? await response.blob() as T : response.status === 204 ? undefined as T : await response.json() as T
  return { data:value, headers:response.headers }
}
const api = {
  get: <T=unknown>(path:string, options?:Options) => request<T>("GET",path,undefined,options),
  post: <T=unknown>(path:string, data?:unknown, options?:Options) => request<T>("POST",path,data,options),
  patch: <T=unknown>(path:string, data?:unknown, options?:Options) => request<T>("PATCH",path,data,options),
}
export default api

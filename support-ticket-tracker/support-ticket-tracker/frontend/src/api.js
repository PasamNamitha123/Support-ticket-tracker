// Small wrapper around fetch for the FastAPI backend.
export async function api(path, { method = "GET", token, json, form } = {}) {
  const headers = {};
  let body;

  if (token) headers.Authorization = `Bearer ${token}`;
  if (json) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(json);
  }
  if (form) body = new URLSearchParams(form); // login uses form encoding

  const res = await fetch(`/api${path}`, { method, headers, body });

  if (!res.ok) {
    let message = "Something went wrong";
    try {
      const data = await res.json();
      if (typeof data.detail === "string") message = data.detail;
      else if (Array.isArray(data.detail) && data.detail[0]?.msg) message = data.detail[0].msg;
    } catch {
      // response had no JSON body
    }
    const error = new Error(message);
    error.status = res.status;
    throw error;
  }
  return res.json();
}

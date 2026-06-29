const API_HOST = process.env.NEXT_PUBLIC_API_HOST || "http://localhost:8080";

export async function apiGet(path: string) {
  const res = await fetch(`${API_HOST}${path}`);
  return res.json();
}

export async function apiPost(path: string, body: any) {
  const res = await fetch(`${API_HOST}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

export async function apiUpload(path: string, formData: FormData) {
  const res = await fetch(`${API_HOST}${path}`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export function getReportUrl(reportId: string) {
  return `${API_HOST}/api/report/${reportId}`;
}

export function getBatchReportUrl(taskId: string) {
  return `${API_HOST}/api/batch/${taskId}/report`;
}

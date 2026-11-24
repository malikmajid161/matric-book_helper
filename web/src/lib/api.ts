const BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
export async function request<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {method: body ? 'POST' : 'GET', headers: {'Content-Type': 'application/json', 'X-Study-Code': sessionStorage.getItem('studyCode') || '', 'Authorization': `Bearer ${sessionStorage.getItem('studyToken') || ''}`}, body: body ? JSON.stringify(body) : undefined, signal: AbortSignal.timeout(45000)});
  if (!response.ok) { const error = await response.json().catch(() => ({})); throw new Error(error.detail || `Request failed (${response.status})`); }
  return response.json();
}
export async function downloadPDF(book: string): Promise<Blob> {
  const response = await fetch(`${BASE}/books/${book}/download`, {headers: {'X-Study-Code': sessionStorage.getItem('studyCode') || '', 'Authorization': `Bearer ${sessionStorage.getItem('studyToken') || ''}`}, signal: AbortSignal.timeout(180000)});
  if (!response.ok) throw new Error('Book download failed. Please retry.');
  return response.blob();
}

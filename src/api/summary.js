import api from "./axios";

// Helper: format date to YYYY-MM-DD
const fmt = (d) => d.toISOString().split("T")[0];

export async function summarizeQuestion(question) {
  const resp = await api.post("/summary/summarize/", { question });
  return resp.data;
}

export async function getRevenue({ days = 30 } = {}) {
  const today = new Date();
  const start = new Date();
  start.setDate(start.getDate() - days);

  // Use revenue-by-day and aggregate on frontend for flexibility
  const resp = await api.get("/metrics/revenue-by-day/", {
    params: { start: fmt(start), end: fmt(today) },
  });
  const data = resp.data || [];
  const gross = data.reduce((s, r) => s + (r.faturamento || 0), 0);
  // Net not computed separately in backend yet; keep same as gross for now
  const net = gross;
  return { gross, net };
}

export async function getTopProducts({ days = 30, limit = 5, store, channel } = {}) {
  const today = new Date();
  const start = new Date();
  start.setDate(start.getDate() - days);
  const params = { start: fmt(start), end: fmt(today), limit };
  if (store) params.store = store;
  if (channel) params.channel = channel;
  const resp = await api.get("/metrics/top-products/", { params });
  const data = resp.data || [];
  // normalize backend keys to component expectations: { name, quantity, revenue }
  return data.map((p) => ({
    id: p.product__id || p.product_id,
    name: p.product__name || p.name || "-",
    category: p.product__category || p.category || null,
    quantity: p.unidades_vendidas || p.quantity || 0,
    revenue: Number(p.receita || p.revenue || 0),
  }));
}

export async function getPeakHours({ days = 30, store, channel } = {}) {
  const today = new Date();
  const start = new Date();
  start.setDate(start.getDate() - days);
  const params = { start: fmt(start), end: fmt(today) };
  if (store) params.store = store;
  if (channel) params.channel = channel;
  const resp = await api.get("/metrics/peak-hours/", { params });
  const data = resp.data || [];
  // Backend returns 'hour' as ISO datetime string truncated to the hour and 'pedidos'
  return data.map((h) => {
    const hourRaw = h.hour;
    let hourInt = null;
    try {
      // hourRaw may be like '2025-10-01T14:00:00Z' or without timezone
      const d = new Date(hourRaw);
      if (!isNaN(d.getTime())) hourInt = d.getUTCHours();
      else hourInt = null;
    } catch (e) {
      hourInt = null;
    }
    return { hour: hourInt, count: h.pedidos || h.count || 0, revenue: Number(h.receita || 0) };
  });
}

export async function getStores() {
  const resp = await api.get('/stores/');
  return resp.data || [];
}

export async function getChannels() {
  const resp = await api.get('/channels/');
  return resp.data || [];
}

export function exportCsvUrl(type, params = {}) {
  const search = new URLSearchParams({ type, ...params }).toString();
  return `/api/metrics/export-csv/?${search}`;
}

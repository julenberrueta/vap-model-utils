/* ========= Helpers ========= */
function fmt(ts) {
  const d = new Date(ts);
  const pad = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}
function nearestTs(ts, tsList) {
  let lo = 0, hi = tsList.length - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (tsList[mid] < ts) lo = mid + 1; else hi = mid;
  }
  const cand1 = tsList[lo];
  const cand0 = tsList[Math.max(0, lo-1)];
  return (Math.abs(cand1 - ts) < Math.abs(cand0 - ts)) ? cand1 : cand0;
}

/* ========= Sincronizar tooltips/crosshair (Rect1 y Rect2) ========= */
function initSyncTooltipsOnce() {
  if (window._hcSyncInit) return;
  window._hcSyncInit = true;

  (function (H) {
    H.Pointer.prototype.reset = function () { return undefined; };
    H.Point.prototype.highlight = function (event) {
      this.onMouseOver();
      this.series.chart.tooltip.refresh(this, event);
      this.series.chart.xAxis[0].drawCrosshair(event, this);
    };
  })(Highcharts);

  const sync = (e) => {
    Highcharts.charts.forEach((chart) => {
      if (!chart) return;
      const xa = chart.xAxis && chart.xAxis[0];
      if (!xa || xa.options.type !== 'datetime') return;  // ⬅️ solo línea/área (Rect1/Rect2)
      const ev = chart.pointer.normalize(e);
      const s0 = chart.series && chart.series[0];
      if (!s0) return;
      const point = s0.searchPoint(ev, true);
      if (point) point.highlight(ev);
    });
  };

  ['mousemove','touchmove','touchstart'].forEach(evt =>
    document.addEventListener(evt, sync, { passive: true })
  );

  document.addEventListener('mouseleave', () => {
    Highcharts.charts.forEach((chart) => {
      if (!chart) return;
      const xa = chart.xAxis && chart.xAxis[0];
      if (!xa || xa.options.type !== 'datetime') return;
      chart.tooltip.hide();
      xa.hideCrosshair();
    });
  });
}

/* ========= Carga de datos común para Rect3 ========= */
const VARIABLES = ['peep_max', 'Age', 'pcr_median', 'antibioticos', 'temperatura_max', 'fio2_max', 'fr_min', 'fio2_median', 'pcr_min', 'peep_median', 'aspecto_secreciones_purulentas', 'spo2_median', 'pr_plateau_min', 'pcr_max', 'temperatura_median', 'fio2_min', 'pafi_min', 'linfocitos_min', 'pr_plateau_median', 'pr_peak_median', 'fr_median', 'pam_min', 'noradrenalina_sum', 'linfocitos_median', 'pafi_median', 'linfocitos_max', 'pr_peak_max', 'peep_min', 'pam_median', 'pr_peak_min', 'pafi_max', 'leucocitos_min', 'PatType_surgical', 'leucocitos_max', 'leucocitos_median', 'traqueo'];

let HC_DATA = null; // { tsList:[], byTs:Map, lastTs:number }
async function loadDataOnce() {
  if (HC_DATA) return HC_DATA;
  let raw;
  if (window.DATA) {
    raw = window.DATA; // por si usas data.js
  } else {
    const res = await fetch('./data/data.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`No se pudo cargar ./data/data.json (HTTP ${res.status})`);
    raw = await res.json();
  }
  const pac = raw['10001'];
  const records = [];
  for (const fecha in pac) {
    const horas = pac[fecha];
    for (const hora in horas) {
      const ts = new Date(`${fecha}T${hora}:00`).getTime();
      records.push({
        ts,
        variables: horas[hora].variables,
        prob: horas[hora].probabilidad
      });
    }
  }
  records.sort((a,b)=>a.ts-b.ts);
  const tsList = records.map(r=>r.ts);
  const byTs = new Map(records.map(r => [r.ts, r]));
  HC_DATA = { tsList, byTs, lastTs: tsList[tsList.length-1] };
  return HC_DATA;
}

async function updateHeader(ts) {
  const ds = await loadDataOnce();
  const selTs = nearestTs(ts, ds.tsList);
  const rec = ds.byTs.get(selTs);

  const elDate = document.getElementById('box-info-date');
  const elProb = document.getElementById('box-info-prob');

  if (elDate) elDate.textContent = fmt(selTs);
  if (elProb) elProb.textContent = `Probabilidad: ${(rec?.prob ?? 0).toFixed(2)}`;
}

/* ========= Rect1: Probabilidad ========= */
async function drawChartInRect1() {
  const containerId = 'hc-rect1';
  const el = document.getElementById(containerId);

  const res = await fetch('./data/data.json', { cache: 'no-store' });
  if (!res.ok) { el.innerHTML = `<div class="p-3 text-danger">Error JSON (HTTP ${res.status}).</div>`; return; }
  const data = await res.json();
  const paciente = data['10001'];

  let points = [];
  for (const fecha in paciente) {
    const horas = paciente[fecha];
    for (const hora in horas) {
      const prob = pacientesafe(paciente[fecha][hora]?.probabilidad);
      const ts = new Date(`${fecha}T${hora}:00`).getTime();
      points.push({ x: ts, y: prob });
    }
  }
  points.sort((a,b)=>a.x-b.x);

  Highcharts.setOptions({ time: { useUTC: true } });
  const chart = Highcharts.chart(containerId, {
    chart: {
      marginTop: 24,
      reflow: true,
      type: 'line',
      zoomType: 'x',
      backgroundColor: 'transparent',
      plotBackgroundColor: 'transparent',
      spacing: [0,0,0,0],
      margin: [10, 10, 35, 48], // top, right, bottom, left
      events: {
        click: function (e) {
          const x = e.xAxis && e.xAxis.length ? e.xAxis[0].value : undefined;
          if (typeof x !== 'undefined') { console.log(`[Rect1] Click: ${fmt(x)}`); selectTs(x); }
        }
      }
    },
    title: {
      text: 'VAP probability',
      align: 'center'
    },
    xAxis: { type: 'datetime', title: { text: 'Fecha' }, crosshair: { width: 1 } },
    yAxis: {
      min: 0,
      max: 1,
      tickInterval: 0.1,
      title: { text: 'Probabilidad' },
      plotLines: [{
        value: 0.5,                           // ← línea horizontal en y=0.5
        color: '#9aa0a6',
        width: 2,
        dashStyle: 'ShortDash',
        zIndex: 5,
        label: {
          text: '0.5',
          align: 'right',
          x: -10, y: -6,
          style: { color: '#9aa0a6' }
        }
      }]
    },
    legend: { enabled: false },
    tooltip: { xDateFormat: '%Y-%m-%d %H:%M', pointFormat: 'Probabilidad: <b>{point.y:.3f}</b>' },
    series: [{
      name: 'Probabilidad',
      data: points,
      lineWidth: 3,
      color: '#A8E6A3',
      zones: [
        { value: 0.25, color: '#A8E6A3' },
        { value: 0.40, color: '#FFF3B0' },
        { value: 0.50, color: '#FFD59E' },
        {              color: '#FFB3B3' }
      ],
      point: {
        events: {
          click: function () { console.log(`[Rect1] Punto: ${fmt(this.x)} | prob=${this.y}`); selectTs(this.x); }
        }
      }
    }],
    credits: { enabled: false }
  });
  el.chart = chart;
  initSyncTooltipsOnce();
}
function pacientesafe(v){ return typeof v === 'number' ? v : 0; }

/* ========= Rect2: Antibióticos (área) ========= */
async function drawAntibioticosInRect2() {
  const containerId = 'hc-rect2';
  const el = document.getElementById(containerId);

  const res = await fetch('./data/antibioticos.json', { cache: 'no-store' });
  if (!res.ok) { el.innerHTML = `<div class="p-3 text-danger">Error JSON (HTTP ${res.status}).</div>`; return; }
  const data = await res.json();
  const paciente = data['10001'];

  const points = [];
  for (const fecha in paciente) {
    const horas = paciente[fecha];
    for (const hora in horas) {
      const dias = paciente[fecha][hora]?.dias_acumulados ?? 0;
      const ts = new Date(`${fecha}T${hora}:00`).getTime();
      points.push({ x: ts, y: dias });
    }
  }
  points.sort((a,b)=>a.x-b.x);

  Highcharts.setOptions({ time: { useUTC: true } });
  const chart = Highcharts.chart(containerId, {
    chart: {
      marginTop: 24,
      reflow: true,
      type: 'area',
      zoomType: 'x',
      backgroundColor: 'transparent',
      plotBackgroundColor: 'transparent',
      spacing: [0,0,0,0],
      margin: [10, 10, 35, 48],
      events: {
        click: function (e) {
          const x = e.xAxis && e.xAxis.length ? e.xAxis[0].value : undefined;
          if (typeof x !== 'undefined') { console.log(`[Rect2] Click: ${fmt(x)}`); selectTs(x); }
        }
      }
    },
    title: {
      text: 'Cumulative days of antibiotic use',
      align: 'center'
    },
    xAxis: { type: 'datetime', title: { text: 'Fecha' }, crosshair: { width: 1 } },
    yAxis: {
      max: 10,
      title: { text: 'Días acumulados' },
      gridLineWidth: 1,
      plotLines: [{
        value: 7,
        color: '#9aa0a6',
        width: 2,
        dashStyle: 'ShortDash',
        zIndex: 5,
        label: {
          text: '7 días',
          align: 'right',
          x: -10, y: -6,
          style: { color: '#9aa0a6' }
        }
      }]
    },
    legend: { enabled: false },
    tooltip: { xDateFormat: '%Y-%m-%d %H:%M', pointFormat: 'Días acumulados: <b>{point.y:.3f}</b>' },
    series: [{
      name: 'Antibióticos (días)',
      data: points,
      lineWidth: 3,
      color: '#B3E5FC',
      fillOpacity: 0.4,
      fillColor: '#B3E5FC',
      point: {
        events: {
          click: function () { console.log(`[Rect2] Punto: ${fmt(this.x)} | días=${this.y}`); selectTs(this.x); }
        }
      }
    }],
    credits: { enabled: false }
  });
  el.chart = chart;
  initSyncTooltipsOnce();
}

/* ========= Rect3: Barras horizontales SHAP (variables en vertical) ========= */
function buildShapData(record) {
  const categories = [...VARIABLES];
  const data = categories.map(v => {
    const info = record.variables[v] || { shap: 0, valor: '' };
    const y = Number(info.shap) || 0; // SHAP ∈ [-1,1]
    const actual = (info.valor === undefined) ? '' :
      (typeof info.valor === 'number' && !Number.isInteger(info.valor) ? info.valor.toFixed(2) : String(info.valor));
    const pos = y >= 0;
    return {
      y, name: v, actual,
      color: pos ? '#A8E6A3' : '#FFB3B3',
      dataLabels: {
        enabled: true,
        inside: false,
        align: pos ? 'left' : 'right',
        x: pos ? 6 : -6,
        style: { textOutline: 'none', color: '#000' },
        formatter: function(){ return this.point.actual; }
      }
    };
  });
  const maxAbs = Math.max(1, Math.ceil((Math.max(...data.map(p => Math.abs(p.y))) + 0.1) * 10) / 10);
  return { categories, data, maxAbs };
}

async function drawShapBarsInRect3(initialTs = null) {
  const containerId = 'hc-rect3';
  const el = document.getElementById(containerId);

  const ds = await loadDataOnce();  // usa tu loader existente
  const targetTs = initialTs ?? ds.lastTs;
  await renderShapChart(containerId, nearestTs(targetTs, ds.tsList));
}

async function renderShapChart(containerId, selTs) {
  const ds = await loadDataOnce();
  const record = ds.byTs.get(selTs);
  const { categories, data, maxAbs } = buildShapData(record);

  Highcharts.setOptions({ time: { useUTC: true } });

  // Altura dinámica para que no se “coman” categorías
  const ROW_H = 26, PAD = 140;
  const wantedH = categories.length * ROW_H + PAD;
  const chartHeight = Math.max(440, Math.min(wantedH, 1000));

  const chart = Highcharts.chart(containerId, {
    chart: {
      reflow: true,
      type: 'column',
      inverted: true,
      height: chartHeight,
      scrollablePlotArea: { minHeight: Math.max(wantedH, 600) },
      backgroundColor: 'transparent',
      plotBackgroundColor: 'transparent',
      spacing: [0,0,0,0],
      marginLeft: 200,   // más espacio para variables largas
      marginRight: 10,
      marginTop: 6,
      marginBottom: 12,
      events: {
        click: function (e) {
          const x = e.xAxis && e.xAxis.length ? e.xAxis[0].value : undefined;
          if (typeof x !== 'undefined') console.log(`[Rect3] Click: ${fmt(x)}`);
        }
      }
    },
    title: {
      text: 'SHAP values',
      align: 'left'
    },
    credits: { enabled: false },
    // Con inverted:true, el eje de categorías es xAxis (vertical)
    xAxis: {
      categories,
      title: { text: '' },
      tickLength: 0
    },
    // Y el eje numérico (SHAP) es yAxis (horizontal)
    yAxis: {
      min: -maxAbs, max: maxAbs,
      title: { text: 'Valor SHAP' },
      tickInterval: 0.5,
      gridLineColor: 'white', gridLineWidth: 1,
      plotLines: [{ value: 0, width: 1, color: '#9aa0a6', zIndex: 3 }]
    },
    tooltip: {
      formatter: function () {
        return `<b>${this.point.name}</b><br>SHAP: <b>${this.y}</b><br>Valor: <b>${this.point.actual}</b>`;
      }
    },
    legend: { enabled: false },
    plotOptions: {
      series: {
        point: {
          events: {
            click: function () {
              console.log(`[Rect3] Punto: ${this.name} @ ${fmt(selTs)} | shap=${this.y} | valor=${this.actual}`);
            }
          }
        },
        dataLabels: {
          enabled: true,          // por si algún punto no trae su propio dataLabel
          inside: false,
          style: { textOutline: 'none' },
          formatter: function () {
            const v = this.point.actual;
            if (v === null || v === undefined || v === '') return '';
            return v;
          }
        }
      }
    },
    series: [{
      name: 'SHAP',
      data // una sola serie, cada punto ya lleva color según signo
    }]
  });

  document.getElementById(containerId).chart = chart;
  window._hc_selectedTs = selTs;
}

/* Mantén tu selectTs existente; si no, usa este: */
async function selectTs(ts) {
  const ds = await loadDataOnce();
  const selTs = nearestTs(ts, ds.tsList);
  await renderShapChart('hc-rect3', selTs);
  updateHeader(selTs);
}


/* ========= Lanzar todo al cargar ========= */
window.addEventListener('DOMContentLoaded', async () => {
  // pinta las gráficas (no hace falta esperar a las de la izda)
  drawChartInRect1();
  drawAntibioticosInRect2();

  // garantiza datos cargados y el SHAP dibujado
  const ds = await loadDataOnce();
  await drawShapBarsInRect3(ds.lastTs);

  // ahora sí: panel con última fecha/prob
  updateHeader(ds.lastTs);
});

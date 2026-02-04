// js/airportsTable.js

const DATA_URL = "http://127.0.0.1:5500/JSONs/airports.json";
const ROOT_ID = "airports-root";


const COLS = [
  "ident", "name", "type", "municipality",
  "iso_region", "iso_country", "iata_code", "icao_code",
  "latitude_deg", "longitude_deg", "elevation_ft"
];

fetch(DATA_URL)
  .then((r) => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  })
  .then((data) => {
    // data is like { "KATL": {...}, "KJFK": {...}, ... }
    const rows = Object.values(data);

    const root = document.getElementById(ROOT_ID);
    if (!root) return;

    const head = `<tr>${COLS.map(c => `<th>${c}</th>`).join("")}</tr>`;
    const body = rows.map((a) =>
      `<tr>${COLS.map(c => `<td>${a?.[c] ?? ""}</td>`).join("")}</tr>`
    ).join("");

    root.innerHTML = `
      <table border="1" cellspacing="0" cellpadding="6">
        <thead>${head}</thead>
        <tbody>${body}</tbody>
      </table>
    `;
  })
  .catch((e) => {
    const root = document.getElementById(ROOT_ID);
    if (root) root.textContent = `Failed to load airports: ${e.message}`;
    console.error(e);
  });

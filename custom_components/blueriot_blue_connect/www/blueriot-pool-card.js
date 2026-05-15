/**
 * Blueriot Blue Connect Pool Card
 * A custom Lovelace card for visualizing Blue Connect pool water data.
 */

class BlueriotPoolCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._entities = [];
  }

  static getStubConfig() {
    return { title: "Pool Monitor" };
  }

  static getConfigElement() {
    return document.createElement("blueriot-pool-card-editor");
  }

  setConfig(config) {
    this._config = config || {};
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  // ── Helpers ────────────────────────────────────────────────────────────────

  _isBlueriiotEntity(s) {
    // 1. Match by integration platform (HA entity registry, 2023+)
    const entry = this._hass.entities?.[s.entity_id];
    if (entry?.platform === "blueriot_blue_connect") return true;
    // 2. Match by unique attributes our sensors always expose
    if ("issuer" in (s.attributes || {})) return true;
    if ("ok_min" in (s.attributes || {}) && "ok_max" in (s.attributes || {})) return true;
    // 3. Fallback: entity_id name patterns
    return (
      s.entity_id.includes("blueriot") ||
      s.entity_id.includes("blue_connect")
    );
  }

  _getMeasurements() {
    if (!this._hass) return [];
    return Object.values(this._hass.states).filter(
      (s) =>
        s.attributes.device_class !== "timestamp" &&
        s.entity_id.startsWith("sensor.") &&
        this._isBlueriiotEntity(s) &&
        s.state !== "unavailable" &&
        s.state !== "unknown"
    );
  }

  _getTimestamps() {
    if (!this._hass) return [];
    return Object.values(this._hass.states).filter(
      (s) =>
        s.attributes.device_class === "timestamp" &&
        s.entity_id.startsWith("sensor.") &&
        this._isBlueriiotEntity(s)
    );
  }

  _statusColor(state) {
    const val = parseFloat(state.state);
    if (isNaN(val)) return "var(--secondary-text-color)";

    const okMin = parseFloat(state.attributes.ok_min);
    const okMax = parseFloat(state.attributes.ok_max);
    const warnLow = parseFloat(state.attributes.warning_low);
    const warnHigh = parseFloat(state.attributes.warning_high);

    if (!isNaN(okMin) && !isNaN(okMax)) {
      if (val >= okMin && val <= okMax)
        return "var(--success-color, #4caf50)";
      if (!isNaN(warnLow) && !isNaN(warnHigh) && val >= warnLow && val <= warnHigh)
        return "var(--warning-color, #ff9800)";
      return "var(--error-color, #f44336)";
    }
    return "var(--primary-text-color)";
  }

  _statusIcon(state) {
    const val = parseFloat(state.state);
    if (isNaN(val)) return "";
    const okMin = parseFloat(state.attributes.ok_min);
    const okMax = parseFloat(state.attributes.ok_max);
    const warnLow = parseFloat(state.attributes.warning_low);
    const warnHigh = parseFloat(state.attributes.warning_high);

    if (!isNaN(okMin) && !isNaN(okMax)) {
      if (val >= okMin && val <= okMax) return "✓";
      if (!isNaN(warnLow) && !isNaN(warnHigh) && val >= warnLow && val <= warnHigh)
        return "⚠";
      return "✕";
    }
    return "";
  }

  _shortName(state) {
    const friendly = state.attributes.friendly_name || state.entity_id;
    // Strip the device name prefix (everything up to the last space-separated measurement)
    const parts = friendly.split(" ");
    return parts[parts.length - 1];
  }

  _formatValue(state) {
    const val = parseFloat(state.state);
    if (isNaN(val)) return state.state;
    if (Math.abs(val) >= 100) return Math.round(val).toString();
    if (Number.isInteger(val)) return val.toString();
    return val.toFixed(1);
  }

  _formatTimestamp(isoString) {
    if (!isoString || isoString === "unavailable" || isoString === "unknown")
      return null;
    try {
      return new Date(isoString).toLocaleString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return null;
    }
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  _render() {
    const measurements = this._getMeasurements();
    const timestamps = this._getTimestamps();
    const title = this._config.title || "Pool Monitor";

    // Primary metrics shown large (first row)
    const primaryKeys = ["ph", "temperature", "orp"];
    const primary = measurements.filter((s) =>
      primaryKeys.some((k) => s.entity_id.toLowerCase().includes(k))
    );
    const secondary = measurements.filter(
      (s) => !primaryKeys.some((k) => s.entity_id.toLowerCase().includes(k))
    );

    const lastTs = timestamps
      .map((s) => this._formatTimestamp(s.state))
      .filter(Boolean)[0];

    const primaryHtml = primary
      .map((s) => {
        const color = this._statusColor(s);
        const badge = this._statusIcon(s);
        return `
        <div class="primary-card">
          <div class="primary-name">${this._shortName(s)}</div>
          <div class="primary-value" style="color:${color}">
            ${this._formatValue(s)}
            <span class="primary-badge" style="color:${color}">${badge}</span>
          </div>
          <div class="primary-unit">${s.attributes.unit_of_measurement || ""}</div>
        </div>`;
      })
      .join("");

    const secondaryHtml = secondary
      .map((s) => {
        const color = this._statusColor(s);
        const badge = this._statusIcon(s);
        return `
        <div class="sec-card">
          <div class="sec-name">${this._shortName(s)}</div>
          <div class="sec-value" style="color:${color}">
            ${this._formatValue(s)}<span class="sec-unit"> ${s.attributes.unit_of_measurement || ""}</span>
          </div>
          <span class="sec-badge" style="color:${color}">${badge}</span>
        </div>`;
      })
      .join("");

    const legendHtml = `
      <div class="legend">
        <span class="legend-dot" style="background:var(--success-color,#4caf50)"></span>OK
        <span class="legend-dot" style="background:var(--warning-color,#ff9800)"></span>Warning
        <span class="legend-dot" style="background:var(--error-color,#f44336)"></span>Out of range
      </div>`;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }

        ha-card {
          padding: 16px 16px 12px;
          overflow: hidden;
        }

        /* ── Header ── */
        .header {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 16px;
        }
        .header-icon {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: var(--primary-color);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          flex-shrink: 0;
        }
        .title {
          font-size: 1.15em;
          font-weight: 600;
          color: var(--primary-text-color);
          flex: 1;
        }
        .subtitle {
          font-size: 0.75em;
          color: var(--secondary-text-color);
          margin-top: 1px;
        }

        /* ── Primary metrics ── */
        .primary-row {
          display: flex;
          gap: 10px;
          margin-bottom: 14px;
        }
        .primary-card {
          flex: 1;
          background: var(--secondary-background-color);
          border-radius: 14px;
          padding: 14px 10px 10px;
          text-align: center;
          min-width: 0;
        }
        .primary-name {
          font-size: 0.7em;
          text-transform: uppercase;
          letter-spacing: 0.8px;
          color: var(--secondary-text-color);
          margin-bottom: 6px;
        }
        .primary-value {
          font-size: 1.9em;
          font-weight: 700;
          line-height: 1;
          position: relative;
        }
        .primary-badge {
          font-size: 0.4em;
          vertical-align: super;
          font-weight: 400;
        }
        .primary-unit {
          font-size: 0.7em;
          color: var(--secondary-text-color);
          margin-top: 4px;
        }

        /* ── Secondary metrics ── */
        .section-label {
          font-size: 0.7em;
          text-transform: uppercase;
          letter-spacing: 0.8px;
          color: var(--secondary-text-color);
          margin-bottom: 8px;
        }
        .secondary-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
          gap: 8px;
          margin-bottom: 12px;
        }
        .sec-card {
          background: var(--secondary-background-color);
          border-radius: 10px;
          padding: 10px 8px 8px;
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          position: relative;
        }
        .sec-name {
          font-size: 0.68em;
          text-transform: uppercase;
          letter-spacing: 0.6px;
          color: var(--secondary-text-color);
          margin-bottom: 4px;
        }
        .sec-value {
          font-size: 1.05em;
          font-weight: 600;
        }
        .sec-unit {
          font-size: 0.7em;
          font-weight: 400;
          color: var(--secondary-text-color);
        }
        .sec-badge {
          font-size: 0.65em;
          position: absolute;
          top: 6px;
          right: 8px;
        }

        /* ── Footer ── */
        .footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-top: 8px;
          flex-wrap: wrap;
          gap: 6px;
        }
        .legend {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.7em;
          color: var(--secondary-text-color);
        }
        .legend-dot {
          display: inline-block;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-left: 6px;
        }
        .legend-dot:first-child { margin-left: 0; }
        .last-update {
          font-size: 0.7em;
          color: var(--secondary-text-color);
        }

        .empty {
          color: var(--secondary-text-color);
          font-size: 0.9em;
          padding: 12px 0;
          text-align: center;
        }
      </style>

      <ha-card>
        <div class="header">
          <div class="header-icon">🏊</div>
          <div>
            <div class="title">${title}</div>
            <div class="subtitle">Blue Connect</div>
          </div>
        </div>

        ${
          measurements.length === 0
            ? (() => {
                // Debug: show first 5 sensor entity_ids + their platform to help diagnose
                const allSensors = this._hass
                  ? Object.values(this._hass.states)
                      .filter((s) => s.entity_id.startsWith("sensor."))
                      .slice(0, 8)
                      .map((s) => {
                        const plat = this._hass.entities?.[s.entity_id]?.platform || "?";
                        const hasIssuer = "issuer" in (s.attributes || {});
                        const hasOkMin = "ok_min" in (s.attributes || {});
                        return `${s.entity_id} [platform=${plat}, issuer=${hasIssuer}, ok_min=${hasOkMin}]`;
                      })
                  : [];
                return `<div class="empty">
                  <div>No sensor data found.</div>
                  <details style="text-align:left;font-size:0.75em;margin-top:8px;">
                    <summary>Debug — first sensors visible</summary>
                    <pre style="white-space:pre-wrap;word-break:break-all;">${allSensors.join("\n") || "(none)"}</pre>
                  </details>
                </div>`;
              })()
            : `
          ${primary.length > 0 ? `<div class="primary-row">${primaryHtml}</div>` : ""}
          ${
            secondary.length > 0
              ? `
            <div class="section-label">All measurements</div>
            <div class="secondary-grid">${secondaryHtml}</div>
          `
              : ""
          }
        `
        }

        <div class="footer">
          ${legendHtml}
          ${lastTs ? `<div class="last-update">Updated ${lastTs}</div>` : ""}
        </div>
      </ha-card>
    `;
  }
}

customElements.define("blueriot-pool-card", BlueriotPoolCard);

// ── Visual editor ──────────────────────────────────────────────────────────────

class BlueriotPoolCardEditor extends HTMLElement {
  connectedCallback() {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: "open" });
    }
    this._render();
  }

  setConfig(config) {
    this._config = config || {};
    this._render();
  }

  _render() {
    if (!this.shadowRoot) return;
    const title = this._config?.title || "";
    this.shadowRoot.innerHTML = `
      <style>
        .editor-row {
          display: flex;
          align-items: center;
          padding: 8px 16px;
          gap: 12px;
        }
        label {
          flex: 0 0 80px;
          font-size: 0.9em;
          color: var(--secondary-text-color);
        }
        input {
          flex: 1;
          padding: 6px 10px;
          border: 1px solid var(--divider-color, #ccc);
          border-radius: 6px;
          background: var(--card-background-color, #fff);
          color: var(--primary-text-color);
          font-size: 0.95em;
        }
      </style>
      <div class="editor-row">
        <label>Title</label>
        <input id="title" type="text" .value="${title}" placeholder="Pool Monitor" />
      </div>
    `;
    this.shadowRoot.getElementById("title").addEventListener("input", (e) => {
      this.dispatchEvent(
        new CustomEvent("config-changed", {
          detail: { config: { ...this._config, title: e.target.value } },
          bubbles: true,
          composed: true,
        })
      );
    });
  }
}

customElements.define("blueriot-pool-card-editor", BlueriotPoolCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "blueriot-pool-card",
  name: "Blue Connect Pool Card",
  description: "Pool water quality dashboard for Blue Connect devices",
  preview: true,
  documentationURL: "https://github.com/Joachimdj/blueriiot-hass-api-integration",
});

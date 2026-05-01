# Phase 8 Change Log — Streamlit Frontend

**Tarih:** 2026-05-01  
**Phase:** 08 — Streamlit Frontend  
**Durum:** Tamamlandı. GSD `SUMMARY.md`, `STATE.md`, `ROADMAP.md` güncellendi.

## Kısa Özet

Bu phase'de Apex'in 4-sayfalık Streamlit MVP frontend'i oluşturuldu. Dark mode tema, Plotly tabanlı finans grafikleri, FastAPI backend entegrasyonu ve structlog → Grafana log akışı kuruldu. Orijinal plana ek olarak OHLCV endpoint'i ve Yahoo Finance tarzı mountain+volume chart eklendi.

## Commit'ler

| Commit | Amaç |
|---|---|
| `7d750af` | `.streamlit/config.toml` dark tema, `app.py` entry point, `api_client.py` |
| `1e5a347` | Plotly dark chart factory'leri ve signal card component'leri |
| `eeeb8ce` | 4 sayfa: Dashboard, Ledger, Detail, Backtest |
| `7fdf406` | `GET /api/v1/ohlcv/{ticker}` endpoint, structlog logları, Ledger/Detail gerçek veriye bağlandı |
| `4390f71` | Mountain+volume dual-panel chart (Yahoo Finance stili) |

## Değişen / Eklenen Dosyalar

### Streamlit Konfigürasyon

#### `.streamlit/config.toml` *(yeni)*

Dark base tema, teal aksanı (`#00D4AA`), monospace font. `gatherUsageStats = false`.

---

### Frontend Entry Point

#### `src/apex/frontend/app.py` *(yeni)*

`st.set_page_config` ile wide layout, dark icon. Session state'i bir kez init eder (`selected_ticker`, `last_analysis`). Sidebar navigasyonu içerir.

---

### API Client

#### `src/apex/frontend/api_client.py` *(yeni)*

FastAPI backend'e httpx ile bağlanır. Tüm fonksiyonlar `@st.cache_data` ile cache'lenir.

| Fonksiyon | Endpoint | TTL |
|---|---|---|
| `fetch_analysis(ticker)` | `POST /api/v1/analyze/{ticker}` | 60s |
| `fetch_health()` | `GET /health` | 30s |
| `fetch_ohlcv(ticker, days)` | `GET /api/v1/ohlcv/{ticker}` | 300s |

Backend offline olduğunda `None` / `[]` döner, sayfalar graceful degradation gösterir.

---

### Components

#### `src/apex/frontend/components/charts.py` *(yeni)*

Tüm chart'lar `plotly_dark` template kullanır.

**`candlestick_chart`** — Mountain+volume dual-panel (Yahoo Finance stili):
- Üst panel (%72): Mavi filled area line, OHLCV hover tooltip (O/H/L/C/V)
- Alt panel (%25): Volume histogram — yeşil = yükselen gün, kırmızı = düşen gün
- Sağ tarafta fiyat ekseni, `xaxis_rangeslider` kapalı

**`price_band_chart`** — Teal filled area line, Ledger sayfası için.

**`backtest_equity_chart`** — Equity curve, Backtest sayfası için.

#### `src/apex/frontend/components/cards.py` *(yeni)*

**`signal_hero_card`** — BUY/SELL/HOLD renk kodlu büyük hero card (yeşil/kırmızı/sarı).

**`agent_decision_card`** — Her agent için sinyal + confidence + reasoning özeti.

---

### Sayfalar

#### `src/apex/frontend/pages/1_Dashboard.py` *(yeni)*

- Backend health indicator (🟢/🔴)
- Ticker arama + Analyse butonu
- `signal_hero_card` ile son analiz sonucu
- 4 metrik: Signal, Confidence, Total Tokens, Cost USD
- Session-based analiz geçmişi tablosu (son 20)

#### `src/apex/frontend/pages/2_Ledger.py` *(yeni)*

- Filtreler: tarih aralığı, sinyal tipi (multiselect), ticker
- `GET /api/v1/ohlcv/{ticker}` ile gerçek fiyat grafiği
- Filtrelenmiş analiz geçmişi tablosu

#### `src/apex/frontend/pages/3_Detail.py` *(yeni)*

- Mountain+volume candlestick chart (gerçek OHLCV, offline'da synthetic fallback)
- `signal_hero_card` ile ticker özeti
- 4 agent kararı 2 kolonlu grid'de (`agent_decision_card`)
- Workflow hata listesi

#### `src/apex/frontend/pages/4_Backtest.py` *(yeni)*

- `st.form`: ticker, tarih aralığı, başlangıç sermayesi, min confidence threshold
- 4 sonuç metriği: Total Return, Sharpe Ratio, Max Drawdown, Win Rate
- Equity curve chart
- Trade tablosu (tarih, sinyal, fiyat, P&L)

---

### Backend Değişiklikleri

#### `src/apex/api/routes/analysis.py` *(güncellendi)*

- `GET /api/v1/ohlcv/{ticker}?days=N` endpoint'i eklendi
- `_default_market_data` fonksiyonu `days` parametresi aldı
- `analyze_ticker` ve `get_ohlcv`'ye structlog eklendi:
  - `analysis.request`, `analysis.rejected`, `analysis.complete` event'leri
  - `ohlcv.request`, `ohlcv.response` event'leri
  - Log field'ları: `ticker`, `signal`, `confidence`, `total_tokens`, `cost_usd`, `bar_count`
- Loglar stdout → Promtail → Loki → Grafana akışına dahil

---

## Ekstra (Orijinal Plan Dışı)

| Ekstra | Açıklama |
|---|---|
| `fetch_ohlcv` + OHLCV endpoint | Ledger/Detail sayfaları gerçek fiyat verisi alıyor |
| structlog log event'leri | Her analiz ve OHLCV isteği Grafana'da izlenebilir |
| Mountain+volume chart | Yahoo Finance tarzı dual-panel, referans screenshot'a göre yapıldı |
| `10-PLAN-02.md` NextJS notu | lightweight-charts + WebSocket + TradingView kalitesi için Phase 10 sonrası plan |

---

## Notlar

- OHLCV endpoint şu an synthetic data döndürüyor. Gerçek DB bağlantısı Phase 10'da yapılacak (`10-PLAN-02.md` task 4).
- NextJS + lightweight-charts migrasyonu v1.0 sonrası için `10-PLAN-02.md`'ye detaylı not olarak eklendi.
- Backtest sayfası tamamen local (deterministic stub) — gerçek backtest engine Phase 10 kapsamında değil, v2'ye bırakıldı.

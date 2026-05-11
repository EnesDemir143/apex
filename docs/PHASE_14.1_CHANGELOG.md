# Phase 14.1 Change Log — TUI Market Panel + Terminal Chart

**Tarih:** 2026-05-06
**Phase:** 14.1 — TUI Market Panel + Terminal Chart
**Durum:** Tamamlandı

## Kısa Özet

Phase 14'teki placeholder MarketPanel gerçek OHLCV verisiyle beslendi ve terminal-native `/chart` ekranı eklendi:

- `market_snapshot` servisi: LLM/FastAPI gerektirmeden yerel OHLCV + indikatör özeti
- `MarketPanel` artık seçili ticker'ın canlı/fallback snapshot'ını gösteriyor
- `/chart [TICKER]` komutu: investing.com tarzı terminal chart ekranı açıyor
- ChartPanel: mum grafiği, volume, RSI/MACD alt paneli, crosshair, bar-inspect modu
- Timeframe seçimi (1m/5m/1h/1d), zoom, pan, bar-inspect (Tab ile gezinme)
- `/x` → `/inspect` yeniden adlandırma; Tab wrap-around düzeltmesi
- Chart-only slash dropdown: ChartScreen'de sadece chart komutları görünüyor

## Commit'ler

| Commit | Amaç |
|---|---|
| `913e510` | market-snapshot service (fallback + indikatör özeti) |
| `c0b8fbe` | MarketPanel wiring + ChartPanel + KeybindPanel widget'ları + state/tcss |
| `7e355e1` | ChartScreen + /chart komutu + routing |
| `0090fa8` | Chart UX polish (inspect rename, tab wrap, chart-only dropdown) |
| `87ae253` | Testler (market_snapshot + tui_app + tui_commands) |

## Değişen / Eklenen Dosyalar

### Services

#### `src/apex/services/market_snapshot.py` *(yeni)*

Ne yaptığı:

- `MarketSnapshot` dataclass: ticker, bars, latest OHLCV, `IndicatorSummary`, source label
- `get_market_snapshot(ticker, days)` async: `MarketDataFetcher` üzerinden veri çeker, başarısız olursa deterministik sentetik bar'larla fallback yapar
- `IndicatorSummary`: RSI, MACD/signal, Bollinger bands, SMA20, EMA26
- Whitelist dışı ticker'ı `local_analysis` ile tutarlı biçimde reddeder
- LLM çağrısı yok, FastAPI bağımlılığı yok

Neden:

- MarketPanel ve ChartPanel'in ortak veri kaynağı; test edilebilir, ağ bağımsız

### TUI Layer

#### `src/apex/tui/state.py` *(güncellendi)*

Ne yaptığı:

- `ChartViewport` dataclass: timeframe, viewport_bars, offset
- `TuiState.chart` alanı eklendi

#### `src/apex/tui/apex.tcss` *(güncellendi)*

Ne yaptığı:

- ChartPanel layout stilleri: header, body, date-axis, bar-info, volume, sub-panel

#### `src/apex/tui/widgets.py` *(güncellendi)*

Ne yaptığı:

- `MarketPanel`: placeholder yerine reactive snapshot; loading/error durumları; ticker değişince otomatik yenileme
- `ChartPanel`: terminal-native chart widget
  - Mum grafiği (Unicode block chars), fiyat ekseni, tarih ekseni
  - Volume bar grafiği
  - RSI + MACD alt paneli
  - Crosshair ve bar-inspect modu (`bar_select_mode`)
  - Timeframe, viewport_bars, offset reactive'leri
  - Pan/zoom desteği
- `KeybindPanel`: ChartScreen için keybind referans sidebar'ı

#### `src/apex/tui/commands.py` *(güncellendi)*

Ne yaptığı:

- `/chart [TICKER]` → `chart` action dispatch
- `/inspect` → `bar_select` action (eski `/x` yeniden adlandırıldı)
- `/refresh`, `/zoom`, `/set-tf-*` → `chart_cmd` action
- `CHART_COMMAND_HELP` dict: chart-only komutlar ayrı tutuldu
- `COMMAND_HELP`'e `chart` eklendi

#### `src/apex/tui/app.py` *(güncellendi)*

Ne yaptığı:

- `ChartScreen`: tam terminal chart ekranı
  - BINDINGS: zoom in/out, crosshair left/right, pan left/right, timeframe 1m/5m/1h/1d, refresh
  - Tab/Shift+Tab: `priority=True` ile bar-inspect gezinme (wrap-around düzeltildi)
  - `on_input_submitted`: `/set-tf-*`, `/refresh`, `/inspect`, `/tf`, `/set`, `/zoom` handler'ları
  - `action_enter_bar_inspect` / `action_inspect_prev` / `action_inspect_next`
  - `_set_timeframe`: timeframe başına async `get_market_snapshot` fetch
  - `id="chart"` set edildi
- `CommandPalette`: `chart_only` param — ChartScreen'de sadece `CHART_COMMAND_HELP` gösteriliyor
- `TickerSelectPalette` + `CommandPaletteScreenMixin`: `/chart` komut desteği
- `ApexTuiApp`: `_handle_result` chart case, `_open_chart`, `_refresh_market_snapshot`

### Tests

#### `tests/unit/test_market_snapshot.py` *(yeni)*

- Fallback deterministik bar döndürüyor (ağ yok)
- Geçersiz ticker reddediliyor
- `IndicatorSummary` alanları mevcut
- Source label: `'fallback'` vs `'live'`

#### `tests/unit/test_tui_app.py` *(güncellendi)*

- `/chart` komutu için ticker picker açılıyor
- `/chart NVDA` → ChartScreen açılıyor (`id='chart'`), ticker sync
- MarketPanel mount sonrası snapshot alıyor (monkeypatched)
- MarketPanel snapshot None iken loading copy gösteriyor
- Market snapshot cache aynı ticker'ı yeniden kullanıyor

#### `tests/unit/test_tui_commands.py` *(güncellendi)*

- `/chart NVDA` → chart action, doğru ticker
- `/chart` (arg yok) → state ticker kullanılıyor
- `/chart` whitelist dışı → error action

---

## Doğrulama

```bash
uv run pytest tests/unit/test_market_snapshot.py tests/unit/test_tui_app.py tests/unit/test_tui_commands.py -q
# ✅ 50 passed

uv run ruff check src/apex/services/market_snapshot.py src/apex/tui/app.py src/apex/tui/commands.py src/apex/tui/widgets.py
# ✅ All checks passed

uv run mypy src/apex/services/market_snapshot.py src/apex/tui/app.py src/apex/tui/commands.py src/apex/tui/widgets.py
# ✅ Success: no issues found
```

## Notlar

- **Fallback:** Ağ/API yokken deterministik sentetik bar'lar üretiliyor; TUI çökmüyor
- **Chart-only dropdown:** ChartScreen'de `/` açıldığında sadece chart komutları görünüyor; diğer ekranlar etkilenmiyor
- **Tab wrap-around:** `priority=True` ile Textual focus cycling override edildi; bar 0'dan son bar'a, son bar'dan bar 0'a wrap çalışıyor
- **/x → /inspect:** Daha açıklayıcı komut adı; eski `/x` artık tanınmıyor

## Sonraki Adım

- **Phase 15:** Reports, History, Replay — markdown report generation, local JSONL history, replay saved runs

# Phase 13 Change Log — Local Analysis + CLI Foundation

**Tarih:** 2026-05-03  
**Phase:** 13 — Local Analysis + CLI Foundation  
**Durum:** Tamamlandı. `apex --help`, `apex analyze --help` çalışıyor; 41 unit test geçti, ruff clean.

## Kısa Özet

Bu phase'de LangGraph workflow'u FastAPI/Postgres/Redis olmadan doğrudan CLI'dan çağırabilmek için gerekli servis seam'i ve entrypoint oluşturuldu:

- `local_analysis.py` servisi: ticker canonicalization, whitelist kontrolü, as-of date validasyonu (gelecek tarih reddedilir), market data fetch + deterministic fallback, `analyze_with_workflow` çağrısı, yapılandırılmış sonuç dönüşü.
- `apex` CLI entrypoint'i: Typer tabanlı, default komut Phase 14 TUI placeholder'ı, `apex analyze TICKER [--date] [--instructions]` secondary/dev komutu.
- `pyproject.toml`: `apex = "apex.cli.main:main"` script, `typer>=0.15.0` bağımlılığı eklendi.
- `src/apex/__init__.py`: `main` entrypoint'i expose ediyor.
- 19 yeni unit test: date validasyon, whitelist, canonicalization, market data fallback, sync wrapper, CLI help/default/analyze/error exit senaryoları — tümü fake/mock ile, gerçek credential gerektirmiyor.

## Commit'ler

| Commit | Amaç |
|---|---|
| `feat: local_analysis service seam` | Server-independent `run_local_analysis` + `run_local_analysis_sync` — workflow'u CLI'dan çağırabilir hale getirir |
| `feat: apex CLI entrypoint (typer)` | `apex` script, default TUI placeholder, `analyze` komutu, Rich tablo çıktısı |
| `test: unit tests for local_analysis and CLI` | 19 test — date validation, whitelist, canonicalization, fallback, CLI contract |
| `chore: update STATE.md and ROADMAP.md for phase 13` | Phase 13 tamamlandı olarak işaretlendi |

## Değişen / Eklenen Dosyalar

### Services

#### `src/apex/services/local_analysis.py` *(yeni)*

Ne yaptığı:

- `run_local_analysis(ticker, mode, analysis_date, extra_instructions, agent_instructions)` — async, server bağımlılığı yok.
- `_validate_analysis_date()` — None → bugün, string → parse, gelecek tarih → ValueError.
- `_fetch_market_data()` — Alpaca/yfinance dener, hata alırsa 35 günlük deterministic stub döner.
- `_default_market_data()` — credential olmadan çalışan sabit OHLCV bar listesi.
- `run_local_analysis_sync()` — `asyncio.run()` wrapper, CLI için.

Neden:

- TUI ve CLI'ın workflow'u FastAPI HTTP katmanı üzerinden değil, doğrudan Python fonksiyon çağrısıyla kullanabilmesi gerekiyor.
- Phase 14 Textual cockpit bu seam'i kullanacak.

---

### CLI

#### `src/apex/cli/__init__.py` *(yeni)*

Ne yaptığı:

- Boş package init.

#### `src/apex/cli/main.py` *(yeni)*

Ne yaptığı:

- `app = typer.Typer(...)` — `apex` komutunun kökü.
- `default()` callback — subcommand yoksa Phase 14 placeholder mesajı basar.
- `analyze(ticker, date, instructions)` — `run_local_analysis_sync` çağırır, Rich tablo ile sinyal/güven/hata/maliyet gösterir. Hata → exit 1, agent error → exit 2.
- `main()` — `pyproject.toml` script entrypoint'i.

Neden:

- `apex` komutu öncelikle TUI launcher olacak (Phase 14); `analyze` secondary/dev/scripting yolu olarak kalıyor.

---

### Package Config

#### `pyproject.toml` *(güncellendi)*

Ne yaptığı:

- `[project.scripts]`: `apex = "apex.cli.main:main"` (eskisi: `apex = "apex:main"`).
- `dependencies`: `typer>=0.15.0` eklendi.

#### `src/apex/__init__.py` *(güncellendi)*

Ne yaptığı:

- `from apex.cli.main import main` — `main` entrypoint'i package seviyesinde expose ediyor.

---

### Tests

#### `tests/unit/test_local_analysis.py` *(yeni)*

Ne yaptığı:

- `_validate_analysis_date`: None/string/date/future senaryoları.
- `run_local_analysis`: structured result, whitelist reject, future date reject, ticker canonicalization, market data fallback.
- `run_local_analysis_sync`: async wrapper doğrulaması.

#### `tests/unit/test_cli.py` *(yeni)*

Ne yaptığı:

- `--help` ve `analyze --help` exit 0.
- Default komut placeholder mesajı.
- `analyze` komutu `run_local_analysis_sync`'i çağırıyor, sinyal çıktısı, `--date`/`--instructions` option geçişi.
- ValueError → exit 1, errors listesi → exit 2.

---

## Doğrulama

Çalışan kontroller:

```bash
uv run apex --help
# ✓ apex [OPTIONS] COMMAND [ARGS]... — analyze komutu görünüyor

uv run apex analyze --help
# ✓ TICKER argümanı, --date, --instructions option'ları görünüyor

uv run pytest tests/unit/test_local_analysis.py tests/unit/test_cli.py -v
# ✓ 19 passed

uv run pytest tests/unit/ --ignore=tests/e2e --ignore=tests/integration
# ✓ 41 passed, 1 skipped

uv run ruff check src/apex/cli src/apex/services/local_analysis.py tests/unit/test_cli.py tests/unit/test_local_analysis.py
# ✓ All checks passed!
```

Sınırlı kalan / dış bağımlılık gerektiren kontroller:

- `uv run apex analyze AAPL` gerçek çalışması için `OPENAI_API_KEY` ve Alpaca/yfinance erişimi gerekiyor (yfinance fallback credential'sız çalışır ama LLM key olmadan workflow agent'ları rule-based fallback'e düşer).

## Ekstra (Orijinal Plan Dışı)

| Ekstra | Açıklama |
|---|---|
| `extra_instructions` / `agent_instructions` state'e eklendi | Phase 14 TUI'ın per-agent prompt geçişini desteklemek için seam hazırlandı; plan'da belirtilmişti, minimal implementasyon |

## Notlar

- `run_local_analysis_sync` `asyncio.run()` kullanıyor — zaten çalışan bir event loop içinden çağrılmamalı (Textual kendi loop'unu yönetir, Phase 14'te async versiyonu doğrudan kullanılacak).
- `_default_market_data` 35 bar döndürüyor — teknik indikatörler (RSI, MACD, BB) için minimum veri gereksinimi karşılanıyor.
- `apex` default komutu şu an placeholder; Phase 14 bunu `textual` app launch ile değiştirecek.

## Sonraki Adım

- **Phase 14:** `apex` default komutunu Textual cockpit'e bağla; `run_local_analysis` async versiyonunu TUI worker thread'inden çağır; ticker/date/instructions TUI state'inden geçirilecek.

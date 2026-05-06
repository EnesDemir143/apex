# Phase 14 Change Log — Textual Terminal Cockpit

**Tarih:** 2026-05-06  
**Phase:** 14 — Textual Terminal Cockpit  
**Durum:** Tamamlandı

## Kısa Özet

Bu phase'de Apex için app-first Hermes-inspired Textual terminal cockpit oluşturuldu:

- `apex` komutu artık varsayılan olarak modern TUI cockpit'i başlatıyor
- Slash komut sistemi ile `/select`, `/analyze`, `/langsmith`, `/usage` vb. komutlar
- Ticker seçici, market paneli, setup paneli, agent progress, event log, report paneli
- Responsive worker ile UI donmadan analiz çalıştırma
- 31 yeni TUI testi (7 app + 24 komut testi)
- `apex analyze AAPL` klasik mod olarak ikincil komut olarak korundu

## Commit'ler

| Commit | Amaç |
|---|---|
| `feat/textual-terminal-cockpit` | App-first TUI cockpit — kullanıcı terminal içinde ticker seçip analiz çalıştırabiliyor |

## Değişen / Eklenen Dosyalar

### CLI Layer

#### `src/apex/cli/main.py` *(güncellendi)*

Ne yaptığı:

- `apex` komutu artık varsayılan olarak TUI'yi başlatıyor (no-args-is-help=False)
- `apex tui [ticker]` alias komutu eklendi
- `apex analyze AAPL` ikincil klasik mod olarak korundu

Neden:

- App-first yaklaşım: kullanıcı terminal içinde kalıp interaktif çalışabilmeli
- Klasik mod script/automation için hala gerekli

### TUI Layer (Yeni)

#### `src/apex/tui/__init__.py` *(yeni)*

Ne yaptığı:

- TUI modülü export'ları

#### `src/apex/tui/app.py` *(yeni)*

Ne yaptığı:

- `ApexTuiApp` — ana Textual app sınıfı
- Widget layout: ticker selector, market panel, setup panel, progress table, event log, report panel, command input, footer stats
- Responsive worker ile analiz çalıştırma (UI donmuyor)
- Slash komut dispatch ve result handling
- `run_tui()` entrypoint fonksiyonu

Neden:

- Hermes-inspired app-first TUI: kullanıcı tek bir terminal session'da ticker değiştirebilmeli, analiz çalıştırabilmeli
- Textual async worker pattern ile long-running analysis UI'yi bloklamıyor

#### `src/apex/tui/state.py` *(yeni)*

Ne yaptığı:

- `TuiState` — root state dataclass
- `SetupState` — ticker, analysis_date, depth, instructions, enabled_agents
- `AnalysisState` — status, signal, confidence, errors, usage, agent_outputs

Neden:

- Widget'lar arası state paylaşımı için merkezi state management
- Analysis date validation (future date reject)

#### `src/apex/tui/commands.py` *(yeni)*

Ne yaptığı:

- Slash komut parser: `/select AAPL`, `/analyze`, `/help` vb.
- `dispatch()` — komut routing ve `CommandResult` dönüşü
- Planned commands için Phase 15/17 placeholder mesajları

Neden:

- Hermes-style command palette UX
- Komut mantığı app'den ayrı, test edilebilir

#### `src/apex/tui/widgets.py` *(yeni)*

Ne yaptığı:

- `TickerSelector` — aktif ticker gösterimi
- `MarketPanel` — price/volume/indicator placeholder
- `SetupPanel` — ticker, date, depth, provider/model, LangSmith status, agents, instructions
- `AgentProgressTable` — team-based progress (Analysis, Risk, Decision)
- `EventLog` — timestamped event messages
- `ReportPanel` — analiz sonucu gösterimi
- `FooterStats` — agents done/total, tokens, cost, elapsed, LangSmith hint

Neden:

- TradingAgents-inspired ama Apex-specific widget'lar
- Reusable, test edilebilir bileşenler

#### `src/apex/tui/apex.tcss` *(yeni)*

Ne yaptığı:

- Textual CSS stylesheet
- Dark theme (GitHub dark colors)
- Widget layout ve styling

Neden:

- Textual CSS ile widget görünümü app kodundan ayrı

### Tests

#### `tests/unit/test_tui_app.py` *(yeni)*

Ne yaptığı:

- 7 TUI app testi
- Widget mount, ticker selection, command dispatch, state defaults

Neden:

- Textual `run_test()` ile UI logic test edilebilir

#### `tests/unit/test_tui_commands.py` *(yeni)*

Ne yaptığı:

- 24 slash komut testi
- Parser, dispatch, whitelist validation, planned command handling

Neden:

- Komut mantığı app'den bağımsız test edilebilir

#### `tests/unit/test_cli.py` *(güncellendi)*

Ne yaptığı:

- `test_default_command_launches_tui` — TUI launch'ı mock'luyor
- Eski `test_default_command_prints_placeholder` kaldırıldı (artık TUI başlatıyor, placeholder yok)

Neden:

- TUI gerçek app olduğu için test'te mock gerekli (yoksa sonsuz döngü)

### Dependencies

#### `pyproject.toml` *(güncellendi)*

Ne yaptığı:

- `textual>=0.80.0` dependency eklendi

Neden:

- Textual TUI framework gerekli

---

## Doğrulama

Çalışan kontroller:

```bash
uv run apex --help
# ✅ TUI default, analyze secondary command

uv run apex tui --help
# ✅ TUI alias

uv run apex analyze --help
# ✅ Classic mode options

uv run pytest tests/unit/test_tui_app.py tests/unit/test_tui_commands.py -v
# ✅ 31 passed

uv run pytest tests/unit/test_cli.py -v
# ✅ 9 passed (TUI launch mock'lu)

make check
# ✅ 86 passed, 1 skipped — ruff clean, mypy clean
```

Manuel test (gerçek TUI):

```bash
# TUI'yi başlat (Ctrl+C ile çık)
uv run apex

# Klasik mod
uv run apex analyze AAPL
```

## Ekstra (Orijinal Plan Dışı)

| Ekstra | Açıklama |
|---|---|
| `test_cli.py` fix | Eski placeholder test TUI launch'ı mock'lamalı yoksa asılıyor |

## Notlar

- **LangSmith status:** Setup panel'de API key present/missing gösteriliyor, secret value asla print edilmiyor
- **Analysis date validation:** Future date reject, default today
- **Provider/model:** Phase 14'te read-only display, switching Phase 17'de
- **Planned commands:** `/history`, `/report` Phase 15'te, `/provider` switching Phase 17'de
- **Market panel:** Şu an placeholder, gerçek chart widget Phase 15+ scope
- **Per-agent instructions:** Setup panel'de field var, local_analysis'e geçiliyor

## Sonraki Adım

- **Phase 15:** Reports, History, Replay — markdown report generation, local JSONL history, replay saved runs
- TUI artık çalışır durumda, Phase 15'te report/history persistence eklenecek

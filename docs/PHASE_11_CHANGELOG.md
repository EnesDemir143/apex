# Phase 11 Change Log — Streamlit API Wiring

**Tarih:** 2026-05-01  
**Phase:** 11 — Streamlit API Wiring  
**Durum:** Tamamlandı. Dashboard, Signals ve Observability sayfaları canlı FastAPI endpoint'lerine bağlandı; make check green (36 passed).

## Kısa Özet

Bu phase'de Streamlit frontend'indeki mock_data bağımlılıkları gerçek API çağrılarıyla değiştirildi:

- `api_client.py`'e `fetch_all_signals(tickers)` ve `fetch_observability()` fonksiyonları eklendi.
- `1_Dashboard.py`: TOP_SIGNALS, HERO_METRICS, agent consensus, latest analysis ve observability paneli canlı API'den besleniyor.
- `2_Signals.py`: ALL_SIGNALS, agent consensus ve latest analysis canlı API'den besleniyor.
- `6_Observability.py`: health status `/health` endpoint'inden, LLM cost analiz response'larından türetiliyor.
- Backtest ve Replay sayfaları mock data'da kaldı (henüz API endpoint'i yok).
- API erişilemez olduğunda tüm sayfalar mock data'ya graceful fallback yapıyor, sarı uyarı banner gösteriyor.
- `post_analysis_hook`: `portfolio_decision` None olduğunda (CI'da API key yok) `ValueError` fırlatmak yerine `rule_based_fallback` uygulanıyor, `status=degraded` dönüyor. E2E `test_analyze_returns_signal` testi artık CI'da geçiyor.
- `config.py`: LangSmith env bridge — `model_post_init` tüm `LANGSMITH_*` / `LANGCHAIN_*` key'lerini `os.environ`'a export ediyor; local dev'de manuel env setup gerekmeden auto-tracing çalışıyor.

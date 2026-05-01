# Phase 3 & 4 — Değişen Dosyalar ve Açıklamaları

> **Phase 3:** FastAPI & Data Ingestion Core
> **Phase 4:** Database Schema & Data Pipeline Completion

---

## Phase 3: FastAPI & Data Ingestion Core

### Neden bu phase?

Projenin dışarıya açılan yüzü (API) ve veri kaynağına bağlanan katmanı (ingestion) bu phase'de kuruldu. Hedef: FastAPI ayağa kalksın, `/health` endpoint'i çalışsın, Alpaca'dan OHLCV verisi çekilebilsin.

---

### `src/apex/domain/models/ohlcv.py` *(yeni)*

**Ne yapar:** Alpaca veya yfinance'dan gelen ham OHLCV verisini temsil eden Pydantic modeli.

**Neden böyle:** Domain katmanında veri modeli tanımlamak, ingestion katmanının dışarıya ne döndürdüğünü kontrat haline getirir. Pydantic validasyonu sayesinde:
- `close <= 0` olan bar kabul edilmez
- `high < low` olan bar kabul edilmez
- `volume < 0` olan bar kabul edilmez

`source` alanı (`"alpaca"` veya `"yfinance"`) hangi kaynaktan geldiğini takip eder — fallback aktifleşince bunu bilmek önemli.

```
OHLCVBar         → tek bir mum (candlestick)
OHLCVResponse    → bir ticker için bar listesi + degraded flag
```

`degraded=True` demek: Alpaca başarısız oldu, yfinance'a düştük, veri kalitesi düşük olabilir.

---

### `src/apex/ingestion/base_market_data_client.py` *(yeni)*

**Ne yapar:** Tüm market data client'larının uyması gereken abstract base class.

**Neden böyle:** Alpaca ve yfinance aynı interface'i implement eder. Bu sayede `MarketDataFetcher` hangi client'ı kullandığını bilmek zorunda kalmaz — sadece `fetch_ohlcv(ticker, start, end)` çağırır. Yeni bir veri kaynağı eklemek istersen (örn. Polygon.io) sadece bu ABC'yi implement edersin, başka hiçbir şeyi değiştirmezsin.

---

### `src/apex/ingestion/alpaca_client.py` *(yeni)*

**Ne yapar:** Alpaca Markets API'den günlük OHLCV bar'ları çeker.

**Neden böyle:** Alpaca paper trading hesabıyla ücretsiz gerçek zamanlı veri sağlar. `alpaca-py` SDK'sının `StockHistoricalDataClient`'ını kullanır. API key `.env`'den `settings` üzerinden gelir — hardcode yok.

Döndürdüğü `OHLCVBar` listesi `source="alpaca"` ile işaretlenir.

---

### `src/apex/ingestion/yfinance_client.py` *(yeni)*

**Ne yapar:** Yahoo Finance'dan OHLCV çeker. Alpaca'nın fallback'i.

**Neden böyle:** Alpaca API key yoksa veya rate limit aşılırsa sistem tamamen çökmemeli. yfinance ücretsiz ve key gerektirmez. Ancak veri kalitesi daha düşük olabilir (gecikmeli, adjusted olmayabilir). Bu yüzden `OHLCVResponse.degraded=True` set edilir — downstream sistemler bunu görüp güven skorunu düşürebilir.

---

### `src/apex/ingestion/market_data_fetcher.py` *(yeni → Phase 4'te genişletildi)*

**Ne yapar:** Alpaca → yfinance failover orchestrator'ı. Hangi client'ı kullanacağına karar verir.

**Neden böyle:** İki client arasındaki geçiş mantığı tek bir yerde toplanır. Phase 3'te temel yapı kuruldu, Phase 4'te `upsert_bars()` metodu eklendi (DB'ye yazma).

Akış:
```
fetch_ohlcv() çağrılır
  → Alpaca dene
  → Başarısız olursa yfinance'a düş, degraded=True set et
  → OHLCVResponse döndür
```

---

### `src/apex/api/app.py` *(yeni)*

**Ne yapar:** FastAPI uygulama factory'si. `create_app()` fonksiyonu uygulamayı oluşturur.

**Neden factory pattern:** Test sırasında farklı config ile uygulama oluşturabilmek için. `app = create_app()` şeklinde module-level instance da var — uvicorn bunu kullanır.

`lifespan` context manager startup/shutdown yönetir:
- Startup: logging setup, bağlantı havuzları
- Shutdown: temiz kapanış

Middleware sırası önemli — en dıştan içe doğru işlenir:
1. `CORSMiddleware` (en dış)
2. `CorrelationIDMiddleware`

---

### `src/apex/api/middleware.py` *(yeni)*

**Ne yapar:** Her HTTP request'e correlation ID ekler.

**Neden:** Distributed tracing için kritik. Bir request birden fazla servise gidiyorsa (veya log'larda takip ediliyorsa) aynı ID ile izlenebilir. Client `X-Correlation-ID` header'ı gönderirse onu kullanır, göndermezse UUID üretir. Response'a da aynı ID eklenir.

---

### `src/apex/api/dependencies.py` *(yeni)*

**Ne yapar:** FastAPI dependency injection fonksiyonları. Şu an minimal — Phase 5'te DB session ve Redis bağlantısı buraya taşınacak.

---

### `src/apex/api/routes/health.py` *(yeni)*

**Ne yapar:** İki endpoint:

| Endpoint | Amaç | Başarısız olursa |
|----------|------|-----------------|
| `GET /health` | Liveness probe — her zaman 200 döner | `status: degraded` döner ama 200 |
| `GET /ready` | Readiness probe — bağlantıları kontrol eder | 503 döner |

**Neden ikisi ayrı:** Kubernetes/Docker health check convention'ı. Liveness = "uygulama hayatta mı?", Readiness = "trafik alabilir mi?". Postgres veya Redis geçici olarak düşerse liveness geçer ama readiness başarısız olur — böylece load balancer trafiği bu pod'a yönlendirmez ama pod'u restart etmez.

Her check için direkt `asyncpg` bağlantısı açılır (ORM overhead'i olmadan) — health check hızlı olmalı.

---

### `tests/integration/conftest.py` *(yeni)*

**Ne yapar:** Integration testler için `app_client` fixture'ı. `httpx.AsyncClient` ile FastAPI'ye istek atar — gerçek HTTP server başlatmadan.

---

### `tests/integration/test_health.py` *(yeni)*

**Ne yapar:** `/health` ve `/ready` endpoint'lerini test eder. Correlation ID header'ının response'a yansıdığını doğrular.

---

### `tests/integration/test_data_client.py` *(yeni)*

**Ne yapar:** `OHLCVBar` validasyon kurallarını test eder (high < low reject, close <= 0 reject). `MarketDataClient`'ın abstract olduğunu doğrular — direkt instantiate edilemez.

---

## Phase 4: Database Schema & Data Pipeline Completion

### Neden bu phase?

Phase 3'te veri çekmeyi öğrendik ama nereye yazacağımızı bilmiyorduk. Bu phase'de tam veritabanı şeması kuruldu, migration çalıştırıldı, seed data eklendi ve pipeline idempotent hale getirildi.

---

### `src/apex/infrastructure_layer/models/base.py` *(yeni)*

**Ne yapar:** SQLAlchemy `DeclarativeBase`. Tüm ORM modelleri buradan türer.

**Neden ayrı dosya:** Circular import'u önler. Model dosyaları birbirini import etmeden `Base`'i ortak kaynaktan alır.

---

### `src/apex/infrastructure_layer/models/stock.py` *(yeni)*

**Ne yapar:** `stocks` tablosu ORM modeli.

**Kolonlar:** `id`, `ticker` (unique, max 10 karakter), `name`, `sector`, `exchange`, `is_active` (bool, default true), `created_at`, `updated_at`

**Neden `is_active`:** Bir ticker delisted olduğunda satırı silmek yerine `is_active=False` yapılır. Tarihsel veri korunur.

---

### `src/apex/infrastructure_layer/models/stock_price.py` *(yeni)*

**Ne yapar:** `stock_prices` tablosu. Günlük OHLCV bar'larını saklar.

**Kritik kararlar:**
- Tüm fiyat kolonları `Numeric(18,8)` — float kullanılmaz, finansal hassasiyet şart
- Volume `Numeric(24,8)` — büyük hacimler için
- `adj_close` ayrı kolon — stock split'lerde düzeltilmiş fiyat
- `(stock_id, date)` unique constraint — aynı gün için duplicate bar giremez, upsert'in temeli bu

---

### `src/apex/infrastructure_layer/models/ingestion_log.py` *(yeni)*

**Ne yapar:** `ingestion_log` tablosu. Her veri çekme işleminin audit kaydı.

**Neden:** Hangi ticker için ne zaman veri çekildi, kaç satır eklendi/güncellendi, hata olduysa ne hatası — bunlar olmadan pipeline debug edilemez. Özellikle production'da kritik.

---

### `src/apex/infrastructure_layer/models/analysis_run.py` *(yeni)*

**Ne yapar:** `analysis_runs` tablosu. Bir analiz oturumunun üst kaydı.

**Kritik kararlar:**
- `id` UUID (server-side `gen_random_uuid()`) — integer PK yerine UUID çünkü distributed sistemlerde çakışma riski yok
- `final_signal` (BUY/SELL/HOLD) ve `final_confidence` `Numeric(5,4)` — 4 ondalık hassasiyet
- `summary` JSONB — agent çıktılarının özeti esnek yapıda saklanır
- `compaction_applied` bool — LLM context compaction yapıldıysa işaretlenir (Phase 7)

---

### `src/apex/infrastructure_layer/models/agent_decision.py` *(yeni)*

**Ne yapar:** `agent_decisions` tablosu. Her agent'ın kararı ayrı satır.

**Neden `analysis_runs`'dan ayrı:** Audit trail için. Hangi agent ne dedi, neden dedi, kaç token harcadı — bunlar ayrı tutulmazsa debugging imkansız. 4 agent × 1 analiz = 4 satır.

**Önemli kolonlar:**
- `reasoning` JSONB — agent'ın gerekçesi
- `indicators` JSONB — kullandığı göstergeler
- `is_fallback` bool — rule-based fallback mı yoksa LLM mi?
- `prompt_version` int — hangi prompt versiyonu kullanıldı

---

### `src/apex/infrastructure_layer/models/embedding.py` *(yeni)*

**Ne yapar:** `embeddings` tablosu. RAG için vektör embeddings saklar.

**Kritik karar:** `Vector` dimension `settings.embedding_dim`'den okunur (default 768). Hardcode değil — model değişirse migration yazmak yerine config değiştirilir. Nomic Embed Text V2 için 768 dim.

---

### `src/apex/infrastructure_layer/models/trade.py` *(yeni)*

**Ne yapar:** `trades` tablosu. Sistem tarafından önerilen/gerçekleştirilen işlemler.

**Önemli kolonlar:**
- `analysis_run_id` FK — hangi analizden doğdu
- `status`: `proposed` / `accepted` / `rejected` — insan onayı workflow'u için
- `environment`: `paper` / `live` — canlı para mı kağıt mı
- `pnl` `Numeric(18,8)` — kar/zarar

---

### `src/apex/infrastructure_layer/models/prediction_band.py` *(yeni)*

**Ne yapar:** `prediction_band_log` tablosu. Fiyat tahmin bantlarını ve gerçekleşen fiyatı saklar.

**Neden:** Model accuracy tracking için. Tahmin edilen upper/lower/mid band vs gerçek close — zamanla modelin ne kadar doğru olduğu ölçülür.

---

### `src/apex/infrastructure_layer/models/llm_usage_log.py` *(yeni)*

**Ne yapar:** `llm_usage_log` tablosu. Her LLM API çağrısının maliyet kaydı.

**Kritik kolon — `cache_hit` bool:** Aynı prompt daha önce çağrıldıysa cache'den döndü mü? Cache hit'ler para harcamaz. Bu kolon olmadan gerçek maliyet hesaplanamaz.

**Neden `analysis_run_id` nullable:** Bazı LLM çağrıları analiz dışında olabilir (embedding generation gibi).

---

### `migrations/versions/4c4190a3b8d1_initial_schema.py` *(yeni)*

**Ne yapar:** Alembic migration. Yukarıdaki 10 tabloyu veritabanında oluşturur.

**Önemli:** `agent_checkpoints` tablosu **yok**. LangGraph'ın `AsyncPostgresSaver.setup()` bunu Phase 7'de otomatik oluşturacak — Alembic'e dahil edilmez çünkü LangGraph'ın iç implementasyonu değişebilir.

Migration başında `CREATE EXTENSION IF NOT EXISTS vector;` çalışır — pgvector extension'ı aktif eder.

---

### `src/apex/ingestion/market_calendar.py` *(yeni)*

**Ne yapar:** NYSE trading day filtresi.

**Neden gerekli:** Hafta sonları ve tatil günleri için veri çekmeye çalışmak gereksiz API çağrısı ve hata demek. `pandas_market_calendars` kütüphanesi NYSE tatil takvimini bilir. `get_trading_days(start, end)` sadece gerçek işlem günlerini döndürür.

---

### `src/apex/ingestion/market_data_fetcher.py` *(genişletildi)*

**Ne eklendi:** `upsert_bars()` metodu.

**Neden upsert:** Aynı ticker için aynı tarihin verisi iki kez çekilirse duplicate satır oluşmamalı. PostgreSQL `ON CONFLICT (stock_id, date) DO UPDATE` ile mevcut satır güncellenir, yeni satır eklenmez. Pipeline kaç kez çalıştırılırsa çalıştırılsın sonuç aynı — idempotent.

---

### `scripts/seed_data.py` *(yeni)*

**Ne yapar:** 5 ticker'ı (AAPL, TSLA, MSFT, NVDA, GOOGL) `stocks` tablosuna ekler.

**Neden idempotent:** Script birden fazla çalıştırılabilir, duplicate oluşmaz. `ON CONFLICT (ticker) DO UPDATE` kullanır. Docker volume silinip yeniden başlatıldığında (bugün yaptığımız gibi) tek komutla seed data geri gelir.

---

### `tests/unit/test_data_pipeline.py` *(yeni)*

**Ne yapar:** Data pipeline'ın unit testleri.

**Test kategorileri:**
- NYSE calendar: hafta sonu ve tatil günleri filtreleniyor mu?
- Fetch bars: primary başarılı olunca fallback çağrılmıyor mu?
- Fetch bars: primary başarısız olunca yfinance devreye giriyor mu?
- Upsert: aynı veri iki kez yazılınca duplicate oluşmuyor mu?
- Upsert: bilinmeyen ticker için hata fırlatıyor mu?

VCR.py cassette placeholder var — Alpaca API'ye gerçek istek atmadan kayıtlı response'u oynatmak için. Cassette henüz kaydedilmedi (skipped), Phase 10'da tamamlanacak.

---

## Özet Tablo

| Dosya | Phase | Tür | Açıklama |
|-------|-------|-----|----------|
| `domain/models/ohlcv.py` | 3 | Model | OHLCV bar + response Pydantic modeli |
| `ingestion/base_market_data_client.py` | 3 | ABC | Market data client interface |
| `ingestion/alpaca_client.py` | 3 | Client | Alpaca API OHLCV client |
| `ingestion/yfinance_client.py` | 3 | Client | yfinance fallback client |
| `ingestion/market_data_fetcher.py` | 3+4 | Orchestrator | Failover + upsert logic |
| `api/app.py` | 3 | App | FastAPI factory + lifespan |
| `api/middleware.py` | 3 | Middleware | Correlation ID propagation |
| `api/dependencies.py` | 3 | DI | FastAPI dependency functions |
| `api/routes/health.py` | 3 | Route | `/health` + `/ready` endpoints |
| `tests/integration/conftest.py` | 3 | Test | AsyncClient fixture |
| `tests/integration/test_health.py` | 3 | Test | Health endpoint tests |
| `tests/integration/test_data_client.py` | 3 | Test | OHLCV model validation tests |
| `models/base.py` | 4 | ORM | SQLAlchemy DeclarativeBase |
| `models/stock.py` | 4 | ORM | stocks tablosu |
| `models/stock_price.py` | 4 | ORM | stock_prices tablosu (Numeric precision) |
| `models/ingestion_log.py` | 4 | ORM | ingestion_log tablosu |
| `models/analysis_run.py` | 4 | ORM | analysis_runs tablosu (UUID PK) |
| `models/agent_decision.py` | 4 | ORM | agent_decisions tablosu (per-agent audit) |
| `models/embedding.py` | 4 | ORM | embeddings tablosu (pgvector) |
| `models/trade.py` | 4 | ORM | trades tablosu |
| `models/prediction_band.py` | 4 | ORM | prediction_band_log tablosu |
| `models/llm_usage_log.py` | 4 | ORM | llm_usage_log tablosu (cache_hit) |
| `migrations/versions/4c4190a3b8d1_initial_schema.py` | 4 | Migration | 10 tablo + pgvector extension |
| `ingestion/market_calendar.py` | 4 | Util | NYSE trading day filtresi |
| `scripts/seed_data.py` | 4 | Script | 5 ticker seed (idempotent) |
| `tests/unit/test_data_pipeline.py` | 4 | Test | Calendar + upsert + failover testleri |
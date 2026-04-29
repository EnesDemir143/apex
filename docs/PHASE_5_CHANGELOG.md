# Phase 5 Change Log — Domain Models & Core Services

**Tarih:** 2026-04-29  
**Phase:** 05 — Domain Models & Core Services  
**Durum:** Kod tarafı tamamlandı ve doğrulandı. GSD `SUMMARY.md`, `STATE.md`, `ROADMAP.md` güncellemesi henüz yapılmadı; manual gate için kullanıcı `OK` bekleniyor.

## Kısa Özet

Bu phase’de Apex’in core/domain/service/API temel katmanları eklendi:

- Domain modelleri ve value object’ler oluşturuldu.
- Ortak sabitler ve uygulama exception hiyerarşisi eklendi.
- LLM client abstraction, fake LLM client ve günlük bütçe koruması eklendi.
- Async SQLAlchemy session factory, Redis client, cache service ve repository pattern eklendi.
- FastAPI’ye analiz ve portföy stub endpoint’leri, structured error handler ve rate limiter middleware eklendi.
- Ruff, mypy, unit test ve ASGI endpoint smoke kontrolleri çalıştırıldı.

## Commit’ler

| Commit | Amaç |
|---|---|
| `838b4b7` | Domain primitives: domain modelleri, `Signal`, constants, exception hierarchy |
| `1ac3eaf` | Service foundations: LLM client, budget limiter, DB/Redis/cache/repository katmanı |
| `bc6e107` | API seams: analysis/portfolio route’ları, error handler, rate limiter, app registration |
| `2200e5c` | Quality gate fixes: lint/typecheck uyumluluk düzeltmeleri |

## Değişen / Eklenen Dosyalar

### Domain Layer

#### `src/apex/domain/value_objects.py`

Eklenenler:

- `Signal` enum:
  - `BUY`
  - `SELL`
  - `HOLD`
- `Indicator` Pydantic modeli:
  - `name`
  - `value`
  - `interpretation`

Sonradan kalite düzeltmesi:

- Ruff `UP042` için `Enum` yerine `StrEnum` kullanıldı.

#### `src/apex/domain/models/stock.py`

Eklenen:

- `Stock` Pydantic domain modeli.

Alanlar:

- `id`
- `ticker`
- `name`
- `sector`
- `exchange`
- `is_active`
- `created_at`

#### `src/apex/domain/models/trade.py`

Eklenen:

- `Trade` Pydantic domain modeli.

Alanlar:

- `id`
- `ticker`
- `signal`
- `confidence`
- `entry_price`
- `exit_price`
- `pnl`
- `status`
- `analysis_run_id`
- `created_at`

#### `src/apex/domain/models/analysis.py`

Eklenen:

- `AnalysisResult` Pydantic modeli.

Alanlar:

- `run_id`
- `ticker`
- `signal`
- `confidence`
- `summary`
- `indicators`
- `total_tokens`
- `cost_usd`
- `latency_ms`
- `status`
- `created_at`

Validation:

- `confidence`: `0.0 <= confidence <= 1.0`
- `cost_usd`: `>= 0.0`

#### `src/apex/domain/models/portfolio.py`

Eklenenler:

- `PortfolioPosition`
- `Portfolio`

Kalite düzeltmesi:

- Mutable default riskini önlemek için `positions` alanında `Field(default_factory=list)` kullanıldı.

#### `src/apex/domain/models/prediction_band.py`

Eklenen:

- `PredictionBand` Pydantic modeli.

Validation:

- `confidence`: `0.0 <= confidence <= 1.0`

#### `src/apex/domain/models/__init__.py`

Güncellendi:

- Yeni domain modelleri package export listesine eklendi.

Export edilenler:

- `AnalysisResult`
- `OHLCVBar`
- `OHLCVResponse`
- `Portfolio`
- `PortfolioPosition`
- `PredictionBand`
- `Stock`
- `Trade`

#### `src/apex/domain/__init__.py`

Güncellendi:

- Domain package seviyesinde modeller ve value object’ler import edilebilir hale getirildi.

Örnek:

```python
from apex.domain import AnalysisResult, Signal, Stock
```

### Core Layer

#### `src/apex/core/constants.py`

Eklenen sabitler:

- `TICKERS_WHITELIST`
- `MAX_CONFIDENCE`
- `MIN_CONFIDENCE`
- `DEFAULT_TIMEOUT`
- `FALLBACK_CONFIDENCE`
- `BUY_CONFIDENCE_THRESHOLD`
- `SELL_CONFIDENCE_THRESHOLD`
- `HOLD_CONFIDENCE_THRESHOLD`

#### `src/apex/core/exceptions.py`

Eklenen exception hiyerarşisi:

- `ApexError`
- `LLMBudgetExceededError`
- `DataFetchError`
- `AgentError`
- `ConfigError`

### Service Layer

#### `src/apex/services/llm_client.py`

Eklenenler:

- `LLMResponse`
- `LLMClient` abstract base class
- `OpenAIClient`
- `FakeLLMClient`
- `_estimate_cost_usd`
- `parse_response_content`

Amaç:

- Agent workflow’ların LLM provider detaylarından bağımsız çalışması.
- Test ve local development için deterministic `FakeLLMClient`.

Not:

- `OpenAIClient`, `langchain-openai` `ChatOpenAI` üzerinden async `ainvoke()` kullanır.

#### `src/apex/services/cost_guard.py`

Eklenen:

- `BudgetLimiter`

Davranış:

- Günlük LLM maliyetini takip eder.
- Redis verilirse günlük key ile Redis’te tutar.
- Redis yoksa in-memory fallback kullanır.
- Bütçe aşılırsa `LLMBudgetExceededError` fırlatır.
- UTC gün sonuna göre TTL hesaplar.

#### `src/apex/services/cache_service.py`

Eklenen:

- `CacheService`

Metodlar:

- `get`
- `set`
- `invalidate`

Davranış:

- Redis client üzerinde `apex:` prefix’i ve TTL desteğiyle çalışır.

#### `src/apex/services/stock_repository.py`

Eklenen:

- `StockRepository`

Metodlar:

- `get_by_ticker`
- `get_all`
- `create`

Kullandığı model:

- `apex.infrastructure_layer.models.Stock`

#### `src/apex/services/analysis_repository.py`

Eklenen:

- `AnalysisRepository`

Metodlar:

- `create`
- `get_by_stock`
- `get_latest`
- `get`

Kullandığı model:

- `apex.infrastructure_layer.models.AnalysisRun`

### Infrastructure Layer

#### `src/apex/infrastructure_layer/database.py`

Eklenenler:

- Async SQLAlchemy engine.
- `AsyncSessionLocal`
- `get_db_session`
- `dispose_engine`

Kullanılan config:

- `settings.database_url`
- `settings.db_echo`
- `settings.db_pool_size`
- `settings.db_max_overflow`

#### `src/apex/infrastructure_layer/redis_client.py`

Eklenenler:

- `create_redis_client`
- `get_redis_client`
- `get_redis`
- `close_redis`

Kullanılan config:

- `settings.redis_url`
- `settings.redis_max_connections`

### API Layer

#### `src/apex/api/routes/analysis.py`

Eklenen endpoint:

- `POST /api/v1/analyze/{ticker}`

Eklenen modeller:

- `AnalyzeRequest`

Davranış:

- Şimdilik stub `AnalysisResult` döner.
- Whitelist içindeki ticker’lar için `HOLD` signal döner.
- Phase 6/7’de gerçek LangGraph workflow ile değiştirilecek seam hazırlandı.

#### `src/apex/api/routes/portfolio.py`

Eklenen endpoint:

- `GET /api/v1/portfolio`

Eklenen modeller:

- `PortfolioResponse`

Davranış:

- Şimdilik stub portfolio verisi döner.

#### `src/apex/api/error_handler.py`

Eklenen:

- `register_error_handlers(app)`

Handler’lar:

- `ApexError` → structured JSON, HTTP 400
- `RequestValidationError` → structured JSON, HTTP 422
- generic `Exception` → structured JSON, HTTP 500

#### `src/apex/api/rate_limiter.py`

Eklenen:

- `RateLimiterMiddleware`

Davranış:

- In-memory token bucket.
- Default limit: `120 requests / minute`.
- Limit aşılırsa HTTP 429 döner.

Not:

- Bu distributed rate limiter değildir. Çoklu instance production ortamı için Redis-backed limiter Phase 7/9 civarında değerlendirilmeli.

#### `src/apex/api/app.py`

Güncellendi:

- `RateLimiterMiddleware` eklendi.
- `analysis_router` eklendi.
- `portfolio_router` eklendi.
- `register_error_handlers(app)` çağrıldı.

Kayıtlı yeni route’lar:

- `/api/v1/analyze/{ticker}`
- `/api/v1/portfolio`

## Çalıştırılan Doğrulamalar

### Plan 05-01 Acceptance Checks

Çalıştırılan kontroller:

- `Signal` enum içinde `BUY`, `SELL`, `HOLD` kontrol edildi.
- `AnalysisResult(BaseModel)` kontrol edildi.
- `TICKERS_WHITELIST`, `ApexError`, `LLMBudgetExceededError` kontrol edildi.
- Domain import smoke testi çalıştırıldı.

Sonuç:

- Passed.

### Plan 05-02 Acceptance Checks

Çalıştırılan kontroller:

- `LLMClient(ABC)`, `OpenAIClient`, `FakeLLMClient` kontrol edildi.
- `BudgetLimiter` ve `LLMBudgetExceededError` kontrol edildi.
- `create_async_engine`, `async_sessionmaker`, `redis.asyncio`, `CacheService` kontrol edildi.
- `StockRepository`, `AnalysisRepository`, `AsyncSession` kontrolleri yapıldı.
- Service import smoke testi çalıştırıldı.

Sonuç:

- Passed.

### Plan 05-03 Acceptance Checks

Çalıştırılan kontroller:

- `analysis.py` içinde `@router.post` ve `/analyze/` kontrol edildi.
- `portfolio.py` içinde `@router.get` ve `/portfolio` kontrol edildi.
- `error_handler.py` içinde `@app.exception_handler` kontrol edildi.
- `rate_limiter.py` içinde rate limiter logic kontrol edildi.
- `app.py` içinde analysis ve portfolio router registration kontrol edildi.
- FastAPI route registration smoke testi çalıştırıldı.
- ASGI smoke:
  - `POST /api/v1/analyze/AAPL`
  - `GET /api/v1/portfolio`

Sonuç:

- Passed.

### Quality Gates

Çalıştırılan komutlar:

```fish
fish -c "uv run ruff check src tests"
fish -c "uv run mypy src"
fish -c "uv run ruff format --check src/apex/domain src/apex/core src/apex/services src/apex/infrastructure_layer/database.py src/apex/infrastructure_layer/redis_client.py src/apex/api"
fish -c "uv run pytest -q --tb=short tests/unit tests/test_placeholder.py"
```

Sonuçlar:

- Ruff check: passed.
- Mypy: passed, `53 source files`.
- Format check for touched Phase 5 paths: passed, `32 files already formatted`.
- Unit tests: `10 passed, 1 skipped`.

## Bilinen Notlar / Sınırlar

- Endpoint’ler gerçek analiz yapmıyor; Phase 6/7’de LangGraph agent workflow bağlanacak.
- `RateLimiterMiddleware` in-memory çalışıyor; distributed production limit için Redis-backed yaklaşım gerekir.
- Live OpenAI, PostgreSQL ve Redis bağlantıları bu phase içinde full integration olarak test edilmedi.
- Docker-backed integration suite bu adımda çalıştırılmadı; hızlı doğrulama olarak unit ve ASGI smoke testleri kullanıldı.
- `.gitignore` içinde mevcut uncommitted `docs/` değişikliği vardı; bu doküman eklenirken `.gitignore` değiştirilmedi.
- GSD manual gate nedeniyle `.planning/phases/05-domain-models-core-services/*-SUMMARY.md`, `.planning/STATE.md`, `.planning/ROADMAP.md` henüz güncellenmedi.

## Sonraki Adım

Kullanıcı `OK` verdikten sonra GSD phase completion akışı devam etmeli:

1. Phase 5 plan summary dosyaları oluşturulmalı.
2. `STATE.md` ve `ROADMAP.md` güncellenmeli.
3. Phase-level verification / review gate çalıştırılmalı.
4. Post-work graphify update çalıştırılmalı.


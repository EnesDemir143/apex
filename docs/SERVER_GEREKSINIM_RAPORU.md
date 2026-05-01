# Apex Sunucu Gereksinimi ve GitHub Kaynakları Uygunluk Raporu

**Tarih:** 2026-04-30  
**Kapsam:** `/Users/enesdemir/Documents/apex` deposundaki mevcut kod, Docker/Compose yapılandırmaları, plan dokümanları ve GitHub resmi dokümanları incelendi.

## Kısa Karar

**Evet, bu projenin gerçek MVP/production kullanımı için bir sunucuya veya managed backend servislerine ihtiyacı var.**

GitHub'ın kendi kaynakları tek başına bu projeyi production olarak çalıştırmak için yeterli değil; ancak **CI/CD, test, container image üretimi, dokümantasyon ve statik rapor/dashboard yayınlama** için kullanılabilir.

Mevcut hedef mimari şunları gerektiriyor:

- Uzun süre çalışan **FastAPI** backend (`uvicorn`, port `8000`)
- Kalıcı **PostgreSQL 17 + pgvector** veritabanı
- **Redis 8** cache/bütçe/ileride rate-limit veya workflow yardımcı servisi
- OpenAI/LangChain çağrıları yapan agent katmanı
- Alpaca/yfinance üzerinden dış market-data erişimi
- Opsiyonel ama planlanmış observability stack: **Loki + Promtail + Grafana**

## Mevcut Proje Durumu

### Uygulama Tipi

Depo bir Python 3.13 backend projesi:

- `pyproject.toml`: FastAPI, SQLAlchemy async, asyncpg, Redis, LangGraph, LangChain/OpenAI, Alpaca, yfinance, Streamlit bağımlılıkları var.
- `Dockerfile`: production image `uvicorn apex.api.app:app --host 0.0.0.0 --port 8000` ile API sunuyor.
- `docker-compose.prod.yml`: app + PostgreSQL + Redis + Loki + Promtail + Grafana stack'i tanımlı.
- `.github/` klasörü yok: şu an GitHub Actions CI/CD workflow'u tanımlanmamış.

### Çalışan/var olan parçalar

- FastAPI app ve route wiring var: `src/apex/api/app.py`
- Health/readiness endpointleri Postgres ve Redis kontrol ediyor: `src/apex/api/routes/health.py`
- Analysis/watchlist API endpointleri şu an stub yanıt dönüyor: `src/apex/api/routes/analysis.py`, `src/apex/api/routes/watchlist.py`
- DB modeli ve Alembic migration var: `migrations/versions/4c4190a3b8d1_initial_schema.py`
- Market data fetcher var: Alpaca primary, yfinance fallback: `src/apex/ingestion/market_data_fetcher.py`
- 4 agent dosyası var: technical, fundamental, risk, portfolio manager; OpenAIClient kullanıyorlar.

### Henüz tamamlanmamış/production açısından kritik eksikler

- Full LangGraph workflow assembly henüz yok; planlarda Phase 7 olarak duruyor.
- Streamlit frontend dependency var ama frontend uygulaması henüz yok; `src/apex/frontend/__init__.py` dışında uygulama dosyası bulunmuyor.
- K8s manifestleri ve GitHub Actions CI/CD henüz yok.
- API dependency dosyasında placeholder var: `src/apex/api/dependencies.py`; gerçek DB/Redis dependency implementasyonları ayrı dosyalarda var ama route seviyesinde tam entegre değil.
- In-memory rate limiter kullanılıyor; multi-worker/multi-instance production için Redis-backed limiter'a evrilmeli.

## GitHub Kaynakları ile Çalışır mı?

### GitHub Pages

**Bu proje doğrudan GitHub Pages üzerinde çalışmaz.**

GitHub Pages resmi olarak statik site hosting servisidir; HTML/CSS/JS dosyalarını repository'den yayınlar. FastAPI, PostgreSQL, Redis, Streamlit server process veya Python backend çalıştırmaz.

Uygun olduğu kullanım:

- Dokümantasyon sitesi
- Statik dashboard
- GitHub Actions ile günlük üretilmiş statik HTML/JSON raporlarını yayınlama

Uygun olmadığı kullanım:

- `/api/v1/analyze/{ticker}` gibi canlı FastAPI endpointleri
- Postgres/Redis bağlantısı
- OpenAI/Alpaca secret kullanan backend
- Streamlit server-side uygulaması

Kaynak: GitHub Pages dokümanı — https://docs.github.com/pages/getting-started-with-github-pages/what-is-github-pages

### GitHub Actions

**GitHub Actions bu projenin CI/CD ve scheduled job tarafında işe yarar; production sunucusu yerine geçmez.**

GitHub-hosted runner'lar workflow job çalıştırır. Linux runner'larda Postgres/Redis service container kullanılabilir, fakat bu servisler workflow süresince geçici çalışır; kalıcı production database/cache değildir. Ayrıca GitHub-hosted job execution için süre limiti vardır; uzun yaşayan web server olarak kullanılamaz.

Uygun olduğu kullanım:

- `ruff`, `mypy`, `pytest` çalıştırmak
- Docker image build etmek
- GHCR'ye image push etmek
- Alembic migration kontrolü
- Scheduled job ile statik rapor üretmek
- Uzak sunucuya deploy tetiklemek

Uygun olmadığı kullanım:

- 7/24 FastAPI server çalıştırmak
- Kalıcı PostgreSQL/Redis barındırmak
- Production kullanıcı trafiğini karşılamak

Kaynaklar:

- GitHub-hosted runner specs: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- Actions limits: https://docs.github.com/en/enterprise-cloud%40latest/actions/reference/actions-limits
- PostgreSQL service containers: https://docs.github.com/actions/tutorials/use-containerized-services/create-postgresql-service-containers
- Redis service containers: https://docs.github.com/en/actions/use-cases-and-examples/using-containerized-services/creating-redis-service-containers

### GitHub Codespaces

**Codespaces geliştirme ortamı olarak kullanılabilir, production ortamı değildir.**

Codespaces VM/container tabanlı cloud dev environment sağlar; resmi dokümanda 2 core/8 GB RAM'den 32 core/128 GB RAM'e kadar seçenekler olduğu belirtiliyor. Bu geliştirme/test için iyi ama production hosting yerine kullanılmamalı.

Kaynak: https://docs.github.com/en/codespaces/about-codespaces/what-are-codespaces

## Sunucu Gereksinimi Tahmini

Aşağıdaki tahminler mevcut compose dosyaları, Python/FastAPI runtime, PostgreSQL/Redis ve planlanan observability bileşenlerine göre yapılmıştır.

### 1) Sadece backend MVP — observability yok

Bileşenler:

- FastAPI app
- PostgreSQL + pgvector
- Redis

Öneri:

| Kaynak | Minimum | Rahat MVP |
|---|---:|---:|
| CPU | 2 vCPU | 2-4 vCPU |
| RAM | 4 GB | 6 GB |
| Disk | 30 GB SSD | 50 GB SSD |
| Swap | 1-2 GB | 2 GB |

Notlar:

- `docker-compose.prod.yml` app için 1 GB, Postgres için 1 GB, Redis için 512 MB limit veriyor; toplam container limiti yaklaşık 2.5 GB.
- OS + Docker + log + burst payı için 4 GB altına inilmemeli.
- 1 vCPU çalışır ama agent/LLM çağrıları, pandas hesapları ve DB işlemleri aynı anda gelirse yavaşlar.

### 2) Backend + observability stack

Bileşenler:

- FastAPI app
- PostgreSQL + pgvector
- Redis
- Loki
- Promtail
- Grafana

Öneri:

| Kaynak | Minimum | Rahat MVP/Prod |
|---|---:|---:|
| CPU | 2 vCPU | 4 vCPU |
| RAM | 6 GB | 8 GB |
| Disk | 50 GB SSD | 80-100 GB SSD |
| Swap | 2 GB | 2-4 GB |

Notlar:

- Compose resource limit toplamı yaklaşık 3.4 GB: app 1 GB + Postgres 1 GB + Redis 512 MB + Loki 512 MB + Promtail 128 MB + Grafana 256 MB.
- Log retention artarsa disk tüketimi hızla büyür. Loki için retention ve disk limiti netleştirilmeli.

### 3) K3s/self-hosted hedefi

Plan dokümanları ARM64 K3s hedefini işaret ediyor. Tek node K3s için öneri:

| Ortam | Öneri |
|---|---|
| Development/staging | 2 vCPU, 4-6 GB RAM, 50 GB SSD |
| MVP production | 4 vCPU, 8 GB RAM, 80-100 GB SSD |
| Daha güvenli production | 4 vCPU, 12-16 GB RAM, 150+ GB SSD; DB backup/volume ayrımı |

## Trafik ve İş Yükü Varsayımı

Mevcut kodda ağır CPU inference yok; LLM inference OpenAI tarafında çalışıyor. Sunucu yükü ağırlıklı olarak:

1. API request handling
2. PostgreSQL sorguları ve pgvector indeksleri
3. Redis cache/budget state
4. pandas ile teknik indikatör hesapları
5. dış API çağrı latency'si
6. observability log yazımı

Bu nedenle başlangıçta RAM/disk CPU'dan daha kritik.

## GitHub-Only Alternatif Mümkün mü?

**Evet ama mevcut ürün mimarisini küçültürseniz mümkün.**

GitHub-only varyant şöyle olabilir:

1. GitHub Actions `schedule` ile günde 1-4 kez çalışır.
2. Alpaca/yfinance/OpenAI çağrıları yapılır.
3. Sonuçlar JSON/Markdown/HTML olarak repository'ye veya artifact'e yazılır.
4. GitHub Pages statik dashboard olarak yayınlar.

Bu modelde:

- Canlı API yok.
- Kullanıcı isteğiyle anlık analiz yok.
- PostgreSQL/Redis yok veya dış managed servis gerekir.
- Secret yönetimi GitHub Secrets ile yapılır.
- Sonuçlar statik ve gecikmeli olur.

Bu model yatırım/analiz raporu yayınlamak için uygun; canlı backend ürünü için uygun değil.

## Önerilen Deployment Stratejisi

### En pratik yol

1. GitHub Actions ekle:
   - lint: `ruff`
   - typecheck: `mypy`
   - tests: unit + integration service containers
   - Docker build
   - GHCR push
2. Küçük bir VPS veya ARM64 K3s node kullan:
   - minimum 2 vCPU / 4-6 GB RAM
   - tavsiye 4 vCPU / 8 GB RAM
3. Production compose ile başla; K3s manifestleri hazır olunca K3s'e geç.
4. İlk production'da observability'yi ayrı fazda aç veya düşük retention ile kullan.
5. PostgreSQL backup stratejisini ilk günden kur.

### Hosting seçenekleri

| Seçenek | Uygunluk | Not |
|---|---|---|
| GitHub Pages | Sadece statik dashboard/docs | Backend çalışmaz |
| GitHub Actions | CI/CD + scheduled statik rapor | 7/24 server değil |
| Codespaces | Dev/test | Production değil |
| Tek VPS + Docker Compose | En hızlı MVP yolu | 4-8 GB RAM yeterli başlar |
| Tek node K3s | Planla uyumlu | K8s operasyon yükü daha fazla |
| Managed DB + container app | Daha production-friendly | Maliyet artar, operasyon azalır |

## Riskler ve Dikkat Edilecekler

- `.env` dosyası localde var; secret'ların repo'ya girmediğinden emin olunmalı.
- `.github/` yok; CI/CD henüz kurulmamış.
- Health endpointleri Postgres/Redis yoksa `degraded`/`503` davranışı verir; production readiness bu servisleri zorunlu kabul ediyor.
- Agent workflow henüz tam wired değil; gerçek analiz yükü Phase 7 sonrası değişebilir.
- OpenAI cost guard mevcut ama distributed kullanım için Redis entegrasyonu doğru bağlanmalı.
- pgvector büyüdükçe Postgres RAM/disk ihtiyacı artar.

## Doğrulama Notları

Çalıştırılan yerel kontroller:

- `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .` → geçti.
- `UV_CACHE_DIR=/tmp/uv-cache uv run mypy src/` → geçti.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/unit tests/test_placeholder.py -q` → 14 passed, 1 skipped.
- Tüm test suite denendi; integration testleri Docker socket erişimi sandbox nedeniyle `PermissionError: Operation not permitted` ile çalışmadı. Bu kod hatası değil, mevcut çalışma ortamında Docker daemon erişimi kısıtı.

## Sonuç

Bu proje için **production hedefi backend + database + cache olduğu sürece sunucu gereklidir**. GitHub kaynakları çok faydalı ama rolü production hosting değil, **CI/CD + test + statik yayın + image registry** olmalı.

Başlangıç önerim:

- **MVP backend:** 2 vCPU / 4-6 GB RAM / 50 GB SSD
- **MVP + observability:** 4 vCPU / 8 GB RAM / 80-100 GB SSD
- **GitHub kullanımı:** Actions + GHCR + Pages/docs; production app'i VPS/K3s üzerinde çalıştır.

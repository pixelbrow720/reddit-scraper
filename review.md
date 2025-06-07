**Analisis Potensi Bug:**

Meskipun kode aktual tidak tersedia, berdasarkan struktur dan deskripsi fitur, berikut adalah area-area di mana bug potensial mungkin muncul:

1.  **Parallel Processing (`core/parallel_scraper.py`) & Rate Limiting (`core/rate_limiter.py`):**
    *   **Race Conditions:** Jika state dibagi antar thread/proses tanpa sinkronisasi yang tepat (misalnya, saat mengupdate progress global atau menulis ke file/database).
    *   **Rate Limit Tidak Efektif:**
        *   Jika `global_rate_limiter` di `ParallelScraper` tidak benar-benar membatasi total request dari semua worker secara efektif. Setiap worker mungkin memiliki `RedditClient` sendiri yang tidak aware dengan rate limit global secara real-time.
        *   Rate limit untuk ekstraksi konten dari link eksternal (`ContentExtractor`) mungkin berbeda dan perlu penanganan terpisah. Jika digabung dengan rate limit Reddit API, bisa jadi terlalu lambat atau terlalu cepat untuk salah satunya.
    *   **Error Propagation:** Kesalahan di satu worker mungkin tidak ditangani atau dilaporkan dengan benar ke proses utama, menyebabkan data hilang atau proses berhenti secara tidak terduga.
    *   **Resource Exhaustion:** Jika jumlah worker tidak dibatasi dengan baik atau jika tugas-tugas individual memakan banyak memori/CPU, bisa menyebabkan sistem lambat atau crash.

2.  **Database Integration (`database/database_manager.py` - SQLite):**
    *   **Concurrency Issues:** SQLite secara default memiliki batasan concurrency (terutama pada penulisan). Dengan banyak worker atau request API yang mencoba menulis ke database secara bersamaan, bisa terjadi `OperationalError: database is locked`. Walaupun ada `self.lock` di `DatabaseManager`, ini hanya berlaku untuk thread dalam satu proses. Jika menggunakan `ProcessPoolExecutor`, lock ini tidak akan berfungsi antar proses.
    *   **Schema Migration:** Tidak ada mekanisme migrasi schema yang terlihat. Jika schema berubah di versi mendatang, ini bisa menyebabkan masalah pada instalasi yang sudah ada.
    *   **Data Integrity:** Validasi data sebelum dimasukkan ke DB. Pydantic di API membantu, tapi bagaimana dengan data dari scraping langsung?
    *   **Query Performance:** Untuk dataset yang sangat besar (jutaan post, seperti disebut di blueprint), query SQLite bisa menjadi lambat meskipun ada indexing, terutama untuk analytics yang kompleks.

3.  **Content Extraction (`processors/content_extractor.py`):**
    *   **Struktur Website Berubah:** Extractor yang spesifik untuk domain (YouTube, GitHub) sangat rentan rusak jika struktur HTML website tersebut berubah.
    *   **JavaScript-Rendered Content:** `requests` + `BeautifulSoup` tidak bisa menangani konten yang dirender oleh JavaScript. Fitur ini mungkin tidak berfungsi untuk banyak website modern.
    *   **Anti-Scraping Measures:** Banyak website memiliki mekanisme anti-scraping yang bisa memblokir IP atau mengembalikan data palsu.
    *   **Timeouts & Error Handling:** Timeouts yang terlalu pendek/panjang atau error handling yang kurang robus bisa menyebabkan worker macet atau data tidak lengkap.

4.  **Analytics (`analytics/sentiment_analyzer.py`, `analytics/trend_predictor.py`):**
    *   **Akurasi Sentiment:** VADER dan TextBlob bagus untuk sentimen umum, tapi mungkin kurang akurat untuk konteks spesifik Reddit (sarkasme, slang, meme). `reddit_patterns` membantu, tapi tetap terbatas.
    *   **Performa Trend Prediction:** Jika menggunakan model ML yang kompleks dan data yang besar secara real-time atau sering, bisa memakan banyak resource.
    *   **Overfitting/Underfitting (ML):** Jika model ML dilatih, perlu validasi yang cermat untuk menghindari ini.
    *   **Ketergantungan Library:** Jika VADER atau TextBlob tidak terinstal (`VADER_AVAILABLE`, `TEXTBLOB_AVAILABLE` flags), fungsionalitas berkurang.

5.  **API & Dashboard (`api/dashboard_api.py`, `frontend/`):**
    *   **WebSocket Handling:**
        *   Manajemen koneksi WebSocket (`websocket_connections`) perlu robus. Bagaimana jika koneksi terputus? Bagaimana jika banyak koneksi?
        *   Pesan yang dikirim ke WebSocket (misalnya, `_notify_websocket_clients`) adalah operasi `await`. Jika satu client lambat atau bermasalah, bisa memblokir pengiriman ke client lain jika tidak di-`gather` dengan `return_exceptions=True` atau di-`create_task`.
    *   **State Management di Backend:** `active_sessions` adalah dictionary global. Ini tidak akan berfungsi jika API di-scale ke beberapa proses/instance (misalnya, dengan Gunicorn workers > 1 atau di Kubernetes). Perlu solusi state terdistribusi (Redis, database).
    *   **Background Tasks FastAPI:** `BackgroundTasks` cocok untuk operasi singkat. Untuk scraping yang bisa berjalan lama, ini kurang ideal. Jika server restart, task hilang. Task queue (Celery, RQ) lebih baik.
    *   **Error Handling di API:** Perlu memastikan semua edge cases di-handle dan mengembalikan status HTTP yang sesuai.
    *   **Keamanan API:** Meskipun CORS dan header keamanan disebut, validasi input yang ketat, otentikasi (jika diperlukan untuk fitur enterprise), dan otorisasi penting.

6.  **Configuration (`cli/config.py`, `config/settings.example.yaml`):**
    *   **Validasi YAML:** Memuat YAML bisa gagal jika formatnya salah. Perlu error handling yang baik.
    *   **Sensitive Data:** `client_secret` disimpan di `settings.yaml`. Untuk production, sebaiknya menggunakan environment variables atau secret management system. (`.env` disebut di `DEPLOYMENT.md`, ini bagus).

7.  **Deployment & Monitoring (Docker, Nginx, Prometheus, Grafana):**
    *   **Resource Limits Docker:** `docker-compose.yml` tidak mendefinisikan resource limits (CPU, memory) untuk container, yang penting di production. (`DEPLOYMENT.md` menyebutkan ini di `troubleshooting > memory issues`, tapi sebaiknya ada di konfigurasi default production).
    *   **Persistensi Data Monitoring:** Volume untuk Prometheus dan Grafana sudah ada, ini bagus.
    *   **Nginx Configuration:** Cukup lengkap, tapi perlu dites dengan SSL di production. `proxy_read_timeout 86400` untuk WebSocket mungkin terlalu panjang jika tidak ada keep-alive yang efektif.

8.  **Memory Management (`core/performance_monitor.py`):**
    *   `tracemalloc` bagus untuk debugging, tapi bisa menambah overhead signifikan jika selalu aktif di production.
    *   `MemoryOptimizer.process_in_chunks` dengan `gc.collect()` setelah tiap chunk bisa membantu, tapi `gc.collect()` tidak selalu menjamin pembebasan memori instan dan bisa menghentikan sementara eksekusi.

9.  **Umum:**
    *   **Unicode Handling:** Selalu jadi sumber bug potensial saat scraping teks dari berbagai sumber.
    *   **Timezone:** Pastikan semua penanganan `datetime` konsisten (UTC direkomendasikan untuk backend).
    *   **Path Handling:** Penggunaan `os.path.join` dan `Path` (dari `pathlib`) sudah bagus. Pastikan konsisten.

**Hal yang Kurang dan Bisa Di-improve:**

1.  **Database Scalability:**
    *   **SQLite untuk "Enterprise Edition":** Seperti disebut di atas, SQLite bisa menjadi bottleneck untuk skala besar dan konkurensi tinggi. Pertimbangkan untuk mendukung PostgreSQL atau MySQL sebagai alternatif, terutama untuk fitur enterprise. Ini akan membutuhkan ORM (seperti SQLAlchemy) untuk abstraksi database.
    *   **Database Migration:** Implementasikan sistem migrasi (Alembic jika pakai SQLAlchemy) untuk mengelola perubahan schema database antar versi.

2.  **Task Management untuk Scraping:**
    *   **Dedicated Task Queue:** Untuk scraping session yang panjang dan parallel, gunakan task queue seperti Celery atau RQ dengan Redis/RabbitMQ sebagai broker. Ini membuat sistem lebih robus, scalable, dan memungkinkan monitoring task yang lebih baik daripada `BackgroundTasks` FastAPI atau `ThreadPoolExecutor` langsung di API.

3.  **Real-time Progress & Control yang Lebih Granular:**
    *   Selain progress per subreddit, mungkin progress per batch post di dalam subreddit.
    *   Kemampuan untuk pause/resume scraping session.

4.  **Konfigurasi dan Secrets Management:**
    *   Untuk production, integrasikan dengan sistem manajemen secret (Vault, AWS KMS, Google KMS) daripada hanya file `.env` atau `settings.yaml` untuk kredensial sensitif.
    *   Validasi konfigurasi yang lebih ketat menggunakan Pydantic juga untuk file YAML.

5.  **Content Extraction Lanjutan:**
    *   Untuk website yang kompleks dengan JavaScript rendering, pertimbangkan integrasi opsional dengan headless browser (Playwright, Selenium). Ini akan menambah dependensi dan resource, jadi harus opsional.
    *   Gunakan library yang lebih canggih untuk ekstraksi konten utama dari artikel, seperti `newspaper3k`.

6.  **Analytics Lanjutan:**
    *   **Topic Modeling:** Untuk menemukan topik-topik utama dalam data yang discrape.
    *   **Network Analysis:** Analisis interaksi antar user.
    *   **Customizable ML Models:** Jika `TrendPredictor` menggunakan ML, mungkinkan pengguna untuk melatih atau menyediakan model mereka sendiri.
    *   **Explainability:** Jika menggunakan ML, sediakan cara untuk memahami mengapa prediksi tertentu dibuat.

7.  **Error Handling dan Resilience:**
    *   **Circuit Breaker Pattern:** Untuk request ke Reddit API atau website eksternal. Jika banyak error, stop sementara request ke endpoint tersebut.
    *   **Dead Letter Queue:** Untuk task scraping yang gagal setelah beberapa kali retry, pindahkan ke DLQ untuk investigasi manual.

8.  **Testing:**
    *   `pytest.ini` menyebutkan `cov-fail-under=80`, yang baik.
    *   Tingkatkan pengujian integrasi yang melibatkan interaksi antar komponen (API -> Database -> Scraper).
    *   Pertimbangkan contract testing jika API akan dikonsumsi oleh banyak pihak.
    *   Frontend testing yang lebih komprehensif (misalnya dengan Cypress atau Playwright).

9.  **Dokumentasi API:**
    *   FastAPI auto-generated docs (Swagger/ReDoc) sudah bagus. Pastikan semua endpoint dan model Pydantic terdokumentasi dengan baik (deskripsi, contoh).
    *   `docs/API.md` lebih fokus pada komponen internal. Mungkin perlu API reference yang lebih fokus pada endpoint HTTP untuk pengguna API.

10. **Resource Management:**
    *   Eksplisitkan resource request dan limit untuk container Docker di file `docker-compose.prod.yml` atau Kubernetes deployment.
    *   Pantau penggunaan resource oleh worker scraping dan optimalkan.

11. **Caching:**
    *   Selain `AnalyticsCache`, pertimbangkan caching untuk data yang sering diakses di API (misalnya, daftar subreddit populer, hasil query umum) menggunakan Redis. `CacheManager` di `performance_monitor.py` adalah awal yang baik, tapi integrasi dengan Redis akan lebih scalable.

12. **Modularitas & Skalabilitas Horizontal:**
    *   Untuk skala enterprise sejati, beberapa komponen (analytics, scraping worker) bisa dipertimbangkan untuk dijadikan service terpisah (microservices) yang bisa di-scale independen. Ini menambah kompleksitas, tapi meningkatkan skalabilitas.

13. **User Interface (Dashboard):**
    *   **Kustomisasi Dashboard:** Kemampuan bagi user untuk membuat widget atau dashboard kustom.
    *   **Manajemen User & Role (Multi-tenancy):** Jika ini benar-benar "Enterprise", mungkin perlu dukungan multi-user dengan role-based access control. `README.md` menyebut "User authentication and multi-tenancy" sebagai upcoming feature, jadi ini sudah direncanakan.
    *   **Alerting:** Integrasi dengan sistem alerting (misalnya, dari Grafana atau custom) untuk notifikasi jika ada masalah scraping atau anomali data.


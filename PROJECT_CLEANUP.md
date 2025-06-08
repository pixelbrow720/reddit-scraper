# 🧹 Project Cleanup Plan

## Files to Remove (Redundant/Outdated)

### Documentation Files (Consolidate)
- `blueprint.md` → Merge into README.md
- `FEATURES_SUMMARY.md` → Merge into README.md  
- `review.md` → Move to `docs/archive/`
- `IMPROVEMENTS.md` → Move to `docs/`

### Duplicate/Old Files
- `dashboard_api.py` → Keep only `improved_dashboard_api.py`
- `rate_limiter.py` → Keep only `thread_safe_rate_limiter.py`
- `docker-compose.yml` → Keep only `docker-compose.improved.yml`
- `requirements.txt` → Keep only `requirements-improved.txt`

### Demo/Example Files (Consolidate)
- `demo_all_features.py` → Move to `examples/`
- `start_dashboard.py` → Merge functionality into `run.py`

## New Structure Plan

```
reddit-scraper/
├── README.md                    # Main documentation
├── LICENSE
├── .gitignore
├── requirements.txt             # Renamed from requirements-improved.txt
├── docker-compose.yml           # Renamed from docker-compose.improved.yml
├── Dockerfile
├── setup.py
├── pytest.ini
├���─ run.py                       # Main entry point
├── config/
│   ├── settings.example.yaml
│   └── settings.yaml
├── src/
│   ├── __init__.py
│   ├── analytics/
│   ├── api/
│   │   ├── __init__.py
│   │   └── dashboard_api.py     # Renamed from improved_dashboard_api.py
│   ├── cli/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── circuit_breaker.py
│   │   ├── parallel_scraper.py
│   │   ├── performance_monitor.py
│   │   ├── rate_limiter.py      # Renamed from thread_safe_rate_limiter.py
│   │   └── reddit_client.py
│   ├── database/
│   ├── exporters/
│   └── processors/
├── frontend/
├── tests/
├── examples/
│   ├── basic_usage.py
│   ├── advanced_usage.py
│   └── demo_all_features.py     # Moved from root
├── docs/
│   ├── API.md
│   ├── INSTALLATION.md
│   ├── DEPLOYMENT.md
│   ├── CONTRIBUTING.md
│   ├── SECURITY.md
│   ├── IMPROVEMENTS.md          # Moved from root
│   └── archive/
│       └── review.md            # Archived
├── scripts/
│   ├── run_demo.sh
│   ├── run_demo.bat
│   └── run_tests.py
├── deployment/
│   ├── nginx/
│   │   └── nginx.conf
│   └── monitoring/
└── data/                        # Runtime data
    └── .gitkeep
```
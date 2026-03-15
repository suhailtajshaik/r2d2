# VPS State

*Last updated: 2026-03-15*

## Running Containers

| Container | Image | Status | URL |
|-----------|-------|--------|-----|
| r2d2-nginx | nginx:alpine | ✅ Up | Port 80/443 |
| portfolio | portfolio-portfolio | ✅ Up | suhailtaj.cloud |
| lab | lab-site-lab | ✅ Up | lab.suhailtaj.cloud |
| prompt-studio | prompt-studio-prompt-studio | ✅ Up | lab.suhailtaj.cloud/prompt-studio |
| localai | localai/localai:latest-cpu | ✅ Up (healthy) | Internal :8080 |
| news-site | news-site | ✅ Up | Internal :80 (newspaper delivery) |

## Stopped Containers
- sellbridge-dev-* (frontend, backend, postgres, redis, supertokens)
- rag-app (backend, frontend, qdrant)
- gst-ledger

## Compose Locations (all under r2d2)
- `/home/r2d2/nginx/` — main reverse proxy
- `/home/r2d2/projects/portfolio/` — portfolio
- `/home/r2d2/projects/lab-site/` — lab
- `/home/r2d2/projects/prompt-studio/` — prompt studio
- `/home/r2d2/projects/Sellbridge/` — sellbridge dev
- `/home/r2d2/projects/rag-app/` — rag app
- `/home/r2d2/projects/gst-ledger-book/` — gst ledger

## Docker Networks
- `r2d2-proxy` — nginx + portfolio + lab
- `prompt-studio` — nginx + prompt-studio
- `sellbridge-dev` — nginx + sellbridge containers
- `rag-app_rag-network` — nginx + rag containers

## Domains
- suhailtaj.cloud → portfolio container
- lab.suhailtaj.cloud → lab container
- lab.suhailtaj.cloud/prompt-studio → prompt-studio container

## SSL
- Cloudflare Origin Certificate at `/home/r2d2/nginx/ssl/`

# Dawar • Eco Assistant UI (React + Vite + TS)

Fully wired to your backend spec.

## Quickstart
```bash
npm i
npm run dev
```

Set API base URL (optional) by creating `.env`:
```env
VITE_API_BASE=http://127.0.0.1:8000
```

## Endpoints used
- POST /api/chat/new
- GET  /api/chat/list
- DELETE /api/chat/{conv_id}
- GET  /api/chat/{conv_id}/history
- POST /api/chat/{conv_id}/send
- POST /api/upload/images/upload
- GET  /api/images/images/history

## **How It All Flows**

1. **Frontend** sends a request (e.g., new message, image upload).
2. **FastAPI endpoint** receives it and validates input using **DTOs**.
3. **Service layer** performs DB operations (create/list/fetch/delete).
4. **Services return models** → converted to **DTOs** for response.
5. **Frontend** gets structured JSON for rendering.

**Example Flow: Send Message**

```
Frontend POST /chat/{conv_id}/send
  → FastAPI endpoint validates request (MessageCreateDTO)
  → MessageService.create_message()
  → Convert Message model → MessageResponseDTO
  → Return JSON to frontend
```

---

This architecture is **clean, modular, and scalable**:

* Models handle persistence.
* Services handle business logic.
* DTOs handle validation and API schemas.
* Endpoints handle routing and conversion between DTOs and services.

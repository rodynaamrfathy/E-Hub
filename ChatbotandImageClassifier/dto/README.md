## **DTOs (Pydantic)**

* Provide **validation, typing, and API documentation**.
* Structured to match API endpoints:

| DTO                      | Purpose                                                 |
| ------------------------ | ------------------------------------------------------- |
| `ConversationDTO`        | Create conversation, list conversations, response.      |
| `MessageDTO`             | Create messages, chat history, single message response. |
| `ImageDTO`               | Upload response, history, detail, classification.       |
| `ImageClassificationDTO` | Create classification.                                  |
| `HealthDTO`              | Health check.                                           |

**Example:** `MessageHistoryDTO` represents a message including optional images and their classification.

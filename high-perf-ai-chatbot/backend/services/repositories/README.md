## **Services**

Each entity has a service class:

| Service                      | Responsibilities                                                                                    |
| ---------------------------- | --------------------------------------------------------------------------------------------------- |
| `ConversationService`        | Create, list, get, delete conversations.                                                            |
| `MessageService`             | Create, list, get, delete messages.                                                                 |
| `ImageService`               | Create, list, get, delete images.                                                                   |
| `ImageClassificationService` | Create, get, delete classifications.                                                                |
| `get_conversation_history`   | Special function to load a conversation’s full chat with messages, images, and classification data. |

Services **talk directly to the DB** and handle business logic.


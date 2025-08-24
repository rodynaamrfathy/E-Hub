## **API Endpoints**

Mapped from services and DTOs:

**Chat API**

* `POST /chat/{conv_id}/send` → Uses `MessageService.create_message` → Returns `MessageResponseDTO`.
* `GET /chat/{conv_id}/history` → Uses `get_conversation_history` → Returns `List[MessageHistoryDTO]`.
* `POST /chat/new` → Uses `ConversationService.create_conversation` → Returns `ConversationResponseDTO`.
* `GET /chat/list` → Uses `ConversationService.list_conversations` → Returns `List[ConversationListDTO]`.
* `DELETE /chat/{conv_id}` → Uses `ConversationService.delete_conversation`.

**Image API**

* `POST /images/upload` → Uses `ImageService.create_image` → Returns `ImageUploadResponseDTO`.
* `POST /images/{image_id}/classify` → Uses `ImageClassificationService.create_classification` → Returns `ImageClassificationDTO`.
* `GET /images/history` → Lists uploaded images → Returns `List[ImageHistoryDTO]`.
* `GET /images/{image_id}` → Returns `ImageDetailDTO`.
* `DELETE /images/{image_id}` → Uses `ImageService.delete_image`.

**Meta API**

* `GET /health` → Returns `HealthDTO`.



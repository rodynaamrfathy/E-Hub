# Streaming Responses Implementation Guide

## Overview

This guide provides comprehensive documentation for implementing real-time streaming responses in the Recycling & Sustainability Assistant chatbot. The implementation uses Server-Sent Events (SSE) to stream AI-generated responses token by token, providing a smooth, real-time chat experience.

## Architecture

```
┌─────────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│     Frontend        │───▶│   FastAPI        │───▶│   Gemini LLM        │
│   (JavaScript)     │    │  Stream Endpoint │    │   Token Stream      │
│   EventSource      │◀───│  (SSE Generator) │◀───│   Generation        │
└─────────────────────┘    └──────────────────┘    └─────────────────────┘
          │                          │                          │
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Real-time UI      │    │  Message Storage │    │    RAG Context      │
│   Updates           │    │  PostgreSQL      │    │    Assembly         │
└─────────────────────┘    └──────────────────┘    └─────────────────────┘
```

## Backend Implementation

### FastAPI Streaming Response Setup

**Location**: `api/chat.py`

The streaming endpoint handles multipart form data (text + images) and returns Server-Sent Events:

```python
@router.post("/{conv_id}/send-stream")
async def send_message_stream_with_images(
    conv_id: str,
    content: str = Form(..., description="Message content"),
    images: Optional[List[UploadFile]] = File(None, description="Optional image files"),
    db: AsyncSession = Depends(get_db_session),
):
    """Send user message with optional images and stream assistant response (SSE)."""

    # Input validation
    if not content.strip() and not images:
        raise HTTPException(status_code=400, detail="Message content or images required")

    # Process uploaded images
    temp_files = []
    image_paths = []

    if images:
        for img in images:
            suffix = os.path.splitext(img.filename)[-1] or ".jpg"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(await img.read())
            tmp.flush()
            tmp.close()
            temp_files.append(tmp.name)
            image_paths.append(tmp.name)

    # Initialize chatbot and services
    chatbot = GeminiMultimodalChatbot(session_id=conv_id)
    msg_service = MessageService()

    # Save user message to database
    user_msg = await msg_service.create_message(
        db, conv_id, sender="user", content=content
    )

    # Stream generator function
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            logger.info(f"🔹 Starting stream for conv={conv_id}, content={content[:80]}...")

            full_response_tokens = []

            # Stream tokens from chatbot
            async for token in chatbot.stream_response(content, image_paths):
                full_response_tokens.append(token.strip())
                yield f"data: {json.dumps({'token': token})}\n\n"
                await asyncio.sleep(0)  # Allow other tasks to run

            # Get complete response and save to database
            full_response = chatbot.get_full_response() or " ".join(full_response_tokens).strip()

            if full_response:
                ai_msg = await msg_service.create_message(
                    db, conv_id, sender="assistant", content=full_response
                )
                logger.info(f"💬 Saved assistant response: {full_response[:80]}...")

            # Send completion signal
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"⚠️ Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        finally:
            # Cleanup temporary files
            for path in temp_files:
                try:
                    if os.path.exists(path):
                        os.unlink(path)
                except:
                    pass

    # Return streaming response
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )
```

### Chatbot Streaming Implementation

**Location**: `services/conversation/GeminiMultimodalChatbot.py`

The chatbot streams tokens from the Gemini LLM and manages conversation context:

```python
async def stream_response(self, user_input: str, images: Optional[List] = None):
    """Stream response tokens as they are generated."""
    final_response = []
    references = []

    try:
        # Process images
        processed_images = [self._prepare(img) for img in (images or []) if img]
        processed_images = [p for p in processed_images if p]

        # RAG retrieval (KB → Articles → Web search)
        retrieved_data = await self._maybe_retrieve(user_input)
        retrieved_context = retrieved_data["context"] if retrieved_data else None
        references = retrieved_data["references"] if retrieved_data else []

        # Create multimodal input
        user_message = self._create_multimodal_message(user_input, processed_images)

        # Prepare message history
        history = self.memory.chat_memory.messages
        messages = [SystemMessage(content=self.system_prompt), *history]

        # Add retrieved context
        if retrieved_context:
            messages.append(
                SystemMessage(content=f"Here are relevant search results:\n{retrieved_context}")
            )

        messages.append(user_message)

        # Stream from Gemini LLM
        async for chunk in self.llm.astream(messages):
            if hasattr(chunk, "content") and chunk.content:
                # Split content into tokens and stream word by word
                tokens = chunk.content.split()
                for token in tokens:
                    final_response.append(token)
                    yield token + " "

        # Add references at the end
        if references:
            refs_formatted = "\n\n📎 References:\n" + "\n".join([
                f"- [{r.get('title','Untitled')}]({r.get('url')})"
                if r.get("url") else f"- {r.get('title','Untitled')}"
                for r in references
            ])
            final_response.append(refs_formatted)
            yield refs_formatted

    except Exception as e:
        print(f"Error in stream_response: {e}")
        yield f"Error: {str(e)}"

    finally:
        # Save conversation context and history
        full_text = " ".join(final_response).strip()
        if full_text:
            self.memory.save_context({"input": user_input}, {"output": full_text})
            user_chat = ChatMessage("user", user_input, [i["data"] for i in processed_images])
            ai_chat = ChatMessage("assistant", full_text)
            self.chat_messages.extend([user_chat, ai_chat])

            # Trim history and persist
            self.chat_messages = self.chat_messages[-self.max_history * 2:]
            self.session_mgr.save(self.chat_messages)

            self._last_full_response = full_text

def get_full_response(self) -> str:
    """Get the complete response after streaming is finished."""
    return getattr(self, "_last_full_response", "")
```

## Message Format

### Stream Data Structure

All streaming messages follow the Server-Sent Events format:

```
data: <JSON_PAYLOAD>\n\n
```

### Message Types

#### 1. Token Messages
```json
{
  "token": "Hello"
}
```

#### 2. Completion Signal
```
data: [DONE]\n\n
```

#### 3. Error Messages
```json
{
  "error": "Error description"
}
```

### Example Stream Sequence

```
data: {"token": "The"}

data: {"token": " best"}

data: {"token": " way"}

data: {"token": " to"}

data: {"token": " recycle"}

data: {"token": " plastic"}

data: {"token": " bottles"}

data: {"token": " is"}

data: {"token": " to"}

data: {"token": " clean"}

data: {"token": " them"}

data: {"token": " first."}

data: {"token": "\n\n📎 References:\n- [EPA Recycling Guidelines](https://www.epa.gov/recycle)"}

data: [DONE]
```

## Frontend Implementation

### JavaScript EventSource Setup

```javascript
class ChatStreamer {
    constructor(conversationId) {
        this.conversationId = conversationId;
        this.eventSource = null;
        this.isStreaming = false;
    }

    async sendMessage(content, images = null) {
        if (this.isStreaming) {
            console.warn('Already streaming a response');
            return;
        }

        try {
            this.isStreaming = true;

            // Prepare form data
            const formData = new FormData();
            formData.append('content', content);

            if (images && images.length > 0) {
                images.forEach((image, index) => {
                    formData.append('images', image);
                });
            }

            // Start streaming request
            const response = await fetch(`/chat/${this.conversationId}/send-stream`, {
                method: 'POST',
                body: formData,
                headers: {
                    // Don't set Content-Type - let browser set it for FormData
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // Set up streaming reader
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let buffer = '';
            let fullResponse = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                // Decode and buffer the chunk
                buffer += decoder.decode(value, { stream: true });

                // Process complete lines
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6); // Remove 'data: ' prefix

                        if (data === '[DONE]') {
                            this.onStreamComplete(fullResponse);
                            this.isStreaming = false;
                            return fullResponse;
                        }

                        try {
                            const parsed = JSON.parse(data);

                            if (parsed.error) {
                                this.onError(parsed.error);
                                this.isStreaming = false;
                                return;
                            }

                            if (parsed.token) {
                                fullResponse += parsed.token;
                                this.onToken(parsed.token, fullResponse);
                            }
                        } catch (e) {
                            console.warn('Failed to parse streaming data:', data, e);
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Streaming error:', error);
            this.onError(error.message);
        } finally {
            this.isStreaming = false;
        }
    }

    // Override these methods to handle events
    onToken(token, fullResponse) {
        console.log('Token received:', token);
        // Update UI with new token
    }

    onStreamComplete(fullResponse) {
        console.log('Stream complete:', fullResponse);
        // Finalize UI updates
    }

    onError(error) {
        console.error('Stream error:', error);
        // Handle error in UI
    }

    abort() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        this.isStreaming = false;
    }
}
```

### Complete Frontend Example with UI

```html
<!DOCTYPE html>
<html>
<head>
    <title>Streaming Chat</title>
    <style>
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .messages {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 4px;
        }
        .user-message {
            background-color: #e3f2fd;
            text-align: right;
        }
        .assistant-message {
            background-color: #f5f5f5;
        }
        .typing-indicator {
            background-color: #fff3e0;
            font-style: italic;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        #messageInput {
            flex: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        #sendButton {
            padding: 10px 20px;
            background-color: #2196f3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        #sendButton:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .file-input {
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div id="messages" class="messages"></div>

        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Type your message..."
                   onkeypress="handleKeyPress(event)">
            <button id="sendButton" onclick="sendMessage()">Send</button>
        </div>

        <div class="file-input">
            <input type="file" id="imageInput" multiple accept="image/*">
            <label for="imageInput">📎 Attach Images</label>
        </div>
    </div>

    <script>
        // Initialize chat with conversation ID
        const conversationId = 'your-conversation-id'; // Get from your app
        const messagesContainer = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const imageInput = document.getElementById('imageInput');

        let currentAssistantMessage = null;
        let isStreaming = false;

        class ChatUI extends ChatStreamer {
            onToken(token, fullResponse) {
                if (!currentAssistantMessage) {
                    currentAssistantMessage = this.createMessageElement('assistant', '');
                    messagesContainer.appendChild(currentAssistantMessage);
                }

                // Update the message content
                const content = currentAssistantMessage.querySelector('.content');
                content.textContent = fullResponse;

                // Scroll to bottom
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            onStreamComplete(fullResponse) {
                currentAssistantMessage = null;
                sendButton.disabled = false;
                sendButton.textContent = 'Send';
                messageInput.disabled = false;
            }

            onError(error) {
                if (currentAssistantMessage) {
                    const content = currentAssistantMessage.querySelector('.content');
                    content.textContent = `Error: ${error}`;
                    content.style.color = 'red';
                }

                currentAssistantMessage = null;
                sendButton.disabled = false;
                sendButton.textContent = 'Send';
                messageInput.disabled = false;
            }

            createMessageElement(role, content) {
                const messageEl = document.createElement('div');
                messageEl.className = `message ${role}-message`;

                const contentEl = document.createElement('div');
                contentEl.className = 'content';
                contentEl.textContent = content;

                messageEl.appendChild(contentEl);
                return messageEl;
            }

            addUserMessage(content) {
                const messageEl = this.createMessageElement('user', content);
                messagesContainer.appendChild(messageEl);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }

        const chatUI = new ChatUI(conversationId);

        async function sendMessage() {
            const content = messageInput.value.trim();
            const images = Array.from(imageInput.files);

            if (!content && images.length === 0) {
                alert('Please enter a message or select images');
                return;
            }

            if (isStreaming) {
                return;
            }

            // Add user message to UI
            chatUI.addUserMessage(content);

            // Clear input
            messageInput.value = '';
            imageInput.value = '';

            // Disable input during streaming
            sendButton.disabled = true;
            sendButton.textContent = 'Sending...';
            messageInput.disabled = true;
            isStreaming = true;

            try {
                await chatUI.sendMessage(content, images.length > 0 ? images : null);
            } finally {
                isStreaming = false;
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        // Auto-focus input
        messageInput.focus();
    </script>
</body>
</html>
```

## Best Practices

### Connection Management

1. **Handle Connection State**:
```javascript
class ChatStreamer {
    constructor(conversationId) {
        this.conversationId = conversationId;
        this.abortController = null;
    }

    async sendMessage(content, images = null) {
        // Abort previous request if still running
        if (this.abortController) {
            this.abortController.abort();
        }

        this.abortController = new AbortController();

        try {
            const response = await fetch(`/chat/${this.conversationId}/send-stream`, {
                method: 'POST',
                body: formData,
                signal: this.abortController.signal
            });

            // ... rest of implementation
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Request was aborted');
                return;
            }
            throw error;
        }
    }

    abort() {
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
    }
}
```

2. **Reconnection Strategy**:
```javascript
class RobustChatStreamer extends ChatStreamer {
    constructor(conversationId, maxRetries = 3) {
        super(conversationId);
        this.maxRetries = maxRetries;
    }

    async sendMessageWithRetry(content, images = null, attempt = 1) {
        try {
            return await this.sendMessage(content, images);
        } catch (error) {
            if (attempt < this.maxRetries && this.isRetryableError(error)) {
                console.warn(`Attempt ${attempt} failed, retrying...`, error);
                await this.delay(1000 * attempt); // Exponential backoff
                return this.sendMessageWithRetry(content, images, attempt + 1);
            }
            throw error;
        }
    }

    isRetryableError(error) {
        return error.message.includes('network') ||
               error.message.includes('timeout') ||
               error.message.includes('502') ||
               error.message.includes('503');
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

### User Experience Considerations

1. **Typing Indicators**:
```javascript
onToken(token, fullResponse) {
    // Show typing indicator on first token
    if (!this.typingIndicator && fullResponse.length < 10) {
        this.showTypingIndicator();
    }

    // Hide typing indicator after a few tokens
    if (this.typingIndicator && fullResponse.length > 20) {
        this.hideTypingIndicator();
    }

    // Update message content
    this.updateMessageContent(fullResponse);
}
```

2. **Partial Response Display**:
```javascript
class SmartChatUI extends ChatStreamer {
    constructor(conversationId) {
        super(conversationId);
        this.updateThrottle = 50; // ms
        this.lastUpdate = 0;
    }

    onToken(token, fullResponse) {
        const now = Date.now();

        // Throttle UI updates for better performance
        if (now - this.lastUpdate > this.updateThrottle) {
            this.updateUI(fullResponse);
            this.lastUpdate = now;
        }

        // Always update on complete sentences
        if (token.includes('.') || token.includes('!') || token.includes('?')) {
            this.updateUI(fullResponse);
        }
    }
}
```

### Performance Optimization

1. **Buffering and Batching**:
```javascript
class OptimizedChatStreamer extends ChatStreamer {
    constructor(conversationId) {
        super(conversationId);
        this.tokenBuffer = [];
        this.batchSize = 5;
    }

    onToken(token, fullResponse) {
        this.tokenBuffer.push(token);

        // Update UI in batches for better performance
        if (this.tokenBuffer.length >= this.batchSize) {
            this.flushTokenBuffer();
        }
    }

    flushTokenBuffer() {
        if (this.tokenBuffer.length > 0) {
            const batch = this.tokenBuffer.join('');
            this.updateUI(batch);
            this.tokenBuffer = [];
        }
    }

    onStreamComplete(fullResponse) {
        this.flushTokenBuffer(); // Flush remaining tokens
        super.onStreamComplete(fullResponse);
    }
}
```

2. **Memory Management**:
```javascript
// Clean up event listeners and resources
window.addEventListener('beforeunload', () => {
    if (chatStreamer) {
        chatStreamer.abort();
    }
});

// Limit message history in UI
function trimMessageHistory(maxMessages = 100) {
    const messages = messagesContainer.children;
    while (messages.length > maxMessages) {
        messagesContainer.removeChild(messages[0]);
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Connection Timeouts

**Symptoms**: Stream stops unexpectedly, no completion signal
**Solutions**:
```javascript
// Add timeout handling
const timeoutId = setTimeout(() => {
    console.error('Stream timeout');
    chatStreamer.abort();
    onError('Request timed out');
}, 60000); // 60 second timeout

// Clear timeout on completion
onStreamComplete = (response) => {
    clearTimeout(timeoutId);
    // ... rest of completion handling
};
```

#### 2. Malformed JSON in Stream

**Symptoms**: JSON parse errors in browser console
**Solutions**:
```javascript
// Robust JSON parsing
function parseStreamData(data) {
    try {
        return JSON.parse(data);
    } catch (e) {
        console.warn('Invalid JSON in stream:', data);

        // Try to extract token from malformed data
        const tokenMatch = data.match(/"token":\s*"([^"]*?)"/);
        if (tokenMatch) {
            return { token: tokenMatch[1] };
        }

        return null;
    }
}
```

#### 3. CORS Issues

**Symptoms**: Network errors in browser, CORS policy violations
**Solutions**:
```python
# Backend: Ensure proper CORS headers
return StreamingResponse(
    event_generator(),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    },
)
```

#### 4. Memory Leaks

**Symptoms**: Increasing memory usage, browser slowdown
**Solutions**:
```javascript
// Proper cleanup
class ChatStreamer {
    cleanup() {
        if (this.reader) {
            this.reader.releaseLock();
            this.reader = null;
        }

        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }

        // Clear large response buffers
        this.responseBuffer = null;
    }
}

// Call cleanup on page unload
window.addEventListener('beforeunload', () => {
    chatStreamer.cleanup();
});
```

### Browser Compatibility

#### Fetch Streams Support
- **Chrome**: 43+ ✅
- **Firefox**: 65+ ✅
- **Safari**: 10.1+ ✅
- **Edge**: 79+ ✅

#### EventSource Fallback
For older browsers, implement EventSource fallback:

```javascript
class CompatibleChatStreamer {
    constructor(conversationId) {
        this.conversationId = conversationId;
        this.supportsStreams = 'body' in Response.prototype && 'getReader' in ReadableStream.prototype;
    }

    async sendMessage(content, images = null) {
        if (this.supportsStreams) {
            return this.sendStreamingMessage(content, images);
        } else {
            return this.sendPollingMessage(content, images);
        }
    }

    async sendPollingMessage(content, images) {
        // Fallback: Regular request with polling for completion
        const response = await fetch(`/chat/${this.conversationId}/send`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        // Simulate streaming by showing characters gradually
        this.simulateStreaming(result.response);
        return result;
    }

    simulateStreaming(text, delay = 50) {
        let index = 0;
        const interval = setInterval(() => {
            if (index < text.length) {
                this.onToken(text[index], text.substring(0, index + 1));
                index++;
            } else {
                clearInterval(interval);
                this.onStreamComplete(text);
            }
        }, delay);
    }
}
```

### Debugging Streaming Connections

#### Enable Debug Logging

**Backend**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

async def event_generator():
    try:
        logger.debug(f"Starting stream for conversation {conv_id}")

        async for token in chatbot.stream_response(content, image_paths):
            logger.debug(f"Streaming token: {token[:20]}...")
            yield f"data: {json.dumps({'token': token})}\n\n"

        logger.debug("Stream completed successfully")
        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"Stream error: {e}", exc_info=True)
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
```

**Frontend**:
```javascript
class DebugChatStreamer extends ChatStreamer {
    onToken(token, fullResponse) {
        console.debug('Token received:', {
            token: token,
            length: fullResponse.length,
            timestamp: new Date().toISOString()
        });
        super.onToken(token, fullResponse);
    }

    onError(error) {
        console.error('Stream error details:', {
            error: error,
            conversationId: this.conversationId,
            timestamp: new Date().toISOString(),
            isStreaming: this.isStreaming
        });
        super.onError(error);
    }
}
```

#### Network Monitoring
```javascript
// Monitor network quality
class NetworkAwareChatStreamer extends ChatStreamer {
    constructor(conversationId) {
        super(conversationId);
        this.connectionQuality = 'good';
        this.monitorConnection();
    }

    monitorConnection() {
        if ('connection' in navigator) {
            const connection = navigator.connection;

            const updateQuality = () => {
                if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                    this.connectionQuality = 'poor';
                } else if (connection.effectiveType === '3g') {
                    this.connectionQuality = 'moderate';
                } else {
                    this.connectionQuality = 'good';
                }

                console.log('Connection quality:', this.connectionQuality);
            };

            connection.addEventListener('change', updateQuality);
            updateQuality();
        }
    }

    getOptimalBatchSize() {
        switch (this.connectionQuality) {
            case 'poor': return 10;
            case 'moderate': return 5;
            default: return 1;
        }
    }
}
```

## Complete Working Example

Here's a minimal but complete example that you can test immediately:

### Backend Test Endpoint
```python
# test_streaming.py
from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

@app.post("/test-stream")
async def test_stream(message: str = Form(...)):
    async def generate():
        # Simulate AI response
        words = f"Echo: {message}".split()

        for word in words:
            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
            await asyncio.sleep(0.1)  # Simulate processing delay

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

### Frontend Test Page
```html
<!-- test_streaming.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Streaming Test</title>
</head>
<body>
    <div>
        <input type="text" id="messageInput" placeholder="Enter test message">
        <button onclick="testStream()">Test Stream</button>
    </div>
    <div id="output"></div>

    <script>
        async function testStream() {
            const message = document.getElementById('messageInput').value;
            const output = document.getElementById('output');
            output.innerHTML = '';

            const formData = new FormData();
            formData.append('message', message);

            try {
                const response = await fetch('http://127.0.0.1:8000/test-stream', {
                    method: 'POST',
                    body: formData
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);

                            if (data === '[DONE]') {
                                output.innerHTML += '<br><strong>Stream Complete!</strong>';
                                return;
                            }

                            try {
                                const parsed = JSON.parse(data);
                                if (parsed.token) {
                                    output.innerHTML += parsed.token;
                                }
                            } catch (e) {
                                console.warn('Parse error:', e);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                output.innerHTML = `Error: ${error.message}`;
            }
        }
    </script>
</body>
</html>
```

## Conclusion

This streaming implementation provides:

- **Real-time Response**: Token-by-token streaming for immediate feedback
- **Multimodal Support**: Text and image inputs with proper handling
- **Error Recovery**: Robust error handling and reconnection strategies
- **Performance**: Optimized for smooth user experience
- **Browser Compatibility**: Works across modern browsers with fallbacks
- **Scalability**: Designed for production use with proper resource cleanup

The implementation balances real-time responsiveness with system reliability, providing a smooth chat experience while maintaining robust error handling and resource management.

**Key Implementation Files**:
- Backend: `api/chat.py` - Streaming endpoint
- Chatbot: `services/conversation/GeminiMultimodalChatbot.py` - Token generation
- Frontend: Custom JavaScript EventSource implementation
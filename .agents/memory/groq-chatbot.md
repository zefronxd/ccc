---
name: Groq chatbot responses
description: Non-obvious Groq response and failure behavior for this bot's chatbot integration.
---

Groq's OpenAI-compatible chat response stores assistant text at `choices[0].message.content`. A model that the API key cannot access can return `model_not_found`, which otherwise looks like a generic chatbot fallback to users.

**Why:** The chatbot originally handled legacy provider response shapes, so a successful Groq response could be discarded silently, while unavailable models produced the same user-facing fallback.

**How to apply:** Keep the extractor recursive for nested `message` objects and include string `content`; log non-success response status and a short response body without logging credentials.
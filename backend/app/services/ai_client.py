"""
Reliable AI client with Groq → Anthropic fallback, timeout, and retry logic.
"""
import asyncio
import json
import re
import logging
from typing import Optional

import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIClientError(Exception):
    pass


# ── Groq (primary, faster + cheaper) ────────────────────────────────────────

async def _call_groq(prompt: str, max_tokens: int = 2000) -> str:
    if not settings.GROQ_API_KEY:
        raise AIClientError("GROQ_API_KEY not configured")

    async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            json={
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.3,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


# ── Anthropic (fallback) ─────────────────────────────────────────────────────

async def _call_anthropic(prompt: str, max_tokens: int = 2000) -> str:
    if not settings.ANTHROPIC_API_KEY:
        raise AIClientError("ANTHROPIC_API_KEY not configured")

    async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]


# ── Unified chat with fallback ───────────────────────────────────────────────

async def chat(
    prompt: str,
    max_tokens: int = 2000,
    retries: int = None,
) -> str:
    """
    Try Groq first. On failure, retry then fall back to Anthropic.
    """
    max_retries = retries if retries is not None else settings.AI_MAX_RETRIES

    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"AI call attempt {attempt + 1} via Groq")
            return await _call_groq(prompt, max_tokens)
        except Exception as groq_err:
            logger.warning(f"Groq attempt {attempt + 1} failed: {groq_err}")
            if attempt < max_retries:
                await asyncio.sleep(0.5 * (attempt + 1))
            else:
                break

    # Fallback to Anthropic
    try:
        logger.info("Falling back to Anthropic Claude")
        return await _call_anthropic(prompt, max_tokens)
    except Exception as claude_err:
        raise AIClientError(f"All AI providers failed. Last error: {claude_err}")


# ── JSON-safe chat ────────────────────────────────────────────────────────────

async def chat_json(prompt: str, max_tokens: int = 2000) -> dict | list:
    """
    Call AI and parse JSON response. Strips markdown fences.
    """
    raw = await chat(prompt, max_tokens)
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()

    # Extract JSON from response (handles preamble text)
    json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', cleaned)
    if json_match:
        cleaned = json_match.group(1)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw response: {raw[:500]}")
        raise AIClientError(f"AI returned invalid JSON: {e}")

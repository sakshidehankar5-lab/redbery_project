"""
LLM Extraction Service
-----------------------
Supports OpenAI, Anthropic, and Azure OpenAI.
Uses the extraction templates to build structured prompts.

Pattern: Provider Strategy + Template Method
"""
import json
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.core.exceptions import LLMException, LLMRateLimitException, LLMResponseParseException
from app.core.logging import get_logger, log_exceptions, log_execution
from app.extractors.templates.extraction_templates import ExtractionTemplate, get_template

settings = get_settings()
log = get_logger(__name__)


# ── LLM Provider Strategy ─────────────────────────────────────────────────────

class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, system: str, user: str) -> tuple[str, str]:
        """Returns (response_text, model_name)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
            self._model = settings.openai_model
        except ImportError as e:
            raise LLMException("openai package not installed", cause=e)

    @property
    def provider_name(self) -> str:
        return "openai"

    @log_exceptions
    async def complete(self, system: str, user: str) -> tuple[str, str]:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or "", self._model
        except Exception as e:
            err_str = str(e).lower()
            if "rate" in err_str or "429" in err_str:
                raise LLMRateLimitException(f"OpenAI rate limit: {e}", cause=e)
            raise LLMException(f"OpenAI error: {e}", cause=e)


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        try:
            import anthropic
            self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            self._model = settings.anthropic_model
        except ImportError as e:
            raise LLMException("anthropic package not installed", cause=e)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @log_exceptions
    async def complete(self, system: str, user: str) -> tuple[str, str]:
        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=2048,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return message.content[0].text, self._model
        except Exception as e:
            err_str = str(e).lower()
            if "rate" in err_str or "429" in err_str:
                raise LLMRateLimitException(f"Anthropic rate limit: {e}", cause=e)
            raise LLMException(f"Anthropic error: {e}", cause=e)


class AzureOpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        try:
            from openai import AsyncAzureOpenAI
            self._client = AsyncAzureOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_key,
                api_version="2024-02-01",
            )
            self._deployment = settings.azure_openai_deployment
        except ImportError as e:
            raise LLMException("openai package not installed", cause=e)

    @property
    def provider_name(self) -> str:
        return "azure_openai"

    async def complete(self, system: str, user: str) -> tuple[str, str]:
        try:
            response = await self._client.chat.completions.create(
                model=self._deployment,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.0,
            )
            return response.choices[0].message.content or "", self._deployment
        except Exception as e:
            raise LLMException(f"Azure OpenAI error: {e}", cause=e)


class OllamaProvider(LLMProvider):
    def __init__(self) -> None:
        import httpx
        self._base_url = settings.ollama_base_url
        self._model = settings.ollama_model
        self._client = httpx.AsyncClient(timeout=120.0)

    @property
    def provider_name(self) -> str:
        return "ollama"

    @log_exceptions
    async def complete(self, system: str, user: str) -> tuple[str, str]:
        try:
            response = await self._client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "stream": False,
                    "options": {"temperature": 0.0},
                },
            )
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"], self._model
        except Exception as e:
            raise LLMException(f"Ollama error: {e}", cause=e)


# ── Provider Factory ──────────────────────────────────────────────────────────

def build_llm_provider(provider: Optional[str] = None) -> LLMProvider:
    p = (provider or settings.llm_provider).lower()
    if p == "openai":
        return OpenAIProvider()
    elif p == "anthropic":
        return AnthropicProvider()
    elif p == "azure_openai":
        return AzureOpenAIProvider()
    elif p == "ollama":
        return OllamaProvider()
    raise LLMException(f"Unknown LLM provider: {p}")


# ── LLM Extraction Service ────────────────────────────────────────────────────

class LLMExtractionService:
    """
    Orchestrates LLM-based field extraction using templates.
    """

    def __init__(self, provider: Optional[LLMProvider] = None) -> None:
        self._provider = provider or build_llm_provider()

    @log_execution
    @log_exceptions
    async def extract_fields(
        self,
        ocr_text: str,
        document_type: str,
        custom_fields: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Given OCR text and document_type, returns {extracted_fields, model, processing_time_ms}.
        """
        template = get_template(document_type)

        system_prompt = self._build_system_prompt(template)
        user_prompt = self._build_user_prompt(ocr_text, template, custom_fields)

        log.info(
            f"LLM extraction | provider={self._provider.provider_name} "
            f"| doc_type={document_type} | ocr_chars={len(ocr_text)}"
        )

        t0 = time.perf_counter()
        raw_response, model_name = await self._provider.complete(system_prompt, user_prompt)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        extracted = self._parse_json_response(raw_response, template)

        log.info(
            f"LLM extraction complete | model={model_name} | "
            f"fields_extracted={len(extracted)} | time={elapsed_ms:.1f}ms"
        )

        return {
            "extracted_fields": extracted,
            "raw_llm_response": raw_response,
            "llm_model": model_name,
            "processing_time_ms": round(elapsed_ms, 2),
        }

    # ── Prompt builders ───────────────────────────────────────────

    @staticmethod
    def _build_system_prompt(template: ExtractionTemplate) -> str:
        field_list = "\n".join(
            f"  - {f.name} ({f.description})"
            + (f" [example: {f.example}]" if f.example else "")
            + (" [REQUIRED]" if f.required else " [optional]")
            for f in template.fields
        )
        return f"""You are an intelligent document data extraction system.
{template.system_instructions}

Extract the following fields and return ONLY valid JSON with no additional text:
{field_list}

Rules:
- Return ONLY a JSON object. No markdown, no explanation.
- Use null for missing or illegible fields.
- Keep original formatting for numbers and dates.
- For arrays (like line_items), use a JSON array.
"""

    @staticmethod
    def _build_user_prompt(
        ocr_text: str,
        template: ExtractionTemplate,
        custom_fields: Optional[list],
    ) -> str:
        field_names = [f.name for f in template.fields]
        if custom_fields:
            field_names = [f for f in field_names if f in custom_fields] or field_names

        return (
            f"Document Type: {template.display_name}\n"
            f"Fields to extract: {', '.join(field_names)}\n\n"
            f"OCR Text:\n```\n{ocr_text}\n```\n\n"
            "Extract and return JSON."
        )

    # ── Response parser ───────────────────────────────────────────

    @staticmethod
    def _parse_json_response(raw: str, template: ExtractionTemplate) -> Dict[str, Any]:
        # Strip markdown code fences if present
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            parsed = json.loads(clean)
        except json.JSONDecodeError as e:
            # Attempt to extract JSON object from free text
            match = re.search(r"\{.*\}", clean, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                except json.JSONDecodeError:
                    raise LLMResponseParseException(
                        f"Could not parse LLM JSON response: {e}",
                        details={"raw_response": raw[:500]},
                        cause=e,
                    )
            else:
                raise LLMResponseParseException(
                    "No JSON object found in LLM response",
                    details={"raw_response": raw[:500]},
                    cause=e,
                )

        if not isinstance(parsed, dict):
            raise LLMResponseParseException(
                "LLM response is not a JSON object",
                details={"parsed_type": type(parsed).__name__},
            )

        return parsed

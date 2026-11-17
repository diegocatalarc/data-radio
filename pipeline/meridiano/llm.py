"""Cliente LLM mínimo. Proveedores: deepseek (por defecto, API compatible con OpenAI) o anthropic.
Sin la clave del proveedor (o con MERIDIANO_MOCK=1) funciona en modo simulado para probar el flujo."""
from __future__ import annotations
import json, os, re, time

import httpx

PROVIDERS = {
    "deepseek": {"key_env": "DEEPSEEK_API_KEY", "base_url": "https://api.deepseek.com"},
    "anthropic": {"key_env": "ANTHROPIC_API_KEY", "base_url": None},
}


def current_provider() -> str:
    return os.environ.get("MERIDIANO_PROVIDER", "deepseek")


def mock_enabled(provider: str | None = None) -> bool:
    p = PROVIDERS[provider or current_provider()]
    return os.environ.get("MERIDIANO_MOCK") == "1" or not os.environ.get(p["key_env"])


def extract_json(text: str):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1).strip()
    start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
    if start < 0:
        raise ValueError(f"La respuesta no contiene JSON: {text[:200]}")
    return json.JSONDecoder().raw_decode(text[start:])[0]


class LLM:
    def __init__(self, provider: str | None = None):
        self.provider = provider or current_provider()
        if self.provider not in PROVIDERS:
            raise ValueError(f"Proveedor desconocido: {self.provider}")
        self.mock = mock_enabled(self.provider)
        self.calls = 0
        self._anthropic = None

    @staticmethod
    def split_model(model: str) -> tuple[str, bool]:
        """'deepseek-flash:thinking' -> ('deepseek-flash', True). Sin sufijo, el razonamiento queda desactivado."""
        name, _, flag = model.partition(":")
        return name, flag == "thinking"

    def complete(self, model: str, system: str, user: str, max_tokens: int = 2000, json_mode: bool = False) -> str:
        self.calls += 1
        model, thinking = self.split_model(model)
        if self.provider == "anthropic":
            if self._anthropic is None:
                import anthropic  # opcional: pip install -e ".[anthropic]"
                self._anthropic = anthropic.Anthropic()
            r = self._anthropic.messages.create(model=model, max_tokens=max_tokens, system=system,
                                                messages=[{"role": "user", "content": user}])
            return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        return self._deepseek(model, system, user, max_tokens, json_mode, thinking)

    def _deepseek(self, model, system, user, max_tokens, json_mode, thinking=False) -> str:
        cfg = PROVIDERS["deepseek"]
        # En modo thinking, el razonamiento consume max_tokens y no admite temperature.
        body = {"model": model, "max_tokens": max_tokens + (4000 if thinking else 0),
                "thinking": {"type": "enabled" if thinking else "disabled"},
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if not thinking:
            body["temperature"] = 0.3
        if json_mode:   # exige la palabra "json" en el prompt (los prompts la incluyen)
            body["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {os.environ[cfg['key_env']]}"}
        for attempt in range(4):
            try:
                r = httpx.post(f"{cfg['base_url']}/chat/completions", json=body, headers=headers, timeout=180)
                if r.status_code in (429, 500, 502, 503, 504):
                    raise httpx.HTTPStatusError("reintentable", request=r.request, response=r)
                r.raise_for_status()
                content = r.json()["choices"][0]["message"]["content"] or ""
                if json_mode and not content.strip():   # DeepSeek devuelve espacios si no logra producir JSON válido
                    raise httpx.TransportError("respuesta JSON vacía")
                return content
            except (httpx.TransportError, httpx.HTTPStatusError) as ex:
                retryable = isinstance(ex, httpx.TransportError) or ex.response.status_code in (429, 500, 502, 503, 504)
                if not retryable or attempt == 3:
                    raise
                time.sleep(2 ** attempt * 2)
        raise RuntimeError("inalcanzable")

    def json(self, model: str, system: str, user: str, max_tokens: int = 2000):
        return extract_json(self.complete(model, system, user, max_tokens, json_mode=True))

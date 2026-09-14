import base64
import os
from typing import List, Optional

import requests
from django.conf import settings


def _get_config():
    cfg = {
        'base_url': os.environ.get('LLM_BASE_URL', 'https://api.bazaarlink.ai/v1').rstrip('/'),
        'api_key': os.environ.get('BAZAARLINK_API_KEY', ''),
        'model': os.environ.get('LLM_MODEL_NAME', 'google/gemini-3.8-flash'),
    }
    ms = getattr(settings, '_FACEAPP_LLM_CACHE', None)
    return cfg


def chat_completion(messages: List[dict], model: Optional[str] = None,
                    base_url: Optional[str] = None, api_key: Optional[str] = None,
                    temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
    cfg = _get_config()
    if base_url is None:
        base_url = cfg['base_url']
    if api_key is None:
        api_key = cfg['api_key']
    if not api_key:
        raise RuntimeError('LLM_API_KEY / BAZAARLINK_API_KEY belum diatur di environment.')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': model or cfg['model'],
        'messages': messages,
        'temperature': temperature,
    }
    if max_tokens:
        payload['max_tokens'] = max_tokens
    resp = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data['choices'][0]['message']['content']


def describe_image(image_bytes: bytes, prompt: str = "Deskripsikan secara singkat apa yang terlihat pada wajah/gambar ini.",
                   base_url=None, api_key=None) -> str:
    encoded = base64.b64encode(image_bytes).decode('utf-8')
    messages = [
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': prompt},
                {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{encoded}'}},
            ],
        }
    ]
    return chat_completion(messages, base_url=base_url, api_key=api_key)

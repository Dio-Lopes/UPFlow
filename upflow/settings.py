"""Configuração única de broker e espaços."""
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import os
import re

from dotenv import load_dotenv
import json

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
VALID_ID = re.compile(r'^[a-z0-9][a-z0-9_-]*$')


@dataclass(frozen=True)
class Venue:
    campus: str
    id: str
    name: str
    capacity: int
    initial_occupied: int

    @property
    def base_topic(self) -> str:
        return f'upflow/v1/{self.campus}/{self.id}'


def load_venues(path: Path | None = None) -> list[Venue]:
    file_path = path or ROOT / 'config' / 'venues.json'
    payload = json.loads(file_path.read_text(encoding='utf-8'))
    venues = [Venue(**v) for v in payload]
    seen: set[tuple[str, str]] = set()
    for v in venues:
        if not VALID_ID.fullmatch(v.campus) or not VALID_ID.fullmatch(v.id):
            raise ValueError(f'Identificador inválido: {v.campus}/{v.id}')
        if v.capacity <= 0 or not 0 <= v.initial_occupied <= v.capacity:
            raise ValueError(f'Capacidade/lotação inicial inválida para {v.id}')
        if (v.campus, v.id) in seen:
            raise ValueError(f'Identificador duplicado: {v.campus}/{v.id}')
        seen.add((v.campus, v.id))
    return venues


@dataclass(frozen=True)
class Broker:
    host: str
    port: int
    tls: bool
    username: str
    password: str


def broker_settings() -> Broker:
    supplied = os.getenv('MQTT_HOST', 'localhost').strip()
    if '://' in supplied:
        parsed = urlparse(supplied)
        if parsed.scheme not in {'mqtt', 'mqtts'} or not parsed.hostname:
            raise ValueError('MQTT_HOST deve ser um hostname ou URL mqtt(s)://')
        host = parsed.hostname
        inferred_tls = parsed.scheme == 'mqtts'
        inferred_port = parsed.port
    else:
        host = supplied
        inferred_tls = False
        inferred_port = None
    if not host or '/' in host:
        raise ValueError('MQTT_HOST inválido')
    tls = os.getenv('MQTT_TLS', str(inferred_tls)).strip().lower() in {'1', 'true', 'yes'}
    port = int(os.getenv('MQTT_PORT', inferred_port or (8883 if tls else 1883)))
    return Broker(host, port, tls, os.getenv('MQTT_USERNAME', ''), os.getenv('MQTT_PASSWORD', ''))


def topic(campus: str, venue: str, stream: str, name: str) -> str:
    if not all(VALID_ID.fullmatch(s) for s in (campus, venue, stream, name)):
        raise ValueError('Tópico contém segmento inválido')
    return f'upflow/v1/{campus}/{venue}/{stream}/{name}'

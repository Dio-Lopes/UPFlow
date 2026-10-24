"""Manual: python -m upflow.publisher --venue bar_minas --occupied 37"""
import argparse
import json
from datetime import datetime, timezone

from .settings import load_venues, topic
from .mqtt_client import connect_client, send


def make_reading(venue, occupied: int, source='demo_manual') -> dict:
    if not 0 <= occupied <= venue.capacity:
        raise ValueError(f'Lotação deve estar entre 0 e {venue.capacity}')
    return {
        'occupied': occupied,
        'capacity': venue.capacity,
        'observed_at': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'source': source,
    }


def main():
    p = argparse.ArgumentParser(description='Publica uma leitura de lotação na Coreflux')
    p.add_argument('--campus', default='feup')
    p.add_argument('--venue', required=True)
    p.add_argument('--occupied', type=int, required=True)
    args = p.parse_args()
    matches = [v for v in load_venues() if v.campus == args.campus and v.id == args.venue]
    if not matches:
        p.error('Espaço desconhecido; consulta config/venues.json')
    venue = matches[0]
    payload = json.dumps(make_reading(venue, args.occupied), separators=(',', ':'))
    dest = topic(venue.campus, venue.id, 'raw', 'reading')
    client = connect_client('manual')
    try:
        send(client, dest, payload, retain=True)
        print(f'Publicado {dest}: {payload}')
    finally:
        client.disconnect()
        client.loop_stop()

if __name__ == '__main__':
    main()

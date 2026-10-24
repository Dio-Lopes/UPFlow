"""Envia leituras simuladas"""
import argparse
import json
import random
import time

from .settings import load_venues, topic
from .mqtt_client import connect_client, send
from .publisher import make_reading


def main():
    p = argparse.ArgumentParser(description='Simulador de cantinas UPFlow')
    p.add_argument('--interval', type=float, default=5, help='Segundos entre ciclos')
    p.add_argument('--once', action='store_true', help='Publicar uma leitura por cantina e terminar')
    args = p.parse_args()
    if args.interval <= 0:
        p.error('--interval tem de ser positivo')
    venues = load_venues()
    rng = random.Random(2026)
    occupancy = {(v.campus, v.id): v.initial_occupied for v in venues}
    client = connect_client('simulator')
    print('Simulador ligado ao broker. Ctrl+C para parar. Dados NÃO REAIS.')
    try:
        while True:
            for v in venues:
                key = (v.campus, v.id)
                step = 0 if args.once else rng.randint(-max(3,v.capacity//12), max(3,v.capacity//12))
                occupancy[key] = max(0, min(v.capacity, occupancy[key] + step))
                message = json.dumps(make_reading(v, occupancy[key], 'demo_simulator'), separators=(',', ':'))
                dest = topic(v.campus, v.id, 'raw', 'reading')
                send(client, dest, message, retain=True)
                print(f'{v.name:25s} {occupancy[key]:3}/{v.capacity} -> {dest}')
            if args.once:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('\nSimulador parado.')
    finally:
        client.disconnect()
        client.loop_stop()

if __name__ == '__main__':
    main()

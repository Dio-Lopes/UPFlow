"""Conexão MQTT comum para simulador, dashboard e publicações manuais."""
import ssl
import threading
import uuid

from .settings import broker_settings


def connect_client(role: str, on_message=None, subscriptions=()):
    import paho.mqtt.client as mqtt
    cfg = broker_settings()
    connected = threading.Event()
    error = []
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f'upflow-{role}-{uuid.uuid4().hex[:10]}',
        protocol=mqtt.MQTTv311,
    )
    if cfg.username:
        client.username_pw_set(cfg.username, cfg.password)
    if cfg.tls:
        client.tls_set_context(ssl.create_default_context())

    def handle_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            error.append(str(reason_code))
            connected.set()
            return
        for subscription in subscriptions:
            client.subscribe(subscription, qos=1)
        connected.set()

    client.on_connect = handle_connect
    if on_message is not None:
        client.on_message = on_message
    client.connect(cfg.host, cfg.port, keepalive=60)
    client.loop_start()
    if not connected.wait(timeout=12):
        client.loop_stop()
        raise RuntimeError(f'Sem resposta MQTT de {cfg.host}:{cfg.port}. Verifica host/porta/TLS.')
    if error:
        client.loop_stop()
        raise RuntimeError(f'Ligação MQTT recusada: {error[-1]}')
    return client


def send(client, topic_name: str, value: str, retain=True):
    info = client.publish(topic_name, value, qos=1, retain=retain)
    info.wait_for_publish(timeout=8)
    if not info.is_published():
        raise RuntimeError(f'Não foi possível publicar em {topic_name}')

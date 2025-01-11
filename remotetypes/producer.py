import sys
import json
from confluent_kafka import Producer


def create_publisher(bootstrap_server: str) -> Producer:
    return Producer({"bootstrap.servers": bootstrap_server})


def send_message(producer: Producer, topic: str, payload: dict, key: str = None) -> None:
    message = json.dumps(payload).encode("utf-8")
    producer.produce(topic, message, key)
    producer.flush()


def main():
    if len(sys.argv) < 5:
        print("Uso: python publisher.py <bootstrap_server> <topic> <id> <object_identifier> <object_type> <operation> [<args>]")
        sys.exit(1)

    # Argumentos requeridos
    server = sys.argv[1]
    topic = sys.argv[2]
    operation_id = sys.argv[3]
    object_identifier = sys.argv[4]
    object_type = sys.argv[5]
    operation = sys.argv[6]

    # Argumento opcional: args
    args = json.loads(sys.argv[7]) if len(sys.argv) > 7 else {}

    # Construir el mensaje según el formato especificado
    message = [
        {
            "id": operation_id,
            "object_identifier": object_identifier,
            "object_type": object_type,
            "operation": operation,
            "args": args if args else None  # Solo incluir "args" si no está vacío
        }
    ]

    # Crear el publisher y enviar el mensaje
    publisher = create_publisher(server)
    send_message(publisher, topic, message)
    print(f"Mensaje enviado a {topic}: {json.dumps(message, indent=4)}")


if __name__ == "__main__":
    main()

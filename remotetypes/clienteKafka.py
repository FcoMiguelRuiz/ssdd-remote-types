import json
from confluent_kafka import Consumer, Producer
import sys
import Ice
import RemoteTypes as rt

# Configuración Kafka
KAFKA_BROKER = "localhost:9092"
INPUT_TOPIC = "main_topic"
OUTPUT_TOPIC = "responses"
GROUP_ID = "Francisco_Ruiz"
OFFSET = "earliest"

# Inicializar cliente Ice
def initialize_ice():
    communicator = Ice.initialize(sys.argv)
    proxy = communicator.stringToProxy("factory:default -h localhost -p 10000")
    factory = rt.FactoryPrx.uncheckedCast(proxy)
    print("conectado")
    if not factory:
        raise RuntimeError("Invalid Factory proxy")
    return communicator, factory

def process_event(event, factory):
    """Procesar un evento individual del topic"""
    response = {"id": event["id"]}
    try:
        obj_type = event["object_type"]
        obj_id = event["object_identifier"]
        operation = event["operation"]
        args = event.get("args", {})

        # Obtener proxy del objeto remoto
        obj_proxy = factory.get(getattr(rt.TypeName, obj_type), obj_id)
        if obj_type == "RDict":
            remote_obj = rt.RDictPrx.checkedCast(obj_proxy)
        elif obj_type == "RList":
            remote_obj = rt.RListPrx.checkedCast(obj_proxy)
        elif obj_type == "RSet":
            remote_obj = rt.RSetPrx.checkedCast(obj_proxy)
        else:
            raise ValueError("Invalid object type")

        if operation == "iter":
            raise Exception("OperationNotSupported")

        # Ejecutar operación
        method = getattr(remote_obj, operation)
        result = method(**args) if args else method()
        response["status"] = "ok"
        response["result"] = result if result is not None else None
    except Exception as e:
        response["status"] = "error"
        response["error"] = type(e).__name__
    return response

def main():
    # Configurar Kafka
    consumer_config = {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": GROUP_ID,
        "auto.offset.reset": OFFSET,
    }
    producer_config = {"bootstrap.servers": KAFKA_BROKER}

    consumer = Consumer(consumer_config)
    producer = Producer(producer_config)

    consumer.subscribe([INPUT_TOPIC])

    communicator, factory = initialize_ice()

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            try:
                events = json.loads(msg.value().decode("utf-8"))
                print(events)
                responses = [process_event(event, factory) for event in events]
                print(json.dumps(responses))
                producer.produce(OUTPUT_TOPIC, json.dumps(responses).encode("utf-8"))
                producer.flush()
            except json.JSONDecodeError:
                print("Error decoding JSON message")
    except KeyboardInterrupt:
        print("Terminated by user")
    finally:
        consumer.close()
        communicator.destroy()

if __name__ == "__main__":
    main()

import json
from confluent_kafka import Consumer, Producer, KafkaException, KafkaError
import sys
import Ice
import RemoteTypes as rt


def load_config(file_path):
    """Carga configuraciones desde un archivo de texto, en caso de que no exista crear uno predeterminado"""
    config = {}
    default_config = {
            "KAFKA_BROKER": "localhost:9092",
            "INPUT_TOPIC": "main_topic",
            "OUTPUT_TOPIC": "responses",
            "GROUP_ID": "Francisco_Ruiz",
            "OFFSET": "earliest"
    }
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    except FileNotFoundError:
        print(f"El archivo de configuración {file_path} no fue encontrado. Creando uno con valores predeterminados") 
        with open(file_path, "w") as file:
            for key, value in default_config.items():
                file.write(f"{key}={value}\n")
        return default_config

    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
        print("Se va a utilizar la configuración por defecto")
        return default_config

    return config

def initialize_ice():
    """Inicializa el cliente Ice"""
    communicator = Ice.initialize(sys.argv)
    proxy = communicator.stringToProxy("factory:default -h localhost -p 10000")
    factory = rt.FactoryPrx.uncheckedCast(proxy)
    print("conectado")
    if not factory:
        raise RuntimeError("Invalid Factory proxy")
    return communicator, factory

def process_event(event, factory):
    """Procesar un evento individual del topic"""
    try:   
        response = {"id": event["id"]}
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
            raise ValueError("Tipo de objeto remoto invalido")

        if operation == "iter":
            raise Exception("OperationNotSupported")

        # Ejecutar operación
        method = getattr(remote_obj, operation)
        result = method(**args) if args else method()
        response["status"] = "ok"
        response["result"] = result if result is not None else None
    except KeyError as e:
        raise KeyError("Error al analizar el mensaje, faltan las claves necesarias")
    except Exception as e:
        response["status"] = "error"
        response["error"] = type(e).__name__
    return response

def main():
    config_path = "config.txt"  #ruta al archivo de configuración
    config = load_config(config_path)
    try:
        #Cargar las variables obtenidas del archivo de configuración
        kafka_broker = config["KAFKA_BROKER"]
        input_topic = config["INPUT_TOPIC"]
        output_topic = config["OUTPUT_TOPIC"]
        group_id = config["GROUP_ID"]
        offset = config["OFFSET"]
    
        consumer_config = {
            "bootstrap.servers": kafka_broker,
            "group.id": group_id,
            "auto.offset.reset": offset,
        }
        producer_config = {"bootstrap.servers": kafka_broker}
    
    
        consumer = Consumer(consumer_config)
        producer = Producer(producer_config)
        consumer.subscribe([input_topic])
        communicator, factory = initialize_ice()
    except KafkaException as e:
        if e.args[0].code() == KafkaError._INVALID_ARG:
            print(f"Argumentos incorrectos en el documento config.txt, por favor comprueba que todos los argumentos son válidos")
            print(f"{e}")
        else:
            print(f"Error al utilizar Kafka: {e}")
        sys.exit(1)
    except Exception:
        print("Error de configuración al crear el cliente por favor borre el documento config.txt")
        sys.exit(1)
    
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
                producer.produce(output_topic, json.dumps(responses).encode("utf-8"))
                producer.flush()
            except json.JSONDecodeError:
                print("Error descodificando el mensaje JSON")
            except Exception as e:
                print(f"Error en el evento: {e}")
     
    except KeyboardInterrupt:
        print("Terminated by user")
    finally:
        consumer.close()
        communicator.destroy()

if __name__ == "__main__":
    main()

from confluent_kafka import Producer
import socket
from pathlib import Path
conf = {'bootstrap.servers': 'localhost:9092',
        'client.id': socket.gethostname()}

producer = Producer(conf)

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))

def main():
    print("enter to main")
    BASE_DIR=Path(__file__).parent.parent
    file_path = BASE_DIR / "AllDataFiles" / "developer_ai_learning_raw.csv"
    try:
        with open(file_path,"r") as f:
            rows=f.readlines()
            for r in rows:
                producer.produce(topic='RawData',
                                 value=r.strip(),
                                 callback=acked
                                 )
                producer.poll(0)
            print("Flushing remaining messages...")
            producer.flush()
        print("all messages delivered")
    except FileNotFoundError:
        print(f"error file {file_path} not found")

if __name__=="__main__":
    main()
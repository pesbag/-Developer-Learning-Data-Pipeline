import io
import json
import sys
import pandas as pd
from pathlib import Path
from ScriptOnLearnDataCsvUpdated import clean_script
from confluent_kafka import Consumer, KafkaException, KafkaError
from confluent_kafka import Producer
import socket
# BASE_DIR=Path(__file__).parent.parent
# file_path=BASE_DIR/"RawValidator"
# from
# CSV_COLUMNS = [
#     'ResponseId', 'Age', 'YearsCode', 'DevType',
#     'LearnCodeChoose', 'LearnCode', 'LearnCodeAI',
#     'AILearnHow', 'AISelect', 'AIAcc', 'AISent'
# ]
producerConf = {'bootstrap.servers': 'localhost:9092',
        'client.id': socket.gethostname()}
consumerConf = {'bootstrap.servers': 'localhost:9092',
        'group.id': 'RawData_5',
        'auto.offset.reset': 'earliest'}
producer = Producer(producerConf)
consumer = Consumer(consumerConf)
running=True
def raw_producer_loop(consumer,topics):
    try:
        consumer.subscribe(topics)
        counter=0
        while running:
            msg=consumer.poll(timeout=1)
            if msg is None:
                print(f"no more message recived.total messages: {counter}")
                break

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                counter+=1
                raw_text = msg.value().decode("utf-8")
                data_dict=json.loads(raw_text)
                df=pd.DataFrame([data_dict])
                clean_df=clean_script(df)
                if clean_df is None:
                    continue
                clean_csv_str = clean_df.to_csv(index=False, header=False).strip()
                producer.produce(topic='cleanData',
                                 value=clean_csv_str.encode('utf-8'),
                                 callback=acked
                                 )
                producer.poll(0)

    finally:
        print("Flushing remaining messages and closing consumer...")
        producer.flush()
        consumer.close()
counter=0
def acked(err, msg):
    global counter
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        counter += 1
        if counter % 500 == 0:
            print(f"Processed {counter} messages successfully...")

if __name__=="__main__":
    raw_producer_loop(consumer,["RawData"])
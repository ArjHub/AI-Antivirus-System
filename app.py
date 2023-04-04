"@author: NavinKumarMNK"
from fastapi import FastAPI, UploadFile, File
import uvicorn
import utils.utils as utils
import json
import os

params = utils.config_parse('PRODUCTION')

"""
@files :
    temp/malware/<uuid>.exe
    temp/cuckoo/<uuid>.json
    temp/img/<uuid>.json
    temp/report/<uuid>.json
    temp/sf/<uuid>.json
"""

if params['production'] == 1:
    try:
        from azure.eventhub import EventHubProducerClient, EventData
    except ImportError as e:
        print(e)
        exit(1)

    CONNECTION_STRING = params['connection_string']
    EVENTHUB_NAME = params['eventhub_name']

    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STRING, eventhub_name=EVENTHUB_NAME)
    
    '''
    @brief : send 3 json files and separate exe file which were not realted
                send malware, json files
                send the batch of events to the event hub.
    '''            
    async def send_to_hub(file_name):
        try:
            with producer_client:
                event_data_batch = producer_client.create_batch()
                if os.path.exists(utils.ROOT_PATH + params['temp_data_path'] + 'malware/and' + file_name):
                    event_data_batch.add(EventData(utils.ROOT_PATH + params['temp_data_path'] + 'malware/win' + file_name))
                if os.path.exists(utils.ROOT_PATH + params['temp_data_path'] + 'malware/win' + file_name):
                    event_data_batch.add(EventData(utils.ROOT_PATH + params['temp_data_path'] + 'malware/win' + file_name))
                if os.path.exists(utils.ROOT_PATH + params['temp_data_path'] + 'json/' + file_name + '.json'):
                    event_data_batch.add(EventData(utils.ROOT_PATH + params['temp_data_path'] + 'json/' + file_name + '.json'))
                if os.path.exists(utils.ROOT_PATH + params['temp_data_path'] + 'img/' + file_name + '_dex.json'):
                    event_data_batch.add(EventData(utils.ROOT_PATH + params['temp_data_path'] + 'image/' + file_name + '_dex.png'))
                if os.path.exists(utils.ROOT_PATH + params['temp_data_path'] + 'img/' + file_name + '_dex.json'):
                    event_data_batch.add(EventData(utils.ROOT_PATH + params['temp_data_path'] + 'image/' + file_name + '_win.png'))
                if os.path.exists(utils.ROOT_PATH + params['temp_data_path'] + 'report/' + file_name + '.json'):
                    event_data_batch.add(EventData(utils.ROOT_PATH + params['temp_data_path'] + 'report/' + file_name + '.json'))
                if os.path.exists(utils.ROOT_PATH + params['temp_data_path'] + 'sf/' + file_name + '.json'):
                    event_data_batch.add(EventData(utils.ROOT_PATH + params['temp_data_path'] + 'sf/' + file_name + '.json'))
                
                producer_client.send_batch(event_data_batch)
                print("A batch of {} events has been published.".format(len(file_name)))
        except Exception as e:
            print(e)

app = FastAPI()

@app.post("/file")
async def file(file: UploadFile = File(...)):
    """
    @brief : 
        input : File, uploaded by user
        output : json file {predictions, optional message}
    @process :
        > create a unique id for the file
        > save the file to temp/malware/<uuid>.exe
        parallel :
            > file2image to MalCoAtNet  
            > file2 cuckoo sandbox & retrieve json 
                > cuckoo.json > api call feature > LSTM
            > file2 lief & retrieve static features json
                > lief.json > LigthGBM
        > make report json
        > send the files, data, json to azure event hub
        > return the results to the user
    """
    
    # malware file to check!
    contents = await file.read()
    uid = utils.random_filename()

    #predictions




    # logic & data sent to respective API
    response = None
    
    if params['production'] == 1:
        await send_to_hub(file.filename)
    
    #send the contents to azure event hub
    if params['production'] == 1:
        await send_to_hub(file.filename)
    

    return {"result" : 1}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
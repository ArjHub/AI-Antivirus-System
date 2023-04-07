"@author: NavinKumarMNK"
from fastapi import FastAPI, UploadFile, File
import uvicorn
import utils.utils as utils
import json
import os
import PIL
import requests

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

async def coatnet_inference(fileno: int, file_path:str):
    if fileno == 1:
        from etl.AndroMal2Img import create_linear_image
    elif fileno == 2:
        from etl.WindMal2Img import create_linear_image
    img_path = create_linear_image(file_path)

    import torchvision.transforms as transforms
    import torch
    transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])    
    x = PIL.Image.open(img_path)
    if params['svm_classifer'] == 1:
        from models.MalCoAtNet.SVM import SVM
        from models.MalCoAtNet.MalCoAtNet import MalCoAtNet
        feature_extractor = MalCoAtNet() 
        feature_extractor.eval()
        with torch.no_grad():    
            x = feature_extractor(x)
            x = transform(x)
            feature = feature_extractor(x)
            classifier = SVM()
            y = classifier.predict(x)
            return y 
    else :
        from models.MalCoAtNet.MalwareClassifer import MalwareClassifer
        model = MalwareClassifer()
        model.eval()
        with torch.no_grad():
            y = model(x)
            return y

async def api_analysis(file_path):
    url = "http://localhost:8000/file"

    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = await requests.post(url, files=files)
        
    if response.status_code == 200:
        print(response.json()["result"])

    else:
        print(f"Error: {response.status_code} ({response.reason})")

async def server_analysis(file_path):
    from etl.remnux.file2log import analyse
    results = analyse()
    return results

async def lgbm_predict(file_path):
    import lightgbm
    from models.LightGBM.lgbm_predict import lgbm_predict
    model = lgbm_predict()
    y = model.predict(file_path)

app = FastAPI()

@app.post("/file")
async def file(file: UploadFile = File(...)):
    """
    @brief : 
        input : File, uploaded by user
        output : json file {predictions, optional message}
    @process :
        > create a unique id for the file
        > save the file to temp/malware/win(or)and/<uuid>.exe
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

    #save the file
    file_path = utils.TEMP_PATH + '/malware'

    if file.filename.split('.')[1] == 'apk':
        from etl.AndroMal2Img import apk2tdex
        file_path += '/and/' + uid + '.apk'
        with open(file_path) as f:
            f.write(contents)
        apk2tdex(file_path[:-4] + '.apk', file_path + '.dvk')
        fileno = 1
    elif file.filename.split('.')[1] == 'dvk':
        file_path += '/and/' + uid + '.dex'
        with open(file_path) as f:
            f.write(contents)
        fileno = 1
    elif file.filename.split('.')[1] == 'win':
        file_path += '/win/' + uid + '.exe'
        with open(file_path) as f:
            f.write(contents)
        fileno = 2
        
    #predictions
    predictions = {}
    if params['coatnet_fe'] == 1:
            x1 = await coatnet_inference(fileno=fileno, file_path=file_path)
    if params['api_analysis'] == 1:
            x2 = await api_analysis(file_path=file_path)
    if params['server_analysis'] == 1
            x3 = await server_analysis(file_path=file_path)
    if params['lgbm_classifer'] == 1:
            x4 = await 

    if params['api_analysis'] == 1:





    # logic & data sent to respective API
    response = None
    
    if params['production'] == 1:
        await send_to_hub(file.filename)
    
    #send the contents to azure event hub
    if params['production'] == 1:
        await send_to_hub(file.filename)
    

    return {"result" : 1}

if __name__ == "__main__":
    import sys
    sys.stdout.write("Initializing...\n")
    import __init__
    __init__.init()
    sys.stdout.write("\033[F") 
    sys.stdout.write("Initialized    \n")
    uvicorn.run(app, host="localhost", port=8000)
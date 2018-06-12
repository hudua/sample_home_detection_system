import json
import time
import requests
import pyodbc
import db_access
from picamera import PiCamera
from os.path import expanduser

#PI ID
floorplanid = 2

with open('settings.json') as f:
    settings = json.load(f)

# Face API request info
face_url = 'https://westus.api.cognitive.microsoft.com/face/v1.0/'
params_detect = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender'
}
header_detect = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': settings['cog_face_key']
}
header_identify = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': settings['cog_face_key']
}

# how long this runs for = approx. how many iterations * 3 seconds
how_many_iterations = 1

if __name__ == "__main__":
    camera = PiCamera()
    camera.rotation = 180
    camera.brightness =  55

    #initial sleep for camera to warm up
    time.sleep(2)

    db = db_access.Db()
    
    for i in range(how_many_iterations):
        camera.capture('images/capture{}.jpg'.format(i))
        img = open(expanduser('images/capture{}.jpg'.format(i)),'rb')

        #######################################
        #send image to Azure Blob storage here#
        #update SQL database with new URL here#
        #######################################

        #db.update_lounge_image(floorplanid,'New URL')

        #refresh lounge person database
        db.refresh_lounge_person(floorplanid)
        
        #face detection
        response = requests.post(
            face_url + 'detect',
            data = img,
            headers = header_detect,
            params = params_detect
        )

        if response.text:
            result = response.json()
        else:
            result = {}
        
        face_ids = [each['faceId'] for each in result]

        # if there are faces detected
        if len(face_ids) > 0:

            #run faces against person group for person identification
            json = {
                'personGroupId': settings['person_group_id'],
                'largePersonGroupId': None,
                'faceIds': face_ids,
                'maxNumofCandidateReturned':1,
                'confidenceThreshold': None
            }
            
            response = requests.post(
                face_url + 'identify',
                json = json,
                headers = header_identify
            )

            if response.text:
                result = response.json()
            else:
                result = {}

            person_ids = [each['candidates'][0]['personId'] for each in result if len(each['candidates']) > 0]

            #if there are people identified, edit names in database
            if len(person_ids) > 0:
                for id in person_ids:
                    response = requests.get(
                        face_url + 'persongroups/{}/persons/{}'.format(settings['person_group_id'],id),
                        headers = header_identify
                    )
                    if response.text:
                        result = response.json()
                    else:
                        result = {}

                    db.insert_lounge_person(floorplanid,result['name'])
                    print('Found ' + result['name'])

    db.cnn.close()
                    

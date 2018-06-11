import json
import yagmail
import time
import requests
from picamera import PiCamera
from os.path import expanduser

with open('settings.json') as f:
    settings = json.load(f)

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

    for i in range(how_many_iterations):
        time.sleep(2)
        camera.capture('images/capture{}.jpg'.format(i))
        
    for i in range(how_many_iterations):
        img = open(expanduser('images/capture{}.jpg'.format(i)),'rb')
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

        print face_ids
        
        if len(face_ids) > 0:
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

            if len(person_ids) > 0:
                yag = yagmail.SMTP(settings['email_user'],settings['email_pw'])
                for id in person_ids:
                    response = requests.get(
                        face_url + 'persongroups/{}/persons/{}'.format(settings['person_group_id'],id),
                        headers = header_detect
                    )
                    if response.text:
                        result = response.json()
                    else:
                        result = {}
                    print 'Found ' + result['name']
		    #contents = ["Found" + result['name'],'images/capture{}.jpg'.format(i)]
                    #yag.send("","Alert!",contents)


                    

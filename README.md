# sample_home_detection_system

Here is how to run this on a new Raspberry Pi:
- In settings.json, change the container accordingly
- In cam_system.py, change the floorplanid accordinly
- In cam_system.py, change number of iterations to be around 100. 100 iterations

100 iterations will take approximately 5 minutes (1 iteration = 1 image + processing time = 3 seconds to run)

The logic is (this is 1 iteration)
- Camera takes an image and saves locally
- Local image is sent to Azure blob storage
- Azure DB [Lounge] table gets updated with blob storage image URL
- DB [LoungePerson] names are refreshed (cleared) because of new image
- Local image is sent to Face API for face detection
- A list of face IDs is generated
- List of face IDs is sent to Face API for identification
- If persons are identified, person IDs are returned
- Person IDs sent to Face API to get person names
- Names are stored into database
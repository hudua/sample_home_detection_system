import pyodbc
import json

with open('settings.json') as f:
    settings = json.load(f)

server = settings['db_server']
db = settings['db']
uid = settings['uid']
pw = settings['pw']
cnn_string = 'DRIVER=FreeTDS;SERVER='+server+';PORT=1433;DATABASE='+db+';UID='+uid+';PWD='+pw+';TDS_Version=8.0;'


class Db:
    def __init__(self):
        self.cnn = pyodbc.connect(cnn_string)
        self.cursor = self.cnn.cursor()

    def update_lounge_image(self, floorplanid, new_value):
        query = "update [Lounge] set recentuploadurl = '{}' where floorplan = {}".format(new_value,floorplanid)
        print(query)
        self.cursor.execute(query)
        self.cnn.commit()

    def refresh_lounge_person(self, floorplanid):
        query = "delete from [LoungePerson] where floorplan = {}".format(floorplanid)
        self.cursor.execute(query)
        self.cnn.commit()

    def insert_lounge_person(self, floorplanid, person_name):
        query = "insert into [LoungePerson] (floorplan, personname) values ({},'{}')".format(floorplanid, person_name)
        self.cursor.execute(query)
        self.cnn.commit()

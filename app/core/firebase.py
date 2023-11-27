import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred , name='firebase' , options={
    'storageBucket': 'flaskapi-e10fe.appspot.com'
})
firebase_app = firebase_admin.get_app(name='firebase')
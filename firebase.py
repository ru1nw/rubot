import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class Firebase:
    cred = credentials.Certificate('./service-account-private-key.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()

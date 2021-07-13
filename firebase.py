import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from constants import Path

class Firebase:
    cred = credentials.Certificate(Path.RUBOT_FIREBASE_CERTIFICATE.value)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

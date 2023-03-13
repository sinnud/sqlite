import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize the Firebase Admin SDK
cred = credentials.Certificate(r'c:\Users\LukeDu\Downloads\sinnud-movies-firebase-adminsdk-6drly-2f1b169c1b.json')
firebase_admin.initialize_app(cred)

from firebase_admin import firestore

firestore_client = firestore.client()

doc_ref = firestore_client.collection('users').document('alice')
doc_ref.set({
    'name': 'Alice',
    'age': 30
})
from firebase import Firebase
from datetime import datetime
from datetime import timedelta
from datetime import timezone

class User_Ratings(Firebase):
    col_ref = Firebase.db.collection(u'rubot-user-ratings')

    @classmethod
    async def rate(cls, receiver, rater, change):
        if await cls.check_time(receiver, rater) != None:
            return -1
        doc_ref = cls.col_ref.document(str(receiver))
        
        doc = doc_ref.get().to_dict()
        if doc["rating"] == 5:
            return 6
        elif doc["rating"] == 1:
            return 0
        rating = ((doc["rating"] * doc["number-of-ratings"] + change)
                  / (doc["number-of-ratings"] + 1))
        
        doc_ref.set({
            u'number-of-ratings': (doc[u"number-of-ratings"] + 1),
            u'raters-history': {str(rater): datetime.now(timezone.utc)},
            u'rating': rating
        }, merge=True)

        return rating

    @classmethod
    async def check_user(cls, uid):
        doc = cls.col_ref.document(str(uid)).get().to_dict()
        return False if (doc == None) else True

    @classmethod
    async def init(cls, uid):
        doc_ref = cls.col_ref.document(str(uid))
        doc_ref.set({
            u'number-of-ratings': 1,
            u'raters-history': {"creation": datetime.now(timezone.utc)},
            u'rating': 3.8
        })

    @classmethod
    async def check_time(cls, receiver, rater):
        doc_ref = cls.col_ref.document(str(receiver))
        raters = doc_ref.get().to_dict()["raters-history"]
        try:
            time = raters[str(rater)]
        except KeyError:
            doc_ref.set({
                u'raters-history': {str(rater): datetime.min}
            }, merge=True)
            return None
        else:
            if time < (datetime.now(timezone.utc) - timedelta(minutes=30)):
                return None
            return time - (datetime.now(timezone.utc) - timedelta(minutes=30))

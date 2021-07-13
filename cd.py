from firebase import Firebase
from datetime import datetime
from datetime import timedelta
from datetime import timezone

class CD(Firebase):
    doc_ref = Firebase.db.collection(u'rubot').document(u'cd')

    @classmethod
    async def get_special(cls):
        return cls.doc_ref.get().to_dict()[u'special-msg-count']

    @classmethod
    async def get_exceptions(cls):
        return cls.doc_ref.get().to_dict()[u'exceptions']

    @classmethod
    async def get_special_counter(cls):
        return cls.doc_ref.get().to_dict()[u'special-counter']

    @classmethod
    async def set_special(
            cls, *, msg_count = doc_ref.get().to_dict()[u'special-msg-count']):
        cls.doc_ref.set({
            u'special-msg-count': msg_count
        }, merge=True)

    @classmethod
    async def set_exceptions(cls, cid):
        arr = cls.doc_ref.get().to_dict()[u'exceptions']
        cls.doc_ref.set({
            u'exceptions': arr + [cid]
        }, merge=True)

    @classmethod
    async def reset_special_counter(cls):
        cls.doc_ref.set({
            u'special-counter': 0
        }, merge=True)

    @classmethod
    async def add_special_counter(cls):
        c = cls.doc_ref.get().to_dict()[u'special-counter'] + 1
        cls.doc_ref.set({
            u'special-counter': c
        }, merge=True)

    @classmethod
    async def add_counter(cls, special):
        if special:
            await cls.add_special_counter()
        else:
            await cls.add_normal_counter()



    # below are only kept as backup in case i wanna come back and finish the entire thing originally planned

    '''@classmethod
    async def get_normal(cls):
        return cls.doc_ref.get().to_dict()[u'normal-msg-count']

    @classmethod
    async def get_normal_counter(cls):
        return cls.doc_ref.get().to_dict()[u'normal-counter']

    @classmethod
    async def set_normal(
            cls, *, msg_count = doc_ref.get().to_dict()[u'normal-msg-count']):
        cls.doc_ref.set({
            u'normal-msg-count': msg_count
        }, merge=True)

    @classmethod
    async def reset_normal_counter(cls):
        cls.doc_ref.set({
            u'normal-counter': 0
        }, merge=True)'''

    @classmethod
    async def add_normal_counter(cls):
        pass
        '''c = cls.doc_ref.get().to_dict()[u'normal-counter'] + 1
        cls.doc_ref.set({
            u'normal-counter': c
        }, merge=True)'''

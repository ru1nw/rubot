from firebase import Firebase

class Rarity(Firebase):
    doc_ref = Firebase.db.collection(u'rubot').document(u'rarity')

    @classmethod
    async def get(cls, gid):
        return cls.doc_ref.get().to_dict()[str(gid)]

    @classmethod
    async def set(cls, gid, percent):
        cls.doc_ref.set({
            str(gid): int(percent)
        }, merge=True)

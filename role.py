from firebase import Firebase

class Role(Firebase):
    col_ref = Firebase.db.collection(u'rubot')
    doc_ref = col_ref.document(u'react-role')

    @classmethod
    async def add_role(cls, emoji, rid, gid):
        cls.doc_ref.set({
            str(gid): {
                u"role": {
                    str(emoji): str(rid)
                }
            }
        }, merge=True)

    @classmethod
    async def add_msg(cls, gid, mid):
        doc = cls.doc_ref.get().to_dict()
        try:
            msgs = doc[str(gid)][u"message"]
        except KeyError:
            msgs = []
            
        cls.doc_ref.set({
            str(gid): {
                u"message": msgs + [str(mid)]
            }
        }, merge=True)

    @classmethod
    async def get_role(cls, gid, emoji):
        return cls.doc_ref.get().to_dict()[str(gid)][u"role"][str(emoji)]

    @classmethod
    async def get_msg(cls, gid):
        try:
            guild = cls.doc_ref.get().to_dict()[str(gid)]
        except KeyError:
            return []
        else:
            return guild[u"message"]

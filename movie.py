from firebase import Firebase
import requests
from bs4 import BeautifulSoup
from string import ascii_letters, digits

class movie(Firebase):
    col_ref = Firebase.db.collection(u'rubot')
    doc_ref = col_ref.document(u'movie-list')
    alnum = ascii_letters + digits + " "

    @classmethod
    async def list(cls, gid):
        return cls.doc_ref.get().to_dict().get(str(gid))

    @classmethod
    async def add(cls, gid, name, url=''):
        if not name.replace(" ", "").isalnum():
            return "[ERR] no non-alphanumericals for name"
        '''for c in name:
            if c not in cls.alnum:
                return "[ERR] no non-alphanumericals for name"'''
        if not url.isascii():
            return "[ERR] no non-ascii for url"
        
        info = {"date": None, "length": None}
        try:
            source_code = requests.get(url).text

            soup = BeautifulSoup(source_code, 'html.parser')

            table = soup.find('table', class_='infobox vevent')
            for tr in table.find_all('tr'):
                for t in tr.find_all('th'):
                    if (t.div != None) and (t.string == "Release date"):
                        try:
                            info["date"] = tr.td.div.ul.next_element.span.span.string
                        except AttributeError:
                            info["date"] = None
                    elif (t.div != None) and (t.string == "Running time"):
                        try:
                            info["length"] = tr.td.next_element
                        except AttributeError:
                            info["length"] = None
        except:
            info = {"date": None, "length": None}

        doc = cls.doc_ref.get().to_dict().get(str(gid), [])
        for l in doc:
            if l[u"name"].lower() == name.lower() and (not l[u"watched"]):
                return (f"[ERR] movie {l[u'name']} already in list! " +
                        "mark it as watched to add it again!")
        doc += [{
            u'name': name,
            u'watched': False,
            u'date': info["date"],
            u'length': info["length"]
        }]
        doc = sorted(
            doc, key=lambda d:(d['watched'], d['name'].lower()))
            
        cls.doc_ref.set({
            str(gid): doc
        }, merge=True)
        return f"[INFO] added movie {name}!"

    @classmethod
    async def watched(cls, gid, name):
        count = 0
        doc = cls.doc_ref.get().to_dict().get(str(gid))
        for d in doc:
            if (d[u'name'].lower().startswith(name.lower())
                and not d[u'watched']):
                if d[u'name'].lower() == name.lower():
                    break
                else:
                    count += 1
        if count > 1:
            return ("[ERR] there are mulitple movies in the list "
                    + f"that start with {name}!")
        for d in doc:
            if (d[u'name'].lower().startswith(name.lower())
                and not d[u'watched']):
                d[u'watched'] = True
                doc = sorted(
                    doc,
                    key=lambda d:(d['watched'], d['name'].lower()))
                cls.doc_ref.set({
                    str(gid): doc
                }, merge=True)
                return f"[INFO] you just watched {d[u'name']}!"
        return f"[ERR] {name} isn't in the list!"

class EMP(object):
    def __init__(self, id="", name="", dept="", image_id=""):
        self.id = id
        self.name = name
        self.dept = dept
        self.image_id = image_id


class DEPT(object):
    def __init__(self, id="", name=""):
        self.id = id
        self.name = name


class EMP_ALL(object):
    def __init__(self, id=0, name="", age=0, sex="", image_id="", post="", pref="", address="", dept="", join="", retire="", image=""):
        self.id = id
        self.name = name
        self.age = age
        self.sex = sex
        self.image_id = image_id
        self.post = post
        self.pref = pref
        self.addrss = address
        self.dept = dept
        self.join = join
        self.retire = retire
        self.image = image





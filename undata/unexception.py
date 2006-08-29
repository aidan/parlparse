

class unexception(Exception):

    def __init__(self, description, paranum):
        self.description = description
        self.paranum = lparanum

    def __str__(self):
        ret = ""
        if self.fragment:
            ret = ret + "Fragment: " + self.paranum + "\n\n"
        ret = ret + self.description + "\n"
        return ret


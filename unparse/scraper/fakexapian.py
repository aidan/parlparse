
DB_CREATE_OR_OPEN = "DB_CREATE_OR_OPEN"

class WritableDatabase:
    def __init__(self, xapian_file, xstr):
        pass

    def add_document(self, doc):
        #print "\n"
        p = doc.__str__()
        if p:
            print p

    def flush(self):
        pass

class Enquire:
    def __init__(self, xapian_db):
        pass
    def set_query(self, parsedquery):
        pass
    def set_weighting_scheme(self, x):
        pass
    def get_mset(self, a, b, c):
        return []

class BoolWeight:
    pass

class Query:
    OP_AND = "OP_AND"

class ParsedQuery:
    def __init__(self, lquery):
        self.parsedquery = "Parsed:%s" % lquery
    def get_description(self):
        return self.parsedquery

class QueryParser:
    STEM_NONE = "STEM_NONE"
    def __init__(self):
        pass
    def set_stemming_strategy(self, x):
        pass
    def set_default_op(self, x):
        pass
    def add_boolean_prefix(self, x1, x2):
        pass
    def parse_query(self, query):
        return ParsedQuery(query)

class Document:
    def __init__(self):
        self.values = []
        self.terms = []
        self.postings = []
        self.data = ""

    def add_value(self, i, value0):
        assert i == len(self.values)
        self.values.append(value0)

    def add_term(self, term):
        self.terms.append(term)

    def add_posting(self, s, ip):
        self.postings.append((ip, s))

    def set_data(self, dsubheadingdata):
        self.data = dsubheadingdata

    def __str__(self):
        res = [ self.data ]
        for i in range(len(self.values)):
            res.append("v%d=%s" % (i, self.values[i]))

        res.extend(self.terms)

        if self.postings:
            pres = [ ]
            j = 0
            for i in range(self.postings[-1][0] + 1):
                if self.postings[j][0] == i:
                    pres.append(self.postings[j][1])
                    j += 1
                else:
                    pres.append("")
            assert j == len(self.postings)
            res.append(".".join(pres))

        res = [] #[s for s in res if s[0] == "R"]
        return " ".join(res)



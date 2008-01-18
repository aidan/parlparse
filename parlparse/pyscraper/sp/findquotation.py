#!/usr/bin/python2.4

import xml.sax
import re
import os

class ScrapedXMLParser(xml.sax.handler.ContentHandler):

    def __init__(self):
        self.parser = xml.sax.make_parser()
        self.parser.setContentHandler(self)

    def find_id_for_quotation(self,date_string,regexp_list):
        self.ids_with_quote = { }
        self.regexp_list = regexp_list
        # Look both in written answers and official reports...
        files_to_look_in = [ "../../../parldata/scrapedxml/sp/sp%s.xml" % date_string,
                             "../../../parldata/scrapedxml/sp-written/spwa%s.xml" % date_string ]
        for filename in files_to_look_in:
            if os.path.exists(filename):
                self.parser.parse(filename)
        # Find the ID that most of the regexps match:
        max_occurences = 0
        id_to_return = None
        for k in self.ids_with_quote:
            occurences = self.ids_with_quote[k]
            if occurences > max_occurences:
                id_to_return = k
                max_occurences = occurences
        return id_to_return
            
    def startElement(self,name,attr):
        if name == "ques" or name == "repl" or name == "speech":
            self.element_id = attr["id"]

    def characters(self,c):
        for r in self.regexp_list:
            if re.search(r,c):                
                self.ids_with_quote.setdefault(self.element_id,0)
                self.ids_with_quote[self.element_id] += 1

# sxp = ScrapedXMLParser()
# sxp.find_id_for_quotation( "2004-02-25", [ re.compile("given that justice must be not only swift"),
#                                            re.compile("He also said that justice must") ] )

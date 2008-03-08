#!/usr/bin/python2.4

import xml.sax
import re
import os

def find_quotation_from_text(sxp,date,text,minimum_substring_length=20):
    substrings = re.split('\s*[,\.\[\]:]+\s*',text)
    long_enough_substrings = filter( lambda e: len(e) > minimum_substring_length, substrings )
    regular_expressions = map( lambda e: re.compile(re.escape(e)), long_enough_substrings )
    return sxp.find_id_for_quotation( str(date), regular_expressions )

def find_speech_with_trailing_spid(sxp,date,spid):
    return sxp.find_id_for_quotation( str(date), [ re.compile('\(\s*'+spid+'\s*\)\s*$') ] )

class ScrapedXMLParser(xml.sax.handler.ContentHandler):

    def __init__(self,file_template=None):
        self.parser = xml.sax.make_parser()
        self.parser.setContentHandler(self)
        if not file_template:
            self.file_templates = [ "../../../parldata/scrapedxml/sp/sp%s.xml",
                                    "../../../parldata/scrapedxml/sp-written/spwa%s.xml",
                                    "../../../parldata/scrapedxml/debates/debates%s.xml" ]
        elif (file_template.__class__ == str) or (file_template.__class__ == unicode):
            self.file_templates = [ file_template ]
        elif (file_template.__class__ == list):
            self.file_templates = file_template
        else:
            raise Exception, "Unknown type of parameter ("+str(file_template.__class__)+") passed to ScrapedXMLParser"

    def find_id_for_quotation(self,date_string,regexp_list):
        self.ids_with_quote = { }
        self.regexp_list = regexp_list
        # Look both in written answers and official reports...
        files_to_look_in = map( lambda t: t % date_string, self.file_templates )
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

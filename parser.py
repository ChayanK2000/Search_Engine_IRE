# from asyncio import subprocess
# import subprocess

import os
import xml.sax
import time
from nltk.corpus import stopwords
import Stemmer

class TextCleaning():
    # def __init__(self):



    def preprocess(self,text):
        '''
        1. check for ref links separately
        2. remove everything inside braces
        2. for extra step: dont rmeove all inside braces. split by '|' and keep th elasst element
        2. remove all non alphanumeric char  
        3. stopwords removal
        4. stemming

        5. dates
        6. {{....}} or [[....]] inside this not necessary except last on splitting with '|'
        '''
        stop_words = set(stopwords.words('english'))
        preprocessed_text = ''.join(ch if ch.isalnum() else ' ' for ch in text)
        preprocessed_text = preprocessed_text.split()
        preprocessed_text = [w for w in preprocessed_text if w not in stop_words]
        stemmer = Stemmer.Stemmer('english')
        preprocessed_text = stemmer.stemWords(preprocessed_text)

        return preprocessed_text




class AllTextHandler():
    # def __init__():


    def __init__(self):
        '''
        0 - not started
        1 - done
        '''
        self.flag_infobox = 0
        self.flag_title = 0
        self.flag_body = 0
        self.flag_references = 0
        self.flag_links = 0
        self.flag_category = 0
        self.flag = None
        self.obj_text = TextCleaning()

    def text_body_handler(self,text):
        #text here is an array st that each element is a line form xml file as extracted from sax
        infobox_text = ""
        body_text = ""
        ref_text = ""
        link_text = ""
        cat_text = ""
        for line in text:
            # if self.flag_infobox == 0:
            # things to try: 'in', startswith, slicing
            # to handle cases like "== references ==" , "== external links ==" etc
            # and things like removing {{Infobox....}}, [category...] etc
            if "{{Infobox" in line:
                # self.init_cases_flag()
                self.flag_infobox = 1
                self.flag = "infobox"
            
            if("==References==" in line):
                self.flag_references = 1
                self.flag = "ref"

            if("==External Links==" in line):
                self.flag_links = 1
                self.flag = "links"


            if("[[Category" in line):
                self.flag_category = 1
                self.flag = "cat"

            if(self.flag == "infobox"):
                infobox_text = infobox_text + line
                if(line == "}}"):
                    self.flag_infobox = 1
                    # self.flag = None
                    # self.flag_body = 1
                    self.flag = "body"
                    continue

            if(self.flag == "body"):
                body_text = body_text + line
            
            if(self.flag == "ref"):
                ref_text = ref_text + line
            
            if(self.flag == "links"):
                link_text = link_text + line

            if(self.flag == "cat"):
                cat_text = cat_text + line

                    


        infobox_text = self.obj_text.preprocess(infobox_text.lower())
        body_text = self.obj_text.preprocess(body_text.lower())
        cat_text = self.obj_text.preprocess(cat_text.lower())
        # ref_text = self.obj_text.preprocess(ref_text)
        # link_text = self.obj_text.preprocess(link_text)
        # infobox_text = self.obj_text.preprocess(infobox_text)

            
        return infobox_text,body_text,cat_text,ref_text,link_text   




        
    



class ArticleHandler(xml.sax.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        # xml.sax.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []
        self.doc_count = 0
        self.obj_for_fields = AllTextHandler()
        

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if (name == "page"):
            self.title = self.infobox = self.body = self.category = self.references = self.links = ""

            
        if name in ('title', 'text'):
            self._current_tag = name
            self._buffer = []
            self.obj_for_fields.__init__()


    def endElement(self, name):
        """Closing tag of element"""
        # if name == self._current_tag:
        #     self._values[name] = ''.join(self._buffer)
        if name == 'title':
            self.title = ''.join(self._buffer)


        if name == "text":

            self.infobox,self.body,self.category,self.references,self.links = self.obj_for_fields.text_body_handler(self._buffer)
            
            # print(infobox)
        

        if name == 'page':
            self.doc_count += 1
            print(f"-- Document {self.doc_count} done--")
            print("Title: ",self.title)
            print("Infobox:",self.infobox)
            print("Body: ",self.body)
            print("Category: ",self.category)
            print("Ref:",self.references)
            print("Links:",self.links)





            
            






# if __name__ == "__main__":

start = time.time()
handler = ArticleHandler()
parser = xml.sax.make_parser()
parser.setContentHandler(handler)
# for line in subprocess.Popen(['bzcat'], stdin = open('sample.xml'), stdout = subprocess.PIPE).stdout:
#     parser.feed(line)
parser.parse(open('sample','r'))
sample_file_stats = os.stat('sample')
data_size = 1456153957
end = time.time()
with open('time_taken.txt','w') as time_file:
    time_file.write(f"Documents: {handler.doc_count}\n")
    time_file.write(f"Size: {sample_file_stats.st_size} Bytes\n")
    time_file.write(f"Time taken: {end-start} seconds\n")
    time_file.write("Estimated time for whole document: "+str((data_size/sample_file_stats.st_size)*(end-start)))


        




  
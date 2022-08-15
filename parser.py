# from asyncio import subprocess
# import subprocess

from collections import defaultdict
import os
import sys
import xml.sax
import time
from nltk.corpus import stopwords
import Stemmer
from nltk.stem.snowball import SnowballStemmer
from tqdm import tqdm
import copy

# doc_count = 0
final_index = defaultdict(str) # to escape key error in line 107
file_number = 1


class Index():
    def __init__(self):
        # defaultdcit instead of {} to automatically handle missing keys for code in lines 73 onwards
        self.title_dict = defaultdict(int)
        self.infobox_dict = defaultdict(int)
        self.body_dict = defaultdict(int)
        self.references_dict = defaultdict(int)
        self.category_dict = defaultdict(int)
        self.link_dict = defaultdict(int)

        # self.final_index = {}
        self.vocab = set()

    def create_field_index(self, words_as_list, identity):
        '''
        * following SPIMI algo
        https://www.youtube.com/watch?v=uXq4aq51eKE


        '''
        # global doc_count

        # dict are copied by address hence changes are refelcted across. but then both affect each other. hence deepcopy could be used but fir using that is basically iterating through the whole dict.

        self.index_dict = defaultdict(int)
        self.vocab.update(words_as_list)
        for word in words_as_list:
            if word not in self.index_dict:
                self.index_dict[word] = 1
            else:
                self.index_dict[word] += 1

        if identity == "t":
            self.title_dict = copy.deepcopy(self.index_dict)

        elif identity == "i":
            self.infobox_dict = copy.deepcopy(self.index_dict)

        elif identity == "b":
            self.body_dict = copy.deepcopy(self.index_dict)

        elif identity == "r":
            self.references_dict = copy.deepcopy(self.index_dict)

        elif identity == "c":
            self.category_dict = copy.deepcopy(self.index_dict)

        elif identity == "l":
            self.link_dict = copy.deepcopy(self.index_dict)

        # print("title:")
        # for i, j in self.title_dict.items():
        #     print(i, j)
        # print("info:")

        # for i, j in self.infobox_dict.items():
        #     print(i, j)
        # print("body:")

        # for i, j in self.body_dict.items():
        #     print(i, j)

        # for i,j in self.title_dict.items():
        #     print(i,j)

    def create_final_index(self):
        global doc_count
        global final_index
        global file_number

        for word in self.vocab:
            posting_data = str(doc_count)+":"

            if self.title_dict[word]:
                posting_data += 't'+str(self.title_dict[word])

            if self.infobox_dict[word]:
                posting_data += 'i'+str(self.infobox_dict[word])

            if self.body_dict[word]:
                posting_data += 'b'+str(self.body_dict[word])

            if self.category_dict[word]:
                posting_data += 'c'+str(self.category_dict[word])

            if self.references_dict[word]:
                posting_data += 'r'+str(self.references_dict[word])

            if self.link_dict[word]:
                posting_data += 'l'+str(self.link_dict[word])

            posting_data += ';'

            final_index[word] += posting_data

        if doc_count % 30000 == 0:
            temp_index_map = sorted(final_index.items())
            temp_index = []
            for word, posting in tqdm(temp_index_map):
                temp_index.append(word+'-'+posting)

            with open(f'./output/index_postings_{file_number}.txt', 'w') as f:
                f.write('\n'.join(temp_index))

            file_number += 1
            final_index = defaultdict(str)


class TextCleaning():
    # def __init__(self):

    global stemmer
    stemmer = Stemmer.Stemmer('english')
    # stemmer = SnowballStemmer(language='english')
    global stop_words
    stop_words = set(stopwords.words('english'))

    def preprocess(self, text):
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

        # preprocessed_text = preprocessed_text.split()
        str = ""
        final_text = []

        global stemmer
        global stop_words
        for ch in text:
            if ch.isalpha():
                str += ch
            else:
                if ((str not in stop_words) and (str != "")):
                    final_text.append(str)
                str = ""

        # following if to handle case where last word is legit but was not added in loop
        if ((str not in stop_words) and (str != "")):
            final_text.append(str)

        final_text = stemmer.stemWords(final_text)

        return final_text


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

    def text_body_handler(self, title, text):
        # text here is an array st that each element is a line form xml file as extracted from sax
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

        title_text = self.obj_text.preprocess(title.lower())
        infobox_text = self.obj_text.preprocess(infobox_text.lower())
        body_text = self.obj_text.preprocess(body_text.lower())
        cat_text = self.obj_text.preprocess(cat_text.lower())
        # ref_text = self.obj_text.preprocess(ref_text)
        # link_text = self.obj_text.preprocess(link_text)
        # infobox_text = self.obj_text.preprocess(infobox_text)

        return title_text, infobox_text, body_text, cat_text, ref_text, link_text


class ArticleHandler(xml.sax.ContentHandler):
    """Content handler for Wiki XML data using SAX"""

    def __init__(self):
        # xml.sax.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []
        global doc_count
        doc_count = 0
        self.obj_for_fields = AllTextHandler()
        self.obj_for_index = Index()

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        global doc_count
        """Opening tag of element"""
        if (name == "page"):
            self.title = self.infobox = self.body = self.category = self.references = self.links = ""

            doc_count += 1

        if name in ('title', 'text'):
            self._current_tag = name
            self._buffer = []
            self.obj_for_fields.__init__()

    def endElement(self, name):
        global doc_count
        """Closing tag of element"""
        # if name == self._current_tag:
        #     self._values[name] = ''.join(self._buffer)
        if name == 'title':
            self.title = ''.join(self._buffer)

        if name == "text":

            self.title, self.infobox, self.body, self.category, self.references, self.links = self.obj_for_fields.text_body_handler(
                self.title, self._buffer)
            self.obj_for_index.__init__()
            self.obj_for_index.create_field_index(self.title, 't')
            self.obj_for_index.create_field_index(self.infobox, 'i')
            self.obj_for_index.create_field_index(self.body, 'b')
            self.obj_for_index.create_field_index(self.category, 'c')
            self.obj_for_index.create_field_index(self.references, 'r')
            self.obj_for_index.create_field_index(self.links, 'l')

            self.obj_for_index.create_final_index()

            # print(infobox)

        if name == 'page':
            print(f"-- Document {doc_count} done--")
            # print("Title: ",self.title)
            # print("Infobox:",self.infobox)
            # print("Body: ",self.body)
            # print("Category: ",self.category)
            # print("Ref:",self.references)
            # print("Links:",self.links)
            # self.obj_for_index.create_index()


# if __name__ == "__main__":
start = time.time()
handler = ArticleHandler()
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

sample_file = sys.argv[1]
# data_file = sys.argv[2]
# for line in subprocess.Popen(['bzcat'], stdin = open('sample.xml'), stdout = subprocess.PIPE).stdout:
#     parser.feed(line)
parser.parse(open(sample_file, 'r'))
sample_file_stats = os.stat(sample_file)
data_size = 1456153957
end = time.time()
with open('time_taken.txt', 'w') as time_file:
    time_file.write(f"Documents: {doc_count}\n")
    time_file.write(f"Size: {sample_file_stats.st_size} Bytes\n")
    time_file.write(f"Time taken: {end-start} seconds\n")
    time_file.write("Estimated time for whole document: " +
                    str((data_size/sample_file_stats.st_size)*(end-start)))

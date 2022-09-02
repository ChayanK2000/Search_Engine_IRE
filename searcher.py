
# from parser import *
import linecache
import math
from collections import Counter
import time
import sys

from parser import TextCleaning
import parser


class FileHandler():
    def __init__(self):
        pass


    def binary_search_in_secondary_file(self,word):   
        low = 0
        with open('./output_final/total_index_pages.txt','r') as f_n:
            high = int(f_n.readline().strip())-1
        
        while low <= high:
            
            mid = (low + high)//2
            line = linecache.getline('./output_final/secondary.txt', mid+1) # getline has 1 based indexing so +1
            word_in_sec_index = line.split()[0]

            if word < word_in_sec_index:
                high = mid-1

            else:
                low = mid+1
                final_line = mid

        # print("look in this .txt",final_line)

        return final_line



    def binary_search_in_merged_indexes(self,word,suffix_of_index_to_look_in):
        low = 0
        with open('./output_final/total_index_pages.txt','r') as f_n:
            pages_and_words_info = f_n.readlines()
        last_file_suffix = int(pages_and_words_info[0])-1

        if(suffix_of_index_to_look_in == last_file_suffix):
            # with open('./output_final/total_index_pages.txt','r') as f_n:
            final_unique_words = int(pages_and_words_info[1])
            high = final_unique_words % 50000 - 1
            print("high is: ",high)
        else:
            high = 50000 - 1

        while(low<=high):
            mid = (low + high)//2
            line = linecache.getline(f'./output_final/index_postings_{suffix_of_index_to_look_in}.txt', mid+1) # getline has 1 based indexing so +1
            word_in_merged_ind,postings = line.split('-')

            if word < word_in_merged_ind:
                high = mid-1

            else:
                low = mid+1
                final_line = mid
                final_postings = postings
        
        print(final_postings)


        


class InputQuery():
    def __init__(self, obj_preprocess,obj_file):
        self.obj_preprocess = obj_preprocess
        self.obj_file = obj_file
        # pass



    def search_for_general_query(self,query):
        preprocessed_query = self.obj_preprocess.preprocess(query)
		# page_freq, page_postings = {}, defaultdict(dict)

        for word in preprocessed_query:
            # print("entered")
            suffix_of_index_to_look_in = self.obj_file.binary_search_in_secondary_file(word)
            self.obj_file.binary_search_in_merged_indexes(word,suffix_of_index_to_look_in)





    def type_of_query(self,query_per_line):
        
        fields_tags_list = ["t:","b:","i:","c:","r:","l:"]
        field_flag = 0
        for tag in fields_tags_list:
            if(tag in query_per_line):
                field_flag = 1
                query_per_line = query_per_line.replace(tag,"*#"+tag)
                # print(query_per_line)
        if(field_flag == 0): #when no field query present
            self.search_for_general_query(query_per_line)
            # print("1")
            # print(query_per_line)

        # else:
        #     queries = query_per_line.split("*#")
        #     if(query_per_line[0:2] == "*#"): # if query starts with field query then no generla query present
        #         search_for_field(queries[1:])
        #         # print("3")
        #         # print(queries[1:])


        #     else: #when query started with general query but also has field queries later on
        #         search_for_both(queries[0],queries[1:]) 
        #         # print("2")
        #         # print(queries[0],queries[1:])



if __name__ == "__main__":
    whole_search_start_time = time.time()
    # print(parser.final_file_number)
    obj_preprocess = TextCleaning()
    obj_file = FileHandler()
    obj_query = InputQuery(obj_preprocess,obj_file)

    queries_file = sys.argv[1]
    with open (queries_file,'r') as f_q:
        while(1):
            query_per_line = f_q.readline().strip("\n")
            if not query_per_line:
                break
            obj_query.type_of_query(query_per_line)
            print("------------")

    




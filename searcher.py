
import linecache
import math
from collections import defaultdict
import time
import sys

from parser import TextCleaning
from typing_extensions import final


class FileHandler():
    def __init__(self,misc_info):
        self.last_file_suffix = int(misc_info[0])-1
        self.N_total_doc = int(misc_info[2])
        self.final_unique_words = int(misc_info[1])
        self.no_of_words_in_final_index_files = int(misc_info[4])
        self.no_of_titles_in_id_title_txt = int(misc_info[5])
        


    def binary_search_in_secondary_file(self,word):   
        low = 0
        # with open('./output_final/total_index_pages.txt','r') as f_n:
        #     high = int(f_n.readline().strip())-1
        high = self.last_file_suffix - 1
        # print(high)
        
        while low <= high:
            
            mid = (low + high)//2
            line = linecache.getline('./output_final/secondary.txt', mid+1) # getline has 1 based indexing so +1
            word_in_sec_index = line.split()[0]

            if word < word_in_sec_index:
                high = mid-1

            else:
                low = mid+1
                final_line = mid

        # print(f"look in this ....{final_line}.txt")

        return final_line



    def binary_search_in_merged_indexes(self,word,suffix_of_index_to_look_in):
        low = 0
        # with open('./output_final/total_index_pages.txt','r') as f_n:
        #     pages_and_words_info = [temp.strip("\n") for temp in f_n.readlines()]
        # last_file_suffix = int(pages_and_words_info[0])-1
        # N_total_doc = int(pages_and_words_info[2])
        # final_unique_words = int(pages_and_words_info[1])


        if(suffix_of_index_to_look_in == self.last_file_suffix):
            # with open('./output_final/total_index_pages.txt','r') as f_n:
            # final_unique_words = int(pages_and_words_info[1])
            high = self.final_unique_words % self.no_of_words_in_final_index_files - 1
            # print("high is: ",high)
        else:
            high = self.no_of_words_in_final_index_files - 1

        while(low<=high):
            mid = (low + high)//2
            line = linecache.getline(f'./output_final/index_postings_{suffix_of_index_to_look_in}.txt', mid+1) # getline has 1 based indexing so +1
            word_in_merged_ind,postings = line.split('-')

            if word < word_in_merged_ind:
                high = mid-1

            else:
                low = mid+1
                final_line = mid
                final_postings = postings.strip("\n")
        
        # print(final_postings)

        return final_postings



    def binary_search_for_title(self,doc_id):
        # No secondary index needed for title.
        # print("id is: ", doc_id)
        suffix_of_title_to_look_in = math.ceil(int(doc_id)/self.no_of_titles_in_id_title_txt)-1 # by this we can directly get title suffix.txt without secondary index for title
        # print(suffix_of_title_to_look_in)


        # with open(f"./output_final/id_title_{suffix_of_title_to_look_in}.txt") as f_id_t:
        low=1
        if(suffix_of_title_to_look_in == math.ceil(self.N_total_doc/self.no_of_titles_in_id_title_txt)-1):
            high = self.N_total_doc%self.no_of_titles_in_id_title_txt
        else:
            high = self.no_of_titles_in_id_title_txt

        while(low<=high):
            mid = (low + high)//2
            line = linecache.getline(f'./output_final/id_title_{suffix_of_title_to_look_in}.txt', mid) # getline has 1 based indexing so +1
            # print(low,mid,high,line)
            curr_id = line.split(':')[0]

            if int(doc_id) < int(curr_id):
                high = mid-1

            else:
                low = mid+1
                # final_line = mid
                final_title = line
            
        # print(final_title)
        return final_title

class Ranking():
    def __init__(self,misc_info):
        # self.last_file_suffix = last_file_suffix
        self.N_total_doc = int(misc_info[2])

        # self.final_unique_words = final_unique_words


    
    def tf_idf_rank(self,final_postings,final_result,field):


        
        final_postings = final_postings.split(';')[:-1]
        # print("final_postings are: ",final_postings)

        n_no_of_doc_in_which_a_word_appears = len(final_postings)
        # final_result = defaultdict(float)

        weights = {'t':1,'i':0.5,'b':0.05,'r':0.25,'l':0.25,'c':0.3}

        for i in final_postings:
            doc_id,postings_each_doc = i.split(':')
            val_of_each_tag = ""
            total_freq = 0
            for j in postings_each_doc:
                
                ascii_val = ord(j)
                
                
                if(48<= ascii_val <=57) and ((last_field == field)or(field is None)):
                    val_of_each_tag += j
                else:
                    if(val_of_each_tag != ""):
                    # last_field = j
                        # continue
                        total_freq += (weights[last_field]*int(val_of_each_tag)) #giving weightage to freqeuncey for diff fields
                        val_of_each_tag =""
                    
                    last_field = j
            
            # hte followingl three/four lines just like in various ither parts of code, to take into account the last number/items and add it to freq, which would be missed in for loop
            if(val_of_each_tag != ""):
                total_freq += (weights[last_field]*int(val_of_each_tag)) #giving weightage to freqeuncey for diff fields
                val_of_each_tag =""

            tf = math.log(1+total_freq)
            idf = math.log(self.N_total_doc/(1+n_no_of_doc_in_which_a_word_appears)) #adding 1 to handle case if no doc is there having that word
            final_result[doc_id] += (tf*idf)


        return final_result




        


class InputQuery():
    def __init__(self, obj_preprocess,obj_file,obj_ranking):
        self.obj_preprocess = obj_preprocess
        self.obj_file = obj_file
        self.obj_ranking = obj_ranking
        # pass



    def search_for_general_query(self,query,final_result):
        query = query.lower()
        preprocessed_query = self.obj_preprocess.preprocess(query)
		# page_freq, page_postings = {}, defaultdict(dict)
        # final_result = defaultdict(float)


        for word in preprocessed_query:
            # print("entered")
            suffix_of_index_to_look_in = self.obj_file.binary_search_in_secondary_file(word)
            final_postings = self.obj_file.binary_search_in_merged_indexes(word,suffix_of_index_to_look_in)
            final_result = self.obj_ranking.tf_idf_rank(final_postings,final_result,None)

        #     final_results_sorted = sorted(final_results_after_tf_idf.items(), key = lambda item : item[1], reverse=True)
        #     final_results_sorted = final_results_sorted[:10]
        #     # print("sorted list is:" )
        #     # print(final_results_sorted)
        # print("--------------")
        # # final_title_list = []
        # for id,value_for_that_id in final_results_sorted:
        #     final_title_list.append(self.obj_file.binary_search_for_title(id))
        

        # print(final_title_list)
        return final_result




    def search_for_field(self,list_of_field_queries,final_result):
        # final_result = defaultdict(float)
        
        for query in list_of_field_queries:
            field = query[0]
            query = query.lower()
            preprocessed_query = self.obj_preprocess.preprocess(query[2:])
            for word in preprocessed_query:
                suffix_of_index_to_look_in = self.obj_file.binary_search_in_secondary_file(word)
                final_postings = self.obj_file.binary_search_in_merged_indexes(word,suffix_of_index_to_look_in)
                final_result = self.obj_ranking.tf_idf_rank(final_postings,final_result,field)
        #         final_results_sorted = sorted(final_results_after_tf_idf.items(), key = lambda item : item[1], reverse=True)
        #         final_results_sorted = final_results_sorted[:10]
        #     # print("sorted list is:" )
        #     # print(final_results_sorted)
        # print("--------------")
        # # final_title_list = []
        # for id,value_for_that_id in final_results_sorted:
        #     final_title_list.append(self.obj_file.binary_search_for_title(id))
        

        # print(final_title_list)

        return final_result



    def search_for_both(self,gen_query,list_of_field_queries,final_result):
        final_result = self.search_for_general_query(gen_query,final_result)
        final_result = self.search_for_field(list_of_field_queries,final_result)
        return final_result



    def type_of_query(self,query_per_line,final_result):
        
        fields_tags_list = ["t:","b:","i:","c:","r:","l:"]
        field_flag = 0
        for tag in fields_tags_list:
            if(tag in query_per_line):
                field_flag = 1
                query_per_line = query_per_line.replace(tag,"*#"+tag)
                # print(query_per_line)
        if(field_flag == 0): #when no field query present
            final_result = self.search_for_general_query(query_per_line,final_result)
            # print("1")
            # print(query_per_line)
            # return final_result

        else:
            queries = query_per_line.split("*#")
            if(query_per_line[0:2] == "*#"): # if query starts with field query then no generla query present
                final_result = self.search_for_field(queries[1:],final_result)
                print("3")
                print(queries[1:])


            else: #when query started with general query but also has field queries later on
                final_result = self.search_for_both(queries[0],queries[1:],final_result) 
                print("2")
                print(queries[0],queries[1:])


        return final_result

    def get_ans(self,final_result):
        final_results_sorted = sorted(final_result.items(), key = lambda item : item[1], reverse=True)
        final_results_sorted = final_results_sorted[:10]
        # print("sorted list is:" )
        # print(final_results_sorted)
        print("--------------")
        final_title_list = []
        for id,value_for_that_id in final_results_sorted:
            final_title_list.append(self.obj_file.binary_search_for_title(id))

        print(final_title_list)
        return final_title_list


    def write_ans_to_file(self,final_title_list,time_taken):
        with open("queries_op.txt",'a') as f_q_op:
            f_q_op.write(''.join(final_title_list))
            f_q_op.write(str(time_taken)+"\n\n")



if __name__ == "__main__":
    # whole_search_start_time = time.time()
    # print(parser.final_file_number)
    
    with open('./output_final/misc_info.txt','r') as f_n:
        misc_info = [temp.strip("\n") for temp in f_n.readlines()]
    # last_file_suffix = int(pages_and_words_info[0])-1 #-1 already done and important as well becuase if pages_and_words_info[0] = 3, that means there are 3 file 0.txt, 1.txt, 2.txt
    # N_total_doc = int(pages_and_words_info[2])
    # final_unique_words = int(pages_and_words_info[1])
    # no_of_doc_to_make_intermed_index_in_each_file = int(pages_and_words_info[3])
    # no_of_words_in_final_index_files = int(pages_and_words_info[4])
    # no_of_titles_in_id_title_txt = int(pages_and_words_info[5])

    
    obj_preprocess = TextCleaning()
    obj_ranking = Ranking(misc_info)
    obj_file = FileHandler(misc_info)
    obj_query = InputQuery(obj_preprocess,obj_file,obj_ranking)

    queries_file = sys.argv[1]

    
    
    with open (queries_file,'r') as f_q:
        while(1):
            start = time.time()
            query_per_line = f_q.readline().strip("\n")
            if not query_per_line:
                break
            final_result = defaultdict(float)
            # final_title_list = []
            final_result = obj_query.type_of_query(query_per_line,final_result)
            final_title_list = obj_query.get_ans(final_result)
            end = time.time()
            time_taken = end-start
            obj_query.write_ans_to_file(final_title_list,time_taken)
            print("------------")

    # end = time.time()

    # print("time taken: ",end-whole_search_start_time)

    




# Search_Engine_IRE

<!-- to do/points to think
- remove/ignore words/sentneces not visible in wiki webpage - like things inside double braces(only the last elemnt when split by '|' is meaningful). like for eg, "abc.jpg" is of no use. such are still present in text.

- why spimi - adv and other ways

- cleaning and processing of links and refs!

- last writing of file not happening when doing so from outside all classes. it happens when i do it  after encountering mediawiki as end element in the article handler class

- string + ko .join kro

- in ko slice se replace kro(if it is in the starting)

- some has "==References==","== References ==","===External Links===" etc - handled

- to remoove {{commons...}} in ref/links - currently handling this by only accepting those lines starting with '*' -->
  
INDEXING:
- first divided into intermediate indexes
- applying spimi algo or basically like merging k-sorted arrays, merged all the index files. all these final merged index files are in 'output_final' folder
- that folder has other files like "id_title" .txt mappign doc id to title. 
- Though secondary index was created for the merged indexes, it is not necessary for the id-title as one can directly access the fiel no by dividing operator(say if every file has 5L titles, file no can be retrieved by (doc_id/5L).ceil -1).txt)
- total indexing was able to complete withing 270s for the 1.4GB data  
- 'total_index_pages_doc.txt : 
    - no of final index txt files
    - total no of tokens across all such index files
    - total no of documents in the dump

SEARCHING:
- for searching, first we identify what type of query is there:
    - only general query word
    - only field query word
    - general followed by field query
- thus accordingly binary search is done first on second index and then on the actual file to get the postings.
- on these postings tf-idf will be applied to get the final results.


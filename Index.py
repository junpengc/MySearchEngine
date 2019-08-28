# Index module
# Author: Junpeng Chen 26747553

import os;
import re;
import math;
import PorterStemmer;



def index_collection(collection_dir,index_dir = './index',stopword_f ='stopwords.txt'):
    collection_dir = os.path.abspath(collection_dir)
    documents = [os.path.join(collection_dir,x) for x in os.listdir(collection_dir) if os.path.isfile(os.path.join(collection_dir,x)) and os.path.splitext(x)[1] == '.txt'];
    inverted_file = {}


    # Building spell check vocabulary:
    words = [];
    for i in documents:
        with open(i,'r',encoding='utf8') as file:
            contents = file.read();
        words += re.findall(r'\w+',contents.lower());
    counter = dict();

    words = remove_stopwords(stopword_f,words);
    for i in words:
        if i not in counter:
            counter[i] = 1;
        else:
            counter[i] += 1;
    vocabulary_file_path = os.path.join(os.path.join('.',index_dir),'vocabulary.txt');
    with open(vocabulary_file_path,'w',encoding='utf8') as vocabulary:
        for i in counter:
            vocabulary.writelines(i+',' + str(counter[i]) + '\n');

    # Indexing document abbreviation and document name
    for i in range(1,len(documents)+1):
        inverted_file['d' + str(i)] = [os.path.split(documents[i-1])[1]];

    # Indexing 
    for i in documents:
        terms = tokenize(i);
        terms = normalize(terms);
        terms = remove_stopwords(stopword_f,terms);    
        terms = stem(terms);
        #print(sorted(terms,key = lambda x:len(x)));
        #print(terms);
        #print(len(terms));
        inverted_file = create_index(inverted_file,terms,i);
    
    inverted_file = append_idf(inverted_file,len(documents));
    save_inverted_file(inverted_file,index_dir);

    print("Indexing completed.");


def tokenize(document):
    if os.path.isfile(os.path.join('.',document)):
        print("Indexing: ",os.path.split(document)[1]);
    else:
        print("Searching for: " + document);
    terms =[];
    parser = re.compile(r"[\{\}\-\.,:;\"\'\(\)?!]*\s[\{\}\-\.,:;\"\'\(\)?!]*");

    # if document is a file, read and tokenize, if it is a query, process directly
    if os.path.isfile(document):
        with open(document,'r',encoding='utf8') as file:
            content = file.read();
    else:
        content = document;

    content = extract_special_terms(terms,content);
    words = parser.split(content);
    terms += words;
    return terms;


def extract_special_terms(terms,content):

    # Delete line break, '-' and '\n'
    cross_line_break = re.compile(r'-\n');
    content = cross_line_break.sub('',content);

    # Delete 's and s'
    s = re.compile(r'\'s\s');
    content = s.sub(' ',content);

    # Delete o' in o'clock
    o = re.compile(r'o\'');
    content = o.sub(' ',content);

    # Extract terms in single quotation:
    single_quotation = re.compile(r"\'(\w{2,}.+?\w{1})\'");
    result = re.findall(single_quotation,content);
    add_pattern_in_collection(result,terms);
    content = single_quotation.sub('',content);

    # Extract email
    email = re.compile(r"\w+@\w+\.\w+\s");
    result = re.findall(email,content);
    add_pattern_in_collection(result,terms);
    content = email.sub('',content);

    # Extract URL
    url = re.compile(r"((ftp|http|https):(\S*))");
    result = re.findall(url,content);
    add_pattern_in_collection(result,terms);
    content = url.sub('',content);

    # Extract IPv4 address
    ipv4 = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}");
    result = re.findall(ipv4,content);
    add_pattern_in_collection(result,terms);
    content = ipv4.sub('',content);

    # Extract Acronym
    acronym = re.compile(r"(([A-Z]\.)+[A-Z])");
    result = re.findall(acronym,content);    
    add_pattern_in_collection(result,terms);
    content = acronym.sub('',content);

    # Combined Terms
    combined_temrs = re.compile(r"(([A-Z]{1}([a-z]+)[\s|\{\}\-\.,:;\"\'\(\)?!]{1,2}){2,})");
    result = re.findall(combined_temrs,content);
    add_pattern_in_collection(result,terms);
    content = combined_temrs.sub('',content);

    
    return content;


def add_pattern_in_collection(pattern,collection):
    for i in pattern:
        if type(i) is str:
            collection.append(re.sub(r"[\n\-\.,:;\"\'\(\)?!]{1,2}$",' ',i).strip());
        elif type(i) is tuple:
            collection.append(re.sub(r"[\n\-\.,:;\"\'\(\)?!]{1,2}$",' ',i[0]).strip());


def normalize(terms):
    result = []
    punctuation = re.compile(r'[\[\]\{\}\-\.,:;\"\'\(\)?!]*');
    new_line_symbol = re.compile(r'\n');
    for i in terms:
        if i:
            lower = i.lower()
            new_line_symbol_removed = re.sub(new_line_symbol,' ',lower);
            punctuation_removed = re.sub(punctuation,'',new_line_symbol_removed);
            under_score_removed = punctuation_removed.strip('_');
            result.append(under_score_removed);
    return result;


def remove_stopwords(stopword_f,terms):
    with open(stopword_f) as file:
        stopword_list = [x.strip() for x in file];
    stopword_list = normalize(stopword_list);
    result = [i for i in terms if i not in stopword_list];

    return result;


def stem(terms):
    ps = PorterStemmer.PorterStemmer();
    return [ps.stem(x,0,len(x)-1) for x in terms];


def create_index(inverted_file,terms,document):
    
    # Get document abbreviation
    document_name = os.path.split(document)[1];
    document_abb = '';

    for key,values in inverted_file.items():
        if inverted_file[key][0] == document_name:
            document_abb = key;
            break;

    if document_abb == '':
        raise RuntimeError('Error: File name not found in index, might be a change of name.');

    for i in terms:
        if i not in inverted_file:
            inverted_file[i] = [document_abb,1]
        else:
            if document_abb not in inverted_file[i]:
                inverted_file[i] += [document_abb,1];
            else:
                for j in range(len(inverted_file[i])):
                    if inverted_file[i][j] == document_abb:
                        inverted_file[i][j+1]+=1;
                        break;

    return inverted_file;
    

def append_idf(inverted_file,N):
    for key,values in inverted_file.items():
        df = len(values)/2;
        if df >= 1:
            idf = round(math.log2(N/(df+1)),3);
            values.append(idf);

    return inverted_file;



def save_inverted_file(inverted_file,index_dir):
    index_file_path = os.path.join(os.path.join('.',index_dir),'index.txt');
    with open(index_file_path,'w',encoding='utf8') as file:
        for key in inverted_file.keys():
            file.writelines(str(key) +',' + str(inverted_file[key]).strip('[]') + '\n');
                            


if __name__ == '__main__':
    index_collection('./Tests','./index','stopwords.txt');

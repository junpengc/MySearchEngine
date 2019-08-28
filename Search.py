import Index;
import os;
import math;
import csv;

def search(index_dir,num_docs,query):
    if type(query) is list:
        query = ', '.join(query);


    if not os.path.isdir(index_dir):
        raise RuntimeError('Index Directory Not Found!');
        return;    
    if not os.path.isfile(os.path.join(index_dir,'index.txt')):
        raise RuntimeError('Index File Not Found!');
        return;

    inverted_file = load_inverted_file(os.path.join(index_dir,'index.txt'));
    vocabulary = load_vocabulary(os.path.join(index_dir,'vocabulary.txt'));
    #Spell checking process;
    old_query = query;
    query = spellChecking(query,vocabulary);
    if query != old_query:
        print("Do you mean: " +  query);

    document_vectors = create_document_vectors(inverted_file);
    query_vector = create_query_vector(inverted_file,query);
    

    cos_similarity = calculate_similarity(query_vector,document_vectors);
    cos_similarity = sorted(cos_similarity.items(),key = lambda x:x[1],reverse = True);
    
    #print_inter_result(inverted_file,document_vectors,query_vector,cos_similarity);

    print("Result befor Rocchio Relevence Feedback:");
    print_result(cos_similarity,inverted_file,int(num_docs));



    # Performing rocchio relevence_feedback
    feedback = input("Choose the relevant document to imporve results( e.g. 1,2,3): ");
    while not validateFeedback(feedback,len(cos_similarity)):
        feedback = input("Choose the relevant document to imporve results( e.g. 1,2,3): ");

    print("\nResult after Rocchio Relevence Feedback:")
    cos_similarity = rocchio_relevence_feedback(query_vector,document_vectors,cos_similarity,feedback);
    print_result(cos_similarity,inverted_file,int(num_docs));



def load_inverted_file(file_path):
    with open(file_path,'r',encoding = 'utf8') as index_file:
        content = csv.reader(index_file,quotechar="'");

        result = {};
        for values in content:
            # if it is a document abbreviation item, set value to document name
            # if it is a term, assign document abbreviation, then term frequncy, at last append idf.
            if len(values) <= 2:
                result[values[0]]=values[1].strip("'");
            else:
                result[values[0]] = [];
                for j in range(1,len(values)-1,2):
                    result[values[0]].append(values[j].strip(" ").strip("'"));
                    result[values[0]].append(int(values[j+1]));
                result[values[0]].append(float(values[-1]));

    return result;

def load_vocabulary(file_path):
    with open(file_path,'r',encoding='utf8') as vocabulary_file:
        content = csv.reader(vocabulary_file);
        result = {};
        for values in content:
            if len(values) >= 2:
                result[values[0]] = int(values[1]);
    
    return result;

def create_document_vectors(inverted_file):
    doc_abb = [];
    for key,values in inverted_file.items(): 
        # if it is a document abbreviation index, not doing anything. 
        if type(values) is str:
            doc_abb.append(key);

    document_vectors = {x:[] for x in doc_abb};
    for term,values in inverted_file.items():
        if not type(values) is list:
            continue;

        for i in range(0,len(values)-1,2):
            document_vectors[values[i]].append(values[i+1]*values[-1]);
        

        term_number = max([len(x) for x in document_vectors.values()])
        for i in document_vectors.values():
            if len(i) < term_number:
                i.append(0.0);

    return document_vectors;

def create_query_vector(invertd_file,query):
    query_terms = Index.tokenize(query);
    query_terms = Index.normalize(query_terms);
    query_terms = Index.stem(query_terms);
    # only use terms that already in vocabulary;
    query_terms = [x for x in query_terms if x in invertd_file.keys()];
    
    # Count query term frequency
    query_tf = {};
    for i in query_terms:
        if i not in query_tf:
            query_tf[i] = 1;
        else:
            query_tf[i] += 1;

    # Generate query vector;
    query_vector = [];
    for key,values in invertd_file.items():
        if type(values) is str:
            continue;
        else:
            if key not in query_tf:
                query_vector.append(0);
            else:
                query_vector.append(query_tf[key]*values[-1])

    return query_vector;

def calculate_similarity(qv,dvs):
    cos_similarity = {};

    #calculat query vector length
    qv_length = 0;
    for i in qv:
        qv_length += i**2;
    qv_length = math.sqrt(qv_length);

    if qv_length == 0:
        return {};

    for key,i in dvs.items():
        v_product = 0;
        dv_length = 0;
        for j in range(len(i)):
            v_product += (qv[j] * i[j]);
            dv_length += i[j]**2;
        dv_length = math.sqrt(dv_length);
        cos_similarity[key] = round(v_product / (dv_length * qv_length), 3);

    return cos_similarity;

def print_result(cos_similarity,inverted_file,num_docs):
    num_docs = min(num_docs,len(cos_similarity));
    if len(cos_similarity) == 0:
        print("No Matching Document.");
    for i in range(num_docs):
        if cos_similarity[i][1] > 0:
            print(i+1,'.',inverted_file[cos_similarity[i][0]],'Relevance:', cos_similarity[i][1]);
    

def rocchio_relevence_feedback(query_vector,document_vectors,cos_similarity,feedback = ''):
    damping_factor = 0.95;
    #top_k_as_relevent = 2;

    #printing parameters of Rocchio
    print("Damping factor: " + str(damping_factor));

    feedback = feedback.split(',');
    for i in range(len(feedback)):
        feedback[i] = int(feedback[i]) - 1;


    dimensions_number = len(query_vector);
    # Calculat relevent vector mean
    relevent_centroid = [0 for x in range(dimensions_number)];
    irrelevent_centroid = [0 for x in range(dimensions_number)];
    
    for i in feedback:
        document_abb = cos_similarity[i][0];
        document_vector = document_vectors[document_abb];
        for j in range(dimensions_number):
            relevent_centroid[j] += document_vector[j];
    
    for i in range(dimensions_number):
        relevent_centroid[i] /= len(feedback);

    for i in range(len(cos_similarity)):
        if not i in feedback:
            document_abb = cos_similarity[i][0];
            document_vector = document_vectors[document_abb];
            for j in range(dimensions_number):
                irrelevent_centroid[j] += document_vector[j];

    for j in range(dimensions_number):
        irrelevent_centroid[i] /= (len(cos_similarity) - len(feedback))


    new_query_vector = [0 for x in range(len(query_vector))];
    for i in range(len(new_query_vector)):
        new_query_vector[i] = query_vector[i] + damping_factor * relevent_centroid[i] - (1-damping_factor) * irrelevent_centroid[i];
        # Bug fix, new query field should be less than zero after minus operation. 
        new_query_vector[i] = max(new_query_vector[i],0)

    cos_similarity = calculate_similarity(new_query_vector,document_vectors);
    cos_similarity = sorted(cos_similarity.items(),key = lambda x:x[1],reverse = True);


    return cos_similarity;

def print_inter_result(inverted_file,document_vectors,query_vector,cos_similarity):
    print(inverted_file);
    for key,values in document_vectors.items():
        print(key,values);
    print('q1',query_vector);
    print(cos_similarity);

def validateFeedback(feedback = '',maxAllowed=0):
    relevantDoument = feedback.split(',');
    for i in relevantDoument:
        if not i.isdigit() or int(i) > maxAllowed:
            print("input Error")
            return False;
    return True;

def spellChecking(query,vocabulary):
    query = query.split(',');
    for i in range(len(query)):
        word = query[i].strip(' ');
        if word not in vocabulary:
            word_similarities = [];
            for j in vocabulary:
                word_similarities.append([j,calculate_word_similarity(word,j)]);
                # word similarity sublinear normalization, or use a bigger stop word lists.
                word_similarities[-1][1] *= math.log10(vocabulary[j]);
            word_similarities = sorted(word_similarities,key = lambda x:x[1],reverse=True);
            query[i] = word_similarities[0][0];
            print("Could be: ");
            print(word_similarities[:5]);
    return ' ,'.join(query);

def calculate_word_similarity(word1,word2):
    # or should i use longest substring match??
    # can only deal with replace, not delete,insert,transpose
    same_letter_count = 0;
    for i in range(min(len(word1),len(word2))):
        if word1[i] == word2[i]:
            same_letter_count+=1;

    # length using both words, is this a good idea?
    return same_letter_count/max(len(word1),len(word2)); 
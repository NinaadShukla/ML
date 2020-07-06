#!/usr/bin/env python
# coding: utf-8

# #### Including library

# In[429]:


from nltk.tokenize import regexp_tokenize
from collections import Counter,defaultdict
from math import log,floor
import random
import email
import email.policy
import numpy as np


# In[430]:


def createtokens(s):
    words = regexp_tokenize(s.lower(),r"\b[a-zA-Z0-9]+\b")
    words = list(filter(lambda x: not str.isnumeric(x) and len(x)>2,words))
    return words


# In[431]:


from os import listdir
from os.path import isfile, join
spampath = "hamnspam/spam/"
hampath = "hamnspam/ham/"
filepaths = lambda mypath : [join(mypath,f) for f in listdir(mypath) if isfile(join(mypath, f)) and not str.startswith(f,r".")]


# In[432]:


ham_filenames = [name for name in sorted(listdir('hamnspam/ham')) if len(name) > 20]
spam_filenames = [name for name in sorted(listdir('hamnspam/spam')) if len(name) > 20]

def load_email(is_spam, filename):
    directory = "hamnspam/spam" if is_spam else "hamnspam/ham"
    with open(join(directory, filename), "rb") as f:
        return email.parser.BytesParser(policy=email.policy.default).parse(f)
    
ham_emails = [load_email(is_spam=False, filename=name) for name in ham_filenames]
spam_emails = [load_email(is_spam=True, filename=name) for name in spam_filenames]

def get_email_structure(email):
    if isinstance(email, str):
        return email
    payload = email.get_payload()
    if isinstance(payload, list):
        return "multipart({})".format(", ".join([
            get_email_structure(sub_email)
            for sub_email in payload
        ]))
    else:
        return email.get_content_type()

def html_to_plain(email):
    try:
        soup = BeautifulSoup(email.get_content(), 'html.parser')
        return soup.text.replace('\n\n','')
    except:
        return "empty"

def email_to_plain(email):
    struct = get_email_structure(email)
    for part in email.walk():
        partContentType = part.get_content_type()
        if partContentType not in ['text/plain','text/html']:
            continue
        try:
            partContent = part.get_content()
        except: # in case of encoding issues
            partContent = str(part.get_payload())
        if partContentType == 'text/plain':
            return partContent
        else:
            return html_to_plain(part)
        


# In[433]:


def mailtotxt(mail):
    txt = email_to_plain(mail)
    if txt is None:
        txt="empty"
    txt = txt.lower()
    return txt
spam_txt = list(map(lambda x:mailtotxt(x),spam_emails))
ham_txt  = list(map(lambda x:mailtotxt(x),ham_emails))


# In[434]:


import nltk
stemmer = nltk.PorterStemmer()
def createcounter(txt):
    word_count = Counter(createtokens(txt)) 
    stemmed_word_count = Counter()
    for word, count in word_count.items():
        stemmed_word = stemmer.stem(word)
        stemmed_word_count[stemmed_word] += count
    return word_count

spam_counters = []
ham_counters = []
for txt in spam_txt:
    spam_counters.append(createcounter(txt))
for txt in ham_txt:
    ham_counters.append(createcounter(txt))


# In[435]:


total_spam_counters = Counter()
for c in spam_counters:
    total_spam_counters += c

total_ham_counters = Counter()
for c in ham_counters:
    total_ham_counters += c

total_counters = total_ham_counters+total_spam_counters


# In[465]:


stop_words_size=15
stop_words = total_counters.most_common(stop_words_size)
vocab_size = 5000
vocab = total_counters.most_common()[stop_words_size:stop_words_size+vocab_size]


# In[466]:


alpha = 1
def countertovector(c):
    vect = np.zeros((vocab_size,))
    for i in range(vocab_size):
#         vect[i] = c[vocab[i][0]]
        vect[i] = int(vocab[i][0] in c)
    return vect


# In[467]:


mf = .75
spam_vectors = np.array([countertovector(c) for c in spam_counters ])
ham_vectors = np.array([countertovector(c) for c in ham_counters ])
spam_vectors_test = spam_vectors[floor(len(spam_vectors)*mf):]
ham_vectors_test = ham_vectors[floor(len(ham_vectors)*mf):]
spam_vectors = spam_vectors[:floor(len(spam_vectors)*mf)]
ham_vectors = ham_vectors[:floor(len(ham_vectors)*mf)]


# In[468]:


total_spam_freq = spam_vectors.sum(axis=0)
total_spam_freq += alpha * np.ones_like(total_spam_freq)
total_ham_freq = ham_vectors.sum(axis=0)
total_ham_freq += alpha * np.ones_like(total_ham_freq)
ham_words_total = sum(total_ham_freq)
spam_words_total= sum(total_spam_freq)


# In[469]:


pw_spam = total_spam_freq/spam_words_total
pw_ham = total_ham_freq/ham_words_total
p_spam = spam_vectors.shape[0]/(ham_vectors.shape[0]+spam_vectors.shape[0])
p_ham = ham_vectors.shape[0]/(ham_vectors.shape[0]+spam_vectors.shape[0])


# In[470]:


def classifytxt(message):
    vect = countertovector(createcounter(message))
    return classifyvector(vect)

def classifyvector(vect):
    logspam = log(p_spam)
    logham = log(p_ham)
    for i in range(len(vect)):
        logspam += vect[i]*log(pw_spam[i])
        logham += vect[i]*log(pw_ham[i])
    return logspam>logham

def classifydir(directory,ismail=False):
    output = dict()
    filenames = filepaths(directory)
    #print(filenames)
    for file in filenames:
        with open(file,encoding="ISO-8859-1") as f:
            txt = f.read()
        output[file]=classifytxt(txt)
    return output


# In[471]:


classifydir('test')


# In[472]:


correctspam=0
for txt in spam_vectors_test:
    correctspam+=classifyvector(txt)
correctham=0
for txt in ham_vectors_test:
    correctham+=not classifyvector(txt)

lsvt = len(spam_vectors_test)    
cs = correctspam
ch = correctham
lhvt = len(ham_vectors_test)
print('''
spam predicted correctly : %d %% (%d/%d)
ham predicted correctly : %d %% (%d/%d)
Accuray : %d %% (%d/%d)
'''%((cs*100)/lsvt,cs,lsvt,(ch*100)/lhvt,ch,lhvt,((cs+ch)*100)/(lsvt+lhvt),cs+ch,lsvt+lhvt))


# In[473]:


print('''
Size of Dataset: %d
No of spam mails: %d
No of Ham mails : %d
Train-Test Splitting Factor: %d%%-%d%%
No of spam mails used for training : %d
No of Ham mails used for training : %d
No of spam mails used for testing : %d
No of Ham mails used for testing : %d
'''%(len(spam_counters)+len(ham_counters),len(spam_counters),len(ham_counters),mf*100,(1-mf)*100,len(spam_vectors),len(ham_vectors),lsvt,lhvt))


# In[474]:


print('size of vocabulary %d'%vocab_size)
print('alpha = %f'%alpha)
print('%d stop words removed'%len(stop_words),stop_words)


# We are also removing numbers and words with length 1 and 2 (i.e a, an, is, etc) from the Vocab

# references : https://www.kaggle.com/veleon/spam-classification ( code for data cleaning, and fetching the content of the mail)
# library used : <br>
# ntlk : for tokenizing and stemming 

# In[ ]:





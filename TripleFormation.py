import spacy
nlp = spacy.load('en_core_web_sm')

from nltk import ngrams
from spacy.matcher import Matcher 
from spacy.tokens import Span 

def get_entities(sent):
  ## chunk 1
  ent1 = ""
  ent2 = ""

  prv_tok_dep = ""    # dependency tag of previous token in the sentence
  prv_tok_text = ""   # previous token in the sentence

  prefix = ""
  modifier = ""

  #############################################################
  for tok in sent:
    ## chunk 2
    # if token is a punctuation mark then move on to the next token
    if tok.dep_ != "punct":
      # check: token is a compound word or not
      if tok.dep_ == "compound":
        prefix = tok.text
        # if the previous word was also a 'compound' then add the current word to it
        if prv_tok_dep == "compound":
          prefix = prv_tok_text + " "+ tok.text
      
      # check: token is a modifier or not
      if tok.dep_.endswith("mod") == True:
        modifier = tok.text
        # if the previous word was also a 'compound' then add the current word to it
        if prv_tok_dep == "compound":
          modifier = prv_tok_text + " "+ tok.text
      
      ## chunk 3
      #if tok.dep_.find("subj") == True and (tok.pos_!="PRON" and tok.pos_!="VERB" and tok.pos_!="DET"):
      if tok.dep_.find("subj") == True:
        #print (tok.text,tok.pos_)
        ent1 = modifier +" "+ prefix + " "+ tok.text
        prefix = ""
        modifier = ""
        prv_tok_dep = ""
        prv_tok_text = ""      

      ## chunk 4
      #if tok.dep_.find("obj") == True and (tok.pos_!="PRON" and tok.pos_!="VERB" and tok.pos_!="DET"):
      if tok.dep_.find("obj") == True:
        ent2 = modifier +" "+ prefix +" "+ tok.text
        prefix = ""
        modifier = ""
        prv_tok_dep = ""
        prv_tok_text = ""
        
      ## chunk 5  
      # update variables
      prv_tok_dep = tok.dep_
      prv_tok_text = tok.text
  #############################################################
  return [ent1.strip(), ent2.strip()]

def get_relation(sent):

  doc = nlp(sent)

  # Matcher class object 
  matcher = Matcher(nlp.vocab)

  #define the pattern 
  pattern = [{'DEP':'ROOT'}, 
            {'DEP':'neg','OP':"?"},
            {'DEP':'prep','OP':"?"},
            {'DEP':'agent','OP':"?"},  
            {'POS':'ADJ','OP':"?"}] 

  matcher.add("matching_1", None, pattern) 

  matches = matcher(doc)
  k = len(matches) - 1

  span = doc[matches[k][1]:matches[k][2]] 

  return(span.text)

def topic_entity_compare(entity, topics):
  allgrams=[]
  allwords=[]
  for n in range(1, len(entity.split())+1):
    ng = ngrams(entity.split(), n)
    for grams in ng:
      #print (grams)
      gram_word=""
      allgrams.append(grams)
      for gram in grams:
        gram_word+=gram+" "
      gram_word=gram_word.strip()
      allwords.append(gram_word)
    
  for topic in topics:
    if topic in allwords:
        return True

  return False

def entity_entity_compare(entity, entities):
  allgrams=[]
  allwords=[]
  for n in range(1, len(entity.split())+1):
    ng = ngrams(entity.split(), n)
    for grams in ng:
      #print (grams)
      gram_word=""
      allgrams.append(grams)
      for gram in grams:
        gram_word+=gram+" "
      gram_word=gram_word.strip()
      allwords.append(gram_word)
    
  for entity in entities:
    if entity in allwords:
        return True

  return False


def getTriples(df):
  triple_doc=[]
  te_triple_doc=[]
  counter=0
  for doc in df['text']:
    #print (doc)
    triples=[]
    te_triples=[]
    nlp_doc = nlp(doc)
    topics=df.iloc[counter]['topics']
    #print (nlp_doc.ents)
    top=[]
    for topic in topics:
      topic=topic.replace("_", " ")
      topic=topic.strip()
      top.append(topic)
    topics=top
    #print (topics)
    doc_ents = {}
    for ent in nlp_doc.ents:
        doc_ents[ent.text]=ent.label_
    #print (doc_ents)
    for sent in nlp_doc.sents:
      #print (sent.text)
      entities = get_entities(sent)
      #print (entities)
      relation = get_relation(sent.text)
      #print (relation)
      triple=[entities[0], relation, entities[1]]
      if (entities[0]!="" and entities[1]!="" and relation!=""):
        #if((entities[0] in doc_ents.keys() or topic_entity_compare(entities[0],topics)) or (entities[1] in doc_ents.keys() or topic_entity_compare(entities[1],topics))):
        if((entity_entity_compare(entities[0], doc_ents.keys()) or topic_entity_compare(entities[0],topics)) or (entity_entity_compare(entities[1], doc_ents.keys()) or topic_entity_compare(entities[1],topics))):
          te_triple=[entities[0], relation, entities[1]]
          #entities.extend(relation)
          #print (triple)
          te_triples.append(te_triple)
        triples.append(triple)
    triple_doc.append(triples)
    te_triple_doc.append(te_triples)
    #print (triples)
    #print(len(triples))
    #print ("te")
    #print (te_triples)
    #print(len(te_triples))
    counter+=1
    if (counter%25 == 0):
      print (counter)
  return (te_triple_doc)

#news_data_sampled['triples'] = getTriples(news_data_sampled)

#news_data_sampled.head()
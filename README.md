# NLP

### Introduction
This project aim to build a spell-checking system which can detect non-words and real words errors, then suggest correct word choice specifically in the computer science field. 
objectives:
1. To build a spell-checker which can detect non-word error using minimum edit distance technique.
2. To build a spell-checker which can detect real words errors using  bigram technique. 

### Challenges
The system's current capabilities for real-word error detection are limited. This limitation is due to its heavy reliance on the corpus used.

### Tools Used
nltk (Natural Language Toolkit), tkinter, re (Regular expression operation), levenshtein, os (Miscellaneous Operating System)

### Corpus
1. The first corpus is drawn from the computer science domain, incorporating text from ten selected research papers.
2. The second corpus, a generalized English lexicon, is derived from the widely used Brown Corpus provided by the Natural Language Toolkit (NLTK) nltk.corpus.brown, this specific corpus is a collection of the Brown University Standard Corpus of Present-Day American English. 

### Improvement
Expand the size and diversity of the training corpus would improve the system's understanding of word usage in various contexts. In addition to that, implementing more complex language models such as trigrams or n-grames could be beneficial. Moreover, incorporating a more sophisticated Natural Language Processing (NLP) model such as transformer-based models, could boost the system's contextual understanding.

### Conclusion
In conclusion, while the system is proficient in non-word error detection, its ability to detect real-word errors could be significantly improved through the mentioned strategies. With careful planning and implementation, the system's overall performance and utility can be significantly enhanced.



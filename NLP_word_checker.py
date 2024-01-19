# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 14:19:15 2023

@author: 60183
"""
# Import necessary libraries
import nltk
import tkinter as tk
from tkinter import ttk, Text, Listbox
import re
from nltk.tokenize import word_tokenize
from Levenshtein import distance  # Library for calculating Levenshtein distance between two words
from nltk.probability import ConditionalFreqDist
from nltk.corpus import brown  # Import the Brown Corpus
from nltk import bigrams  # Function to generate bigrams from a list
import os  # Library for OS related functionalities

# Function to read and process the corpus
def read_corpus():
    folder_path = '../Corpus'  # Specifying the path to the folder containing the files
    file_paths = []

    for file_name in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_name)):
            file_path = os.path.join(folder_path, file_name).replace('\\', '/')
            file_paths.append(file_path)

    word_dict = set()  # Initialize an empty set to store the unique words
    bigram_list = []
    
    # Reading each file in the corpus and performing necessary preprocessing
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            corpus_text = file.read()

        tokens = word_tokenize(corpus_text)
        # Normalize the tokens and filter out non-alphanumeric characters except for punctuation
        normalized_tokens = [token.lower() for token in tokens if re.match('^[a-zA-Z\']+$|[.,;]$', token)]
        # Add the unique words from each file to the word_dict set
        word_dict.update(normalized_tokens)  
        bigram_list.extend(list(bigrams(normalized_tokens)))

    # Get the words from the Brown corpus
    brown_words = [word.lower() for word in brown.words() if re.match('^[a-zA-Z]+|[.,;]$', word)]
    word_dict.update(brown_words)  # Add the unique words from the Brown corpus to the word_dict set
    
    # Create word_dict_search, which only includes alphabetical words
    word_dict_search = set([word for word in word_dict if word.isalpha()])
    
    # Create bigrams
    brown_bigrams = list(bigrams(brown_words))
    
    # Extend bigram_list with the bigrams from the Brown corpus
    bigram_list.extend(brown_bigrams)
    bigram_freq = ConditionalFreqDist(bigram_list)
    return word_dict, bigram_freq, word_dict_search

# Class to create a GUI for word checking and correction
class WordChecker(tk.Tk):
    def __init__(self, corpus_folder):
        super().__init__()
        self.title("Word Checking GUI")
        # Reading the corpus and initializing the required data structures
        self.dictionary, self.bigrams, self.dictionary_search = read_corpus()
        self.correction_window = None
    
        # Setup the main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)
    
        # Configure grid
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=2)
        self.main_frame.grid_columnconfigure(1, weight=1)
    
        # Add legend lines
        legend_frame = self.create_frame(self.main_frame, row=0, column=0, columnspan=2)
        legend1 = ttk.Label(legend_frame, text="Highlighted red for non-word error.", foreground="red")
        legend2 = ttk.Label(legend_frame, text="Highlighted yellow for real-word error.", foreground="black")
        legend1.pack(anchor='w')
        legend2.pack(anchor='w')

    
        # Frame for Input Sentence
        self.input_frame = self.create_frame(self.main_frame, row=1, column=0, rowspan=2)
        ttk.Label(self.input_frame, text="Input Sentence:").pack()
        self.input_text = Text(self.input_frame)
        self.input_text.pack(fill='both', expand=True)
        self.input_text.tag_config('error', background='red')
        self.input_text.tag_config('potential_error', background='yellow')
        self.input_text.bind('<KeyRelease-space>', self.mark_words)  # Mark words upon pressing space
        self.input_text.bind('<Button-1>', self.show_suggestions)  # Show suggestions when a word is clicked
    
        # Frame for Suggested Words
        self.suggested_frame = self.create_frame(self.main_frame, row=1, column=1)
        ttk.Label(self.suggested_frame, text="Suggested Words:").pack()
        self.suggested_text = Listbox(self.suggested_frame)
        self.suggested_text.pack(fill='both', expand=True)
        self.suggested_text.bind('<<ListboxSelect>>', self.replace_word)
    
        # Search Words
        self.search_frame = self.create_frame(self.main_frame, row=2, column=1)
        self.search_entry, self.search_text = self.create_search_frame(self.search_frame)
    
        self.checked_text = Text(self)

    # Function to suggest corrections for real words based on bigram frequencies
    def suggest_real_word_corrections(self, previous_word):
        all_suggestions = self.bigrams[previous_word.lower()].most_common()
        suggestions = []
        
        for word, freq in all_suggestions:
            if word.isalpha():  # Check if the word contains only alphabetic characters
                suggestions.append((word, freq))
                
            if len(suggestions) == 5:
                break
                
        return suggestions
     
    # new function to show the suggest words
    def show_suggestions(self, event):
        pos = self.input_text.index(f'@{event.x},{event.y} wordstart')
        pos_split = pos.split('.')
        if int(pos_split[1]) > 0:  # checks if the current position is not at the first character of the first word
            pos_before_word = f'{pos_split[0]}.{int(pos_split[1]) - 1}'  # position one character before the start of the current word
            word_before_pos = pos_before_word
            while True:
                if word_before_pos != "1.0":
                    word_before_pos = self.input_text.index(f'{word_before_pos} - 1c')  # shift to the left by one character
                    if self.input_text.get(word_before_pos) == ' ':  # stop when a space is encountered
                        word_before_pos = self.input_text.index(f'{word_before_pos} + 1c')  # move one character right to get to the start of the word
                        break
                else:
                    word_before_pos = "1.0"
                    break
            self.word_before_wrong_word = self.input_text.get(f'{word_before_pos} wordstart', f'{word_before_pos} wordend')  # get the word before the wrong word
    
        if 'error' in self.input_text.tag_names(pos):
            self.wrong_word = self.input_text.get(f'{pos} wordstart', f'{pos} wordend')
            try:
                suggestions, distances = self.suggest_corrections(self.wrong_word)
                self.suggested_text.delete(0, 'end')
                for word, dist in zip(suggestions, distances):
                    self.suggested_text.insert('end', f'{word} (distance: {dist})')
            except ValueError as e:
                print(f'An error occurred: {e}')
                return
        elif 'potential_error' in self.input_text.tag_names(pos):
            self.wrong_word = self.input_text.get(f'{pos} wordstart', f'{pos} wordend')
    
            try:
                suggestions = self.suggest_real_word_corrections(self.word_before_wrong_word)
                self.suggested_text.delete(0, 'end')
                for word,freq in suggestions:
                    self.suggested_text.insert('end', f'{word} (frequency: {freq})')
            except ValueError as e:
                print(f'An error occurred: {e}')
                return
            
    # Check if a word exists in the dictionary or if it's punctuation
    def is_word(self, word):
        return word.lower() in self.dictionary or word in ",.!?;"
    
    # Check if a bigram exists in our bigram list
    def is_valid_bigram(self, bigram):
        return bigram in self.bigrams

    # Calculate Levenshtein distance between two words
    def calc_distance(self, word):
        return word, distance(word, self.wrong_word)
    
    # Function to mark unknown words in red in the input sentence
    def mark_unknown_words(self, event=None):
        text = self.input_text.get(1.0, 'end-1c')
        words = re.findall(r'\b[\w\']+\b|[.,!?;]', text)  # include ' in the regex
        self.input_text.delete(1.0, 'end')
        for word in words:
            if not self.is_word(word):
                self.input_text.insert('end', word + ' ', 'error')
            else:
                self.input_text.insert('end', word + ' ')
                
    # Function to mark real word errors in the input sentence
    def mark_real_words_error(self, event=None):
        text = self.input_text.get(1.0, 'end-1c')
        words = re.findall(r'\b[\w\']+\b|[.,!?;]', text)
    
        # Get bigrams from sentence (including misspelled words)
        sentence_bigrams = list(bigrams(words))
    
        # Only keep the bigrams where both words are valid
        sentence_bigrams = [(w1, w2) for w1, w2 in sentence_bigrams if self.is_word(w1) and self.is_word(w2)]
    
        # Variable to store the last word of the previous valid bigram
        last_valid_word = None
    
        # Iterate over each word and its bigram
        for idx, (word1, word2) in enumerate(sentence_bigrams):
            bigram_freq = self.bigrams[word1][word2]  # Get the frequency of the bigram
    
            print(f"Bigram: {(word1, word2)}, Frequency: {bigram_freq}")  # Print out the frequency
    
            if bigram_freq <= 2:
                # Only mark the first word as an error if it was not part of a valid bigram before
                if word1 != last_valid_word:
                    # Start searching from the beginning of the text
                    pos = '1.0'
                    while pos:
                        # Start and end position of the word in the text
                        pos = self.input_text.search(' ' + word1 + ' ', pos, stopindex=tk.END)
                        if pos:
                            start = self.input_text.index(f'{pos}+1c')  # Adjust start position to avoid the space before the word
                            end = self.input_text.index(f'{start}+{len(word1)}c')
                            self.input_text.tag_add('potential_error', start, end)
                            pos = end  # Update the position to start searching from
    
            # Update the last valid word
            if bigram_freq > 2:
                last_valid_word = word2

    # Function to call both types of error_marking function in the input sentence
    def mark_words(self, event=None):
        self.mark_unknown_words()
        self.mark_real_words_error()
        
    #Function to replace an incorrect word with a selected correct word
    def replace_word(self, event):
        # get the selected line index
        idx = self.suggested_text.curselection()
    
        # get the selected line's text
        line = self.suggested_text.get(idx)
    
        # split the line on ':' and take the first part (the word)
        correct_word = line.split('(')[0].strip()
    
        start = self.input_text.search(self.wrong_word + ' ', '1.0', stopindex=tk.END)
        if start:
            # Including the following space in the deletion and replacement
            end = self.input_text.index(f'{start}+{len(self.wrong_word)+1}c')
            self.input_text.delete(start, end)
            self.input_text.insert(start, correct_word + ' ')
            end = self.input_text.index(f'{start}+{len(correct_word)+1}c')  # End point now includes the space after the word
    
            # remove all tags in the replaced word's range
            self.input_text.tag_remove('error', start, end)
            self.input_text.tag_remove('potential_error', start, end)
    
            # check if the new word exists in the dictionary
            if not self.is_word(correct_word):
                self.input_text.tag_add('error', start, end)
    
            self.suggested_text.delete(0, 'end')
    
    # Function to display suggestions for a selected incorrect word
    def suggest_words(self, event):
        pos = self.suggested_text.index(f'@{event.x},{event.y} wordstart')
        word = self.suggested_text.get(f'{pos} wordstart', f'{pos} wordend')
        word = re.sub(r'\s\(distance:\s\d+\)', '', word)  # remove the distance info from the word
        if word in self.dictionary:
            self.replace_word(word)  # use replace_word method to replace the wrong word 
    
    # Function to suggest corrections for a misspelled word
    def suggest_corrections(self, misspelled_word):
        misspelled_word = misspelled_word.lower()

        max_length_diff = 3
        candidates = [word for word in self.dictionary if
                      abs(len(word) - len(misspelled_word)) <= max_length_diff]

        distances = {word: distance(misspelled_word, word) for word in candidates}
        sorted_distances = sorted(distances.items(), key=lambda x: x[1])

        suggestions = [word for word, _ in sorted_distances[:5]]
        return suggestions, [dist for _, dist in sorted_distances[:5]]
    
    #Function to display words in the dictionary that start with the search term
    def search_words(self, event):
        search_term = self.search_entry.get()
        matches = sorted(word for word in self.dictionary_search if word.startswith(search_term))
        self.search_text.delete(1.0, 'end')
        self.search_text.insert('end', '\n'.join(matches))
    
    # Function to create a new frame in the GUI
    def create_frame(self, parent, row, column, rowspan=1, columnspan=1):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky='nsew')
        return frame
    
    # Function to create the search frame in the GUI
    def create_search_frame(self, parent):
        frame = ttk.Frame(parent)
        frame.pack()
        ttk.Label(frame, text="Search Words:").pack()
        entry = ttk.Entry(frame)
        entry.bind('<KeyRelease>', self.search_words)
        entry.pack()
        text = Text(frame)
        text.pack()
        return entry, text



if __name__ == '__main__':
    app = WordChecker('../Corpus')
    app.mainloop()

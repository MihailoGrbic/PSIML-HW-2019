import numpy as np
import os

class language:
    def __init__(self, name = None, path = None, bigram_dict = {}, bigram_list = [], bigram_num = None):
        self.name = name                                                                                                        # two-letter name of the language
        self.path = path                                                                                                        # path to language master folder
        self.bigram_dict = bigram_dict                                                                                          # dictionary of all bigrams from a language
        self.bigram_list = bigram_list                                                                                          # a sorted list of tuples containing bigrams and their number of appearances
        self.bigram_num = bigram_num                                                                                            # number of appearances of all bigrams
    
    def sort_bigrams(self):                                                                                                     # converts the bigram dictionary into a sorted list and calculates the number of appearance of all bigrams
        bigram_list = []                                                                                                        
        bigram_num = 0                                                                                                          
        for bigram_elem in self.bigram_dict:
            bigram_list.append(((bigram_elem), self.bigram_dict[bigram_elem]))
            bigram_num += self.bigram_dict[bigram_elem]

        self.bigram_list = sorted(sorted(bigram_list, key = lambda x: x[0]), key = lambda x: x[1], reverse = True)              # sorts the bigram list
        self.bigram_num = bigram_num



def calculate_probability(language_list, sequence_dict):                                                                        
    probability_list = []

    for language in language_list:
        sequence_prob = 1.0                                                                                                     # sequence probability given the language
        for bigram in sequence_dict:
            if bigram not in language.bigram_dict:
                sequence_prob = 0
                break
            else:
                sequence_prob *= (language.bigram_dict[bigram] / language.bigram_num) ** (sequence_dict[bigram])
        probability_list.append(sequence_prob)

    probability_sum = sum(probability_list)                                                                                     # normalizes the probabilities for each language
    for i in range (0, len(probability_list)):
        if probability_sum > 0:                                                                                                 # avoids division by zero
            probability_list[i] /= probability_sum

    return probability_list




def process_line(bigram_dict, line):                                                                                            # updates the input bigram dictionary with bigrams from the input line
    line = line.rstrip('\n').rstrip('\r').rstrip('\ufeff').lower()                                                              # removes unwanted characters and turns the line lowercase 
    for i in range(0, len(line) - 1):
        bigram = line[i] + line[i + 1]
        if bigram in bigram_dict:
            bigram_dict[bigram] += 1
        else:
            bigram_dict[bigram] = 1
    return bigram_dict    



def process_file(bigram_dict, path):                                                                                            # updates the input bigram dictionary with bigrams from the input file
    f = open(path, "r", encoding="utf8")
    lines = f.readlines()
    for line in lines:
        process_line(bigram_dict, line)
    return bigram_dict



if __name__ == "__main__":
    corpus_path = input()
    sequences_path = input()                                                                                                    

    language_name_list = next(os.walk(corpus_path))[1]                                                                          # reads the two-letter name for each language
    language_list = []
    for name in language_name_list:
        language_list.append(language(name, os.path.join(corpus_path, name), {}))

    for directory_name, subdirectory_list, file_list in os.walk(corpus_path):                                                   # finds all files under from a single language and process them
        for language in language_list:
            if language.path in directory_name:
                for fname in file_list:
                    path = os.path.join(directory_name, fname)
                    language.bigram_dict = process_file(language.bigram_dict, path)
        
    for language in language_list:                                                                                              # outputs top 5 bigrams for each language
        language.sort_bigrams()
        for i in range(0, min(5, len(language.bigram_list))):
            print(language.name, end = ",")
            print(language.bigram_list[i][0], end = ",")
            print(language.bigram_num, end = ",")
            print(language.bigram_list[i][1])

    sequences_file = open(sequences_path, "r", encoding="utf8")                                                                 # reads the sequences
    sequence_list = sequences_file.readlines()                                                                                  # splits the sequences into a list    

    for sequence in sequence_list:                                                                                              # iterates through the sequences and prints the probabilities
        sequence_dict = process_line({}, sequence)
        probability_list = calculate_probability(language_list, sequence_dict)
        for i in range(0, len(probability_list)):
            print(language_list[i].name, end = ",")
            print(probability_list[i])

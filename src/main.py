import sys
import os
import re
import unicodedata
import json
import shutil


# Colors class for pretty print
class bcolors:
    BLUE  = '\033[94m'
    GREEN = '\033[92m'
    RED   = '\033[91m'
    GOLD  = '\033[93m'
    ENDC  = '\033[0m'

# Function that returns the stop word list giving a path file
def file_to_stop_word_list(path):
    stop_word_list = []
    with open(path) as f:
        for line in f.readlines():
            stop_word_list.append(line.strip())
    return stop_word_list

# Function that removes non-significant word from a word_list
def remove_stop_word(word_list, stop_word_list):
    stop_word_set = set(stop_word_list)
    word_list = [x for x in word_list if x not in stop_word_set]

    return word_list

# Function that calculates the n-grams of a giving word list
def n_gram(text, n):
    if n == 1:
        return text
    else:
        output = []
        for i in range(len(text) - n + 1):
            output.append(text[i:i + n])
        output = [' '.join(x) for x in output]
        return output

# Function that parses a file giving a path and return list of line
def parse_file(path):
    content = ""
    try:
        with open(path) as f:
            for line in f.readlines():
                content += line
        return content
    except:
        return "-1"

# Function that normalizes a word
def normalizer(word):
    # Normalizing accent
    word = ''.join(c for c in unicodedata.normalize('NFD', word) if unicodedata.category(c) != 'Mn')
    # Lowercasing
    word = word.lower()
    return word

# Function that cleans text and return a list of word from a giving text
def text_to_word(text):
    # Retrieve special char and split text to word
    word_list = re.sub("[^\w]", " ", text).split()

    word_list = [normalizer(word) for word in word_list]

    return word_list

# Function that merges n-grams and return the resulting n-gram
def n_grams_merge(n_grams):
    big_n_gram = set()
    for n_gram in n_grams:
        big_n_gram |= n_gram
    
    return big_n_gram

# Function that writes data (json) to path file
def save_data_on_disk(data, path):
    with open(path, 'w') as f:
        json.dump(list(data), f)

# Function that calculates the jaccard distance
# def by J(A, B) = |A n B| / |A u B|
def jaccard_dist(set1, set2):
    return float(len(set1 & set2)) / len(set1 | set2)

# Function that produces big n-grams from the train dataset and save on result folder
def parse_train_dataset(stop_word_list):
    # Actualize results/
    if os.path.exists("./results/n-grams/"):
        shutil.rmtree("./results/n-grams/")
    os.makedirs("./results/n-grams/")
    
    # Browse topics from dataset train resources
    dataset_train_path = "./resources/topics-dataset-train/"
    topics_list = []
    number_files = 0    
    for root, dirs, files in os.walk(dataset_train_path):
        for topic_name in dirs:
            
            # Get topic list
            topics_list.append(topic_name)

            # Get big n-gram from an entire topic folder
            n_grams = []
            topic_folder_path = dataset_train_path + topic_name + "/"
            print(bcolors.GREEN + "\nGetting big-n-gram from " + bcolors.GOLD + "{}".format(topic_name)
                  + bcolors.GREEN + " topic" + bcolors.ENDC)

            # Browse files from topics                       
            print("\t-> parsing files from current topic")
            for root, dirs, files in os.walk(topic_folder_path):
                for filename in files:

                    # Parse a text file
                    text_file_path = topic_folder_path + filename
                    current_n_gram = path_to_ngram(text_file_path, stop_word_list)

                    if current_n_gram == -1:
                        pass
                    else:
                        number_files += 1
                        # Add current n_gram
                        n_grams.append(set(current_n_gram))

            # Merge all the n-grams from current topic
            print("\t-> merging n-grams")
            big_n_gram = n_grams_merge(n_grams)

            # Save it on results folder
            print("\t-> save big n-gram into results folder")
            results_path = "./results/n-grams/" + topic_name + ".n-gram.json"
            save_data_on_disk(big_n_gram, results_path)
    
    # Save topics list on resources/
    print(bcolors.GREEN + "\nSave topics list on disk" + bcolors.ENDC)
    print("\t-> {} files has been treated\n".format(number_files))
    save_data_on_disk(topics_list, "./results/topics.json")

# Function that get list of n-grams from json file from results folder
def json_to_ngram(path):
    n_grams_list = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            json_file_path = path + filename

            with open(json_file_path) as f:
                data = json.load(f)
                n_gram = set(data)
                n_grams_list.append(n_gram)
    return n_grams_list

# Function that get the n-gram giving a path file
def path_to_ngram(path, stop_word_list):
    # Parse text file
    lines_list = parse_file(path)
    if (lines_list == "-1"):
        return -1
    word_list = text_to_word(lines_list)

    # Remove stop word
    word_list = remove_stop_word(word_list, stop_word_list)

    # Get n_gram
    current_n_gram = n_gram(word_list, 2)

    return current_n_gram

# Function that give the topic of a text giving a text path
def text_path_to_topic_categorization(test_text_path, stop_word_list, n_grams_list, topics_list):
    # Get n-gram from path
    current_n_gram = path_to_ngram(test_text_path, stop_word_list)

    if current_n_gram == -1:
        #sys.exit("\nThis file can't be parsed\n")
        return -1
    else:
        # Calculate the distance for all topics train
        dist_list = []
        current_n_gram = set(current_n_gram)
        for res_n_gram in n_grams_list:
            # Calculate jaccard distance
            dist = jaccard_dist(current_n_gram, res_n_gram)
            dist_list.append(dist)
    
        # Get the index of the max value
        max_index = dist_list.index(max(dist_list))
        
        # Detect the best topic
        detected_topic = topics_list[max_index]

        return detected_topic

def main():
    print("\n=========================")
    print("    Texts" + bcolors.GOLD + " Categorizer " + bcolors.ENDC)
    print("=========================")

    # Parsing option
    if len(sys.argv) != 2 or sys.argv[1] not in ["-train", "-test"]:
        if len(sys.argv) != 2:
            print(bcolors.RED + "\nError: too many or too few argument." + bcolors.ENDC)  
        else:
            print(bcolors.RED + "\nError: bad argument." + bcolors.ENDC)

        print("\nPlease enter one of these following options:")
        print(bcolors.BLUE + "\t-train" + bcolors.ENDC + "\t train the program using resources/topics-dataset-train/")
        print(bcolors.BLUE + "\t-test" + bcolors.ENDC + "\t launch the topic recognizer\n") 
        quit(1)

    # Parse stop word file
    print(bcolors.GREEN + "\nGetting stop words" + bcolors.ENDC)
    path_stop_word = "./resources/stop-words"
    stop_word_list = file_to_stop_word_list(path_stop_word)

    # Train
    if sys.argv[1] == "-train":
        # Get big n-gram from data-set train and save on disk
        parse_train_dataset(stop_word_list)

    # Test
    elif sys.argv[1] == "-test":
        
        # Get n-grams from results/n-grams/
        print(bcolors.GREEN + "Getting trained n-grams" + bcolors.ENDC)
        res_path = "./results/n-grams/"
        n_grams_list = json_to_ngram(res_path)

        # Get the topics list from results/topics.json
        print(bcolors.GREEN + "Getting topics list" + bcolors.ENDC)        
        topics_list = []
        with open("./results/topics.json") as f:
            topics_list = json.load(f)

        # Parsing option -file or -dataset
        print("\nWhich option do you want?")
        print(bcolors.BLUE + "\t-file" + bcolors.ENDC + "\t\tlaunch categorization for a single file")
        print(bcolors.BLUE + "\t-dataset"+ bcolors.ENDC + "\tlaunch categorization for an entire dataset")
        option = input("\n> ")

        if option in ["file", "-file"]:
            # Get text path from user
            print("\nPlease enter path to your file:")
            print("(ex: ./resources/topics-dataset-test/alt.atheism/53068)")
            test_text_path = input("\n> ")

            # Get the topic of a giving path text
            detected_topic = text_path_to_topic_categorization(test_text_path, stop_word_list, n_grams_list, topics_list)
            if detected_topic == -1:
                sys.exit("\nThis file can't be parsed\n")

            print("\nText Categorizer detects that the topic of this text is " + bcolors.GOLD 
                + "{}".format(detected_topic) + bcolors.ENDC + ".\n")
        
        elif option in ["dataset", "-dataset"]:
            # Get dataset path from user
            print("\nPlease enter path to your dataset:")
            print("(ex: ./resources/topics-dataset-test/)")
            dataset_path = input("\n> ")
            
            # Browse topics from dataset
            dataset_res = []
            nb_files_tot = []
            for root, dirs, files in os.walk(dataset_path):
                for topic_name in dirs:
                    topic_folder_path = dataset_path + topic_name + "/"

                    # Browse files from topics                      
                    print("\t-> parsing files from topic " + bcolors.GOLD + topic_name + bcolors.ENDC)
                    nb_files = 0
                    nb_success = 0
                    for root, dirs, files in os.walk(topic_folder_path):
                        for filename in files:
                            text_file_path = topic_folder_path + filename

                            # Get the topic of a giving path text
                            detected_topic = text_path_to_topic_categorization(text_file_path, stop_word_list, n_grams_list, topics_list)

                            if detected_topic == -1:
                                pass
                            else:
                                nb_files += 1
                                if detected_topic == topic_name:
                                    nb_success += 1
                    
                    success_rate = nb_success / nb_files
                    dataset_res.append(round(success_rate * 100, 2))
                    nb_files_tot.append(nb_files)

            for topic, res, nb_file in zip(topics_list, dataset_res, nb_files_tot):
                print("Rate of " + bcolors.BLUE + "{}%".format(res) + bcolors.ENDC + " with \t" + bcolors.BLUE
                      + "{} ".format(nb_file) + bcolors.ENDC + "files tested on topic " + bcolors.GOLD + "{}".format(topic) + bcolors.ENDC)
    
            print("\nTotal number of files tested: " + bcolors.BLUE + "{}".format(sum(nb_files_tot)) + bcolors.ENDC + ".")
            total_success_rate = round(sum(dataset_res) / len(dataset_res), 2)
            hazard_success_rate = round(1 / len(topics_list) * 100, 2)
            print("Total rate of success: " + bcolors.BLUE + "{}".format(total_success_rate) + bcolors.ENDC + "%.")
            print("Success rate with hazard: " + bcolors.BLUE + "{}".format(hazard_success_rate) + bcolors.ENDC + "%.\n")

        else:
            print(bcolors.RED + "\nError: bad argument.\n" + bcolors.ENDC)
            quit(1)


if __name__ == "__main__":
    main()

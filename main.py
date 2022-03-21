import random
import threading
import math

available_words = [i[:-1] for i in open("words.txt", "r").readlines()]  #list of all possible answers
wordsAllowed = [i[:-1] for i in open("wordsAllowed.txt", "r").readlines()]  #list of all possible entries

def get_letter_dictionary(word_list):   #gets a letter dictionary of the each letter and the number of times it appears in the word list
    letter_dictionary = {}
    for letter in "abcdefghijklmnopqrstuvwxyz":
        letter_dictionary.update({letter:0})
    for word in word_list:
        for letter in word:
            letter_dictionary.update({letter:(letter_dictionary[letter] + 1)})
    return letter_dictionary

def game_data_avg(game_data):   #returns average steps to complete a game
    try:
        return (game_data["1"] + 2 * game_data["2"] + 3 * game_data["3"] + 4 * game_data["4"] + 5 * game_data["5"] + 6 * game_data["0"]) / (game_data["1"] + game_data["2"] + game_data["3"] + game_data["4"] + game_data["5"] + game_data["0"])
    except:
        return 0

def repetition_filter(char, num_repetitions, wordList, exact):  #filters out words with incorrect number of character repetitions
    if exact:
        for word in wordList:
            if word.count(char) != num_repetitions:
                wordList.remove(word)
    else:
        for word in wordList:
            if word.count(char) < num_repetitions:
                wordList.remove(word)
    return wordList

def filter_words(return_list, guess, answer):   #returns a list of possible words left, given a guess and an answer
    for int in range(len(answer)):
        if guess[int] == answer[int]:   #filters words with correct letter at specific location
            # print(guess[int], "at specific location")
            return_list = filter(guess[int], position=(int), wordList=return_list)
        elif guess[int] in answer:    #filters words with correct letter present
            # print(guess[int], "in word")
            return_list = filter(guess[int], wordList=return_list)   
            return_list = wrongPositionFilter(guess[int], int, wordList=return_list) 
        elif guess[int] not in answer:  #filters out words with invalid letter in word
            # print(guess[int], "not in word")
            return_list = inverseFilter(filterChar=guess[int], wordList=return_list)
    for char in guess:
        if not guess.count(char) > 1 or not answer.count(char) > 1:
            continue
        if guess.count(char) <= answer.count(char): # "beers" "peees"
            return_list = repetition_filter(char, guess.count(char), return_list, False)  # we know the answer has at least guess.count(char) characters
        else: # guess count > answer count
            return_list = repetition_filter(char, answer.count(char), return_list, True) # answer count has the exact correct occurences of char
    return return_list

def filter(filterChar, position="any", repetitions="any", wordList="none"): #general purpose filter, covers correct letters, repetitions, and letters present
    returnList = []
    if type(position) == int:
        if position < 0 or position > 4:
            raise RuntimeError("InvalidCharacterPosition")
    if wordList == "none":
        available_words = open("words.txt", "r")
        wordList = [word for word in available_words]
        available_words.close()
    for word in wordList:
        if position != "any":
            if word[position] == filterChar:
                if word.count(filterChar) == repetitions or repetitions == "any":
                    returnList.append(word)
        elif repetitions != "any":
            if filterChar in word and word.count(filterChar) == repetitions:
                returnList.append(word)
        else:
            if filterChar in word:
                returnList.append(word)
    return returnList

def inverseFilter(filterChar, wordList="none"): #returns a list of words that do NOT contain the filter character
    returnList = []
    if wordList == "none":
        file = open("words.txt", "r")
        wordList = [line for line in file]
        file.close()
    for word in wordList:
        if filterChar not in word:
            returnList.append(word)
    return returnList

def wrongPositionFilter(filterChar, index, wordList="none"):    #returns a list of words that do not have the filter character at the specified index
    returnList = []
    if wordList == "none":
        file = open("words.txt", "r")
        wordList = [line for line in file]
        file.close()
    for word in wordList:
        if filterChar != word[index]:
            returnList.append(word)
    return returnList

def word_state_repetition_filter(word, wordState, word_list):  #filters out words with incorrect number of character repetitions using a word state
    # 1 identify repetitions in word
    repeatedChars = {i: word.count(i) for i in list(set(word)) if word.count(i) > 1}
    charRepetitions = {i: 0 for i in repeatedChars.keys()}
    for char in repeatedChars.keys():
        for i in range(5):
            if word[i] == char and wordState[i] != "0":
                repeatedChars[char] -= 1
                charRepetitions[char] += 1
    for char in repeatedChars.keys():
        word_list = repetition_filter(char, charRepetitions[char], word_list, repeatedChars[char] != 0)
    return word_list

def get_word_value(word, letter_dictionary, counted_word=""):   #gets the word value based off of the frequency of the letters in the letter dictionary
    value = 0
    counted_letters = [letter for letter in counted_word]
    for letter in word:
        if letter not in counted_letters:
            value += letter_dictionary[letter]
            counted_letters.append(letter)
    return value

def isBlimp(wordList):   #returns whether or not a word list has the "blimp problem"
    if len(wordList) > 10 or len(wordList) < 3:
        return False
    threshold = math.floor(len(wordList)/2)
    commonLettersDict = {}
    for word1 in wordList:
        for word2 in wordList:
            if word2 == word1:
                continue
            if len(list(set(word1) & set(word2))) >= 3: # if words have at least 3 letters in common
                commonLetters = ""
                for letters in list(set(word1) & set(word2)):
                    commonLetters += letters
                commonLetters = "".join(sorted(commonLetters))
                try:
                    commonLettersDict[commonLetters] += 1
                    if commonLettersDict[commonLetters] >= threshold:
                        return True
                except:
                    commonLettersDict[commonLetters] = 1
    return False

def getBlimpMax(wordList, commonLetters, totalWords=wordsAllowed): #returns highest word by letter frequency, excluding letters in common with most possible answers
    letterDictionary = get_letter_dictionary(wordList)
    wordValues = {word:get_word_value(word, letterDictionary, commonLetters) for word in totalWords}
    return max(wordValues, key=wordValues.get)

def blimpSearch(wordList):  #made to avoid the "blimp problem" where a search would be narrowed down best by a word already filtered out
    threshold = math.floor(len(wordList)/2) # ex: match, batch, latch are possible answers, blimp would be a good filter word
    commonLettersDict = {}
    blimpWords = {}
    for word1 in wordList:
        for word2 in wordList:
            if word2 == word1:
                continue
            if len(list(set(word1) & set(word2))) >= 3: # if words have at least 3 letters in common
                commonLetters = ""
                for letters in list(set(word1) & set(word2)):
                    commonLetters += letters
                commonLetters = "".join(sorted(commonLetters))
                try:
                    commonLettersDict[commonLetters] += 1
                except:
                    commonLettersDict[commonLetters] = 1
    for commonLetters in commonLettersDict:
        if commonLettersDict[commonLetters] >= threshold:
            blimpWord = getBlimpMax(wordList, commonLetters)
            blimpWords.update({blimpWord: get_word_value(blimpWord, get_letter_dictionary(wordList), commonLetters)})
    return max(blimpWords, key=blimpWords.get)

def getMaxValue1(wordList): #returns highest word by letter frequency
    letterDictionary = get_letter_dictionary(wordList)
    wordValues = {word:get_word_value(word, letterDictionary) for word in wordList}
    return max(wordValues, key=wordValues.get)

def gameFilter(word, wordState, word_list):   #filters words using game output information
    first_letter = int(wordState[0])
    second_letter = int(wordState[1])
    third_letter = int(wordState[2])
    fourth_letter = int(wordState[3])
    fifth_letter = int(wordState[4])
    lettersInWord = [word[i] for i in range(0, 5) if wordState[i] == "1" or wordState[i] == "2"]
    if first_letter == 0:
        if word[0] not in lettersInWord:
            word_list = inverseFilter(word[0], word_list)
    elif first_letter == 1:
        word_list = filter(word[0], wordList=word_list)
        word_list = wrongPositionFilter(word[0], 0, word_list)
    elif first_letter == 2:
        word_list = filter(word[0], position=0, wordList=word_list)
    if second_letter == 0:
        if word[1] not in lettersInWord:
            word_list = inverseFilter(word[1], word_list)
    elif second_letter == 1:
        word_list = filter(word[1], wordList=word_list)
        word_list = wrongPositionFilter(word[1], 1, word_list)
    elif second_letter == 2:
        word_list = filter(word[1], position=1, wordList=word_list)
    if third_letter == 0:
        if word[2] not in lettersInWord:
            word_list = inverseFilter(word[2], word_list)
    elif third_letter == 1:
        word_list = filter(word[2], wordList=word_list)
        word_list = wrongPositionFilter(word[2], 2, word_list)
    elif third_letter == 2:
        word_list = filter(word[2], position=2, wordList=word_list)
    if fourth_letter == 0:
        if word[3] not in lettersInWord:
            word_list = inverseFilter(word[3], word_list)
    elif fourth_letter == 1:
        word_list = filter(word[3], wordList=word_list)
        word_list = wrongPositionFilter(word[3], 3, word_list)
    elif fourth_letter == 2:
        word_list = filter(word[3], position=3, wordList=word_list)
    if fifth_letter == 0:
        if word[4] not in lettersInWord:
            word_list = inverseFilter(word[4], word_list)
    elif fifth_letter == 1:
        word_list = filter(word[4], wordList=word_list)
        word_list = wrongPositionFilter(word[4], 4, word_list)
    elif fifth_letter == 2:
        word_list = filter(word[4], position=4, wordList=word_list)
    if len(set(list(word))) != len(word):
        word_list = word_state_repetition_filter(word, wordState, word_list)
    return word_list

def validState(wordState):  #returns whether or not a word state is valid
    if len(wordState) != 5:
        return False
    else:
        try:
            for char in wordState:
                if int(char) < 0 or int(char) > 2:
                    return False
        except:
            return False
    return True

def allComplete(wordLists): #returns whether or not all lists are narrowed down to their answers
    for wordList in wordLists:
        if len(wordList) != 1:
            return False
    return True

def listComplete(list): #returns whether or not a list is narrowed down to its answer
    if len(list) == 1:
        return True
    else:
        return False

def getShortestList(wordLists): #returns the shortest list with at least 2 possible words
    lists = []
    for i in range(8):
        if listComplete(wordLists[i]):
            continue
        else:
            lists.append(wordLists[i])
    minimum = 9999
    minList = []
    for i in range(len(lists)):
        if len(lists[i]) < minimum and len(lists[i]) > 1:
            minimum = len(lists[i])
            minList = lists[i]
    return minList

def test_highestFrequency8(n):   #tests search using letter frequencies
    game_data = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0, "0": 0, "DNF": 0}
    for i in range(n):
        wordLists = [[i[:-1] for i in open("words.txt", "r").readlines()] for j in range(8)]
        test_words = []
        while len(test_words) < 8:
            test_word = random.choice(wordLists[0])
            if test_word not in test_words:
                test_words.append(test_word)
        for i in range(8):
            wordLists[i] = filter_words(wordLists[i], "acnes", test_words[i])
        for i in range(8):
            wordLists[i] = filter_words(wordLists[i], "lirot", test_words[i])
        steps = 0
        while steps < 6:
            if allComplete(wordLists):
                break
            wordList = getShortestList(wordLists)
            if isBlimp(wordList):
                inputWord = blimpSearch(wordList)
            else:
                inputWord = getMaxValue1(wordList)
            for i in range(8):
                if listComplete(wordLists[i]):
                    continue
                wordLists[i] = filter_words(wordLists[i], inputWord, test_words[i])
                if listComplete(wordLists[i]):
                    for j in range(8):
                        if listComplete(wordLists[j]):
                            continue
                        wordLists[j] = filter_words(wordLists[j], wordLists[i][0], test_words[j])
            steps += 1
        steps += 8
        if steps == 8:
            game_data.update({"5": game_data["5"] + 1})
        elif steps == 9:
            game_data.update({"4": game_data["4"] + 1})
        elif steps == 10:
            game_data.update({"3": game_data["3"] + 1})
        elif steps == 11:
            game_data.update({"2": game_data["2"] + 1})
        elif steps == 12:
            game_data.update({"1": game_data["1"] + 1})
        elif steps == 13:
            game_data.update({"0": game_data["0"] + 1})
        else:
            game_data.update({"DNF": game_data["DNF"] + 1})
        success_rate = 1 - (game_data["DNF"] / (game_data["1"] + game_data["2"] + game_data["3"] + game_data["4"] + game_data["5"] + game_data["0"] + game_data["DNF"]))
        print("highest_freq8", (game_data["1"] + game_data["2"] + game_data["3"] + game_data["4"] + game_data["5"] + game_data["0"] + game_data["DNF"]), game_data, success_rate, game_data_avg(game_data))
            
# test_highestFrequency8(1000)
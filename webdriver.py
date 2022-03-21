import main as gameEngine
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

def keyboardIn(string):
    keyBoardLocation = "document.getElementById('keyboard').children[0]"
    for letter in string:
        if letter in "qwertyuiop":
            driver.execute_script(keyBoardLocation + ".children[0]" + ".children[" + str("qwertyuiop".index(letter)) + "].click()")
        elif letter in "asdfghjkl":
            driver.execute_script(keyBoardLocation + ".children[1]" + ".children[" + str("asdfghjkl".index(letter)) + "].click()")
        else:
            driver.execute_script(keyBoardLocation + ".children[2]" + ".children[" + str("zxcvbnm".index(letter) + 1) + "].click()")
    driver.execute_script(keyBoardLocation + ".children[2]" + ".children[8].click()")

def getWordState(colIndex, rowIndex):
    wordState = ""
    for int in range(5):
        letterColor = driver.execute_script('return document.getElementById("widescreen-container").children[0].children[' + str(colIndex) + '].children[0].children[0].children[' + str(rowIndex) + '].children[' + str(int) + '].getAttribute("style")')
        if letterColor == 'color: white; background-color: rgb(24, 26, 27);':
            wordState += "0"
        elif letterColor == 'color: black; background-color: rgb(255, 204, 0);':
            wordState += "1"
        else:
            wordState += "2"
    return wordState

def colComplete(colIndex):
    for i in range(13):
        if getWordState(colIndex, i) == "22222":
            return True
    return False

def allComplete():
    for i in range(8):
        if not colComplete(i):
            return False
    return True

def getShortestListAbove2():
    lists = []
    for i in range(8):
        if colComplete(i):
            continue
        else:
            lists.append(wordLists[i])
    minimum = 9999
    minList = []
    for i in range(len(lists)):
        if len(lists[i]) < minimum and len(lists[i]) > 2:
            minimum = len(lists[i])
            minList = lists[i]
    return minList

def getShortestList():
    lists = []
    for i in range(8):
        if colComplete(i):
            continue
        else:
            lists.append(wordLists[i])
    minimum = 9999
    minList = []
    for i in range(len(lists)):
        if len(lists[i]) < minimum and len(lists[i]) > 0:
            minimum = len(lists[i])
            minList = lists[i]
    return minList

def getLongestList(): #returns the longest list
    lists = []
    for i in range(8):
        if colComplete(i):
            continue
        else:
            lists.append(wordLists[i])
    maximum = 0
    maxList = []
    for i in range(len(lists)):
        if len(lists[i]) > maximum:
            maximum = len(lists[i])
            maxList = lists[i]
    return maxList

def runTurn(rowIndex):
    if rowIndex > 2:
        wordList = getShortestList()
    else:
        wordList = getLongestList()
    if rowIndex == 12:
        inputWord = gameEngine.getMaxValue1(wordList)
    else:
        if gameEngine.isBlimp(wordList):
            inputWord = gameEngine.blimpSearch(wordList)
        else:
            inputWord = gameEngine.getMaxValue1(wordList)
    keyboardIn(inputWord)
    for i in range(8):
        wordLists[i] = gameEngine.gameFilter(inputWord, getWordState(i, rowIndex), wordLists[i])
    
while(1):
    driver.get("https://octordle.com/?mode=free")
    driver.execute_script("document.getElementById('widescreen-yes').click()")
    wordLists = [[i[:-1] for i in open("words.txt", "r").readlines()] for j in range(8)]
    keyboardIn("salet")
    for i in range(8):
        wordLists[i] = gameEngine.gameFilter("salet", getWordState(i, 0), wordLists[i])
    # keyboardIn("lirot")
    # for i in range(8):
    #     wordLists[i] = gameEngine.gameFilter("lirot", getWordState(i, 1), wordLists[i])
    rowIndex = 1
    try:
        while not allComplete():
            runTurn(rowIndex)
            rowIndex += 1
    except:
        pass
    time.sleep(1)
    driver.execute_script("document.getElementById('reset_free').click()")
    driver.switch_to.alert.accept()
# OctordleBot
This AI currently has an accuracy of approximately 98.4% and an average steps-per-game of 10.62 (2.38 steps remaining) using the answer list (2315 words)-
<br>
![Accuracy](daa.JPG)
<br>
In the image above, the number of guesses remaining is shown in a dictionary (5: 0, 4: 48...).
The numbers following the dictionary is the accuracy (percent of games completed) and the average steps per completed game, respectively.
<br>
<br>
# How it Works
The AI makes the same first guess every game- "salet". This word is statistically one of the best words to pick.
<br><br>
Subsequent guesses are made by filtering the lists of possible words by removing the words that include letters that have already been guessed and selecting the remaining word with the greatest word score. The word score is given by the sum of each letter's frequency in the list of possible answers, not including repeated letters within the word. The AI chooses the column with the least possible answers to focus on for making a guess. If there is a case where a list is between 3 and 6 words and at least half of the words (rounded down) have at least 3 of the same letters in common, the AI will look at the full list and guess a word with the highest word score that excludes the letters in common (this is also referred to as a "blimp search" in the code). After a guess is made, the list of possible words is filtered based on the letters that are in the word and the letters that are in the correct position. The words that contain letters that are not in the word are removed.
<br><br>
A webdriver was also created using Selenium, which allows the user to open up wordle directly through the code and watch the AI play through the game.

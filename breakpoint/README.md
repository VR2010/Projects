# Project title: BREAKPOINT

#### Video Demo:

#### Description:

**BREAKPOINT** is a Hangman-inspired game that helps players learn common engineering terms and their definitions. I wanted to make learning these terms more interactive and enjoyable instead of making it feel like a traditional lesson or course.

The game contains 30 engineering-related terms, each with a short description. The player has six attempts to guess the hidden word. Each time the player makes an incorrect guess, another part of the bridge on the right begins to fall apart. If all six attempts are used, the entire bridge collapses.

## howtoplay.html

The `howtoplay.html` page can be accessed by clicking the **"How to Play"** button at the top of the home page. It explains how the game works and outlines the rules, allowing a player to understand the game without needing any prior knowledge.

I used an ordered list with nested ordered lists for the instructions. Originally, I had everything in one ordered list, but I changed the structure because some instructions were related to each other. Grouping them under larger points made the instructions easier to follow and gave the page a clearer structure.

At the bottom of the page, there is a **"Back to Game"** button that takes the player back to the main page.

## index.html

`index.html` is the main page of BREAKPOINT and contains most of the game's functionality. The page uses a `container` class with two main sections: `left` and `bridgehangman`. This separates the word-guessing part of the game from the bridge.

The `left` section contains several `div` elements, an `input`, and buttons. The **Attempts Left** display keeps track of how many attempts the player has remaining, with one attempt being removed after every incorrect guess.

Below this is the hidden word, represented by underscores corresponding to the length of the randomly selected engineering term. The word is randomly selected from an array containing 30 engineering terms.

The `input` element is used for entering guesses. I added several checks to prevent invalid input, such as: the player can only enter one character at a time, the character must be a standard English letter, and the player cannot enter a letter that has already been guessed.

The **Guess** button checks the player's input. If the letter appears in the word, it is revealed in the correct position or positions. If the letter is incorrect, it is added to the **Wrong Guesses** section and one attempt is removed.

The **Description** section is initially empty and is filled in once the player either guesses the word correctly or runs out of attempts. The **Result** section tells the player whether they won or lost. If they lose, the correct word is also displayed.

The JavaScript for the game is included at the bottom of `index.html` rather than in a separate JavaScript file. It handles the main game logic, including randomly selecting a word, validating and checking guesses, keeping track of attempts and wrong guesses, changing the bridge after each incorrect guess and more.

### The Bridge

The `bridgehangman` section contains an SVG illustration of a suspension bridge. I created the bridge using SVG lines, curves, rectangles, and grouped elements that could be reused across the different stages of the collapse.

The bridge gradually falls apart as the player makes incorrect guesses. Each mistake causes another section to collapse:

1. The left outer section of the deck falls.
2. The right outer section of the deck falls.
3. The left tower collapses.
4. The right tower collapses.
5. The center section of the deck falls.
6. The entire bridge collapses into rubble.

I originally placed the bridge underneath the word-guessing section. However, I decided to move it to the side because I wanted the player to be able to see the effect of each incorrect guess immediately. When the bridge was underneath the game interface, the first few stages of the collapse could only be seen after scrolling. Moving it to the side made the changes much more noticeable while playing.

### Restart

The **Restart** button is located at the top of the page beside the **How to Play** button. Clicking it resets the game to its starting state. It restores all six attempts, clears the previous guesses and result, enables the input and Guess button again, and randomly selects a new engineering term.

## styles.css

`styles.css` contains the styling used by both `index.html` and `howtoplay.html`.

It controls the overall appearance of the website, including the background, colors, buttons, input fields, layout, and other visual elements. I used CSS variables near the beginning of the file to keep the colors consistent throughout the website and make it easier to change the color scheme if needed.

The stylesheet also includes a responsive design section using a media query. This changes the layout when the screen becomes smaller, such as on a mobile phone. The word-guessing section and bridge switch from a side-by-side layout to a vertical layout, making the game easier to use on smaller screens.

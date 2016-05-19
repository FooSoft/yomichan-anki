# Yomichan #

A while ago I started working on an [Anki](http://ankisrs.net/) plugin in an attempt to solve various annoyances I
encountered when trying to read Japanese books on my computer. Yomichan is the result of my efforts and makes Japanese
sentence/vocabulary mining trivial. It can be used in conjunction with the [Yomichan extension for
Chrome](/projects/yomichan-chrome-ext) to further enhance your learning experience by enabling flash card creation
directly from the Chrome web browser.

## Motivation ##

The software I was using for mining up to now was [Rikaichan](http://www.polarcloud.com/rikaichan/). I'm sure most
people studying the Japanese language are familiar with this browser extension and probably have it installed in
Firefox. Although pretty amazing, this tool is bound to Firefox. Firefox is obviously not a book reader: it doesn't
behave well with large text files, doesn't remember where you last stopped reading, and most importantly there was no
integration with Anki. As such, adding new vocab to my Anki deck was annoying; I wanted to be able to do this with one
mouse click. After several hours of work, Yomichan could do this and much more.

## Installation ##

Yomichan can be downloaded from the its [Anki shared addon page](https://ankiweb.net/shared/info/934748696). There is an
automatic update checker included in the plugin that (unless you disabled it in options) will notify you when new
versions become available. Developers can also clone the [repository on
GitHub](https://github.com/FooSoft/yomichan-chrome-ext), assuming that they have [Git LFS](https://git-lfs.github.com/)
installed and have initialized the included submodules after pulling down the main project.

## Usage ##

1.  Make sure you are running the latest version of Anki.
2.  Open your vocab deck and note the fields that are used in your deck.

    [![Card layout dialog](img/layout-thumb.png)](img/layout.png)

3.  Launch Yomichan from the tools menu inside Anki.
4.  Open the text file you want and you will see its contents in the Yomichan.  Your layout and color scheme will look
    different because the screenshot shows my personal settings.

    [![Reader dialog](img/reader-thumb.png)](img/reader.png)

5.  To look up words hover your mouse over them while pressing the middle mouse button (usually this is your scroll
    wheel). You can also press and hold shift instead if you like (or your mouse has no center button).
6.  To set up your Anki deck for Yomichan select Preferences from the Edit menu and you should see a screen that looks
    like this:

    [![Preferences dialog](img/preferences-thumb.png)](img/preferences.png)

7.  Now you should add markers such as `{expression}`, `{reading}`, `{reading}` and `{sentence}` to specify how new
    cards should be created. Card fields will vary depending on your deck model. If you want to be able to use
    *AnkiConnect* via the [Yomichan extension for Chrome](/projects/yomichan-chrome-ext), tick the checkbox labeled
    *Enable AnkiConnect* as shown above.

8.  When you look up definitions you will have the option to create Anki cards for them with one click. You will see the
    icons for performing these actions next to each item. *Icons for actions which update your decks won't show up if
    Anki thinks you can't add a fact with those items*. This likely means that they would either be duplicates of
    existing cards in the deck or that Yomichan hasn't been properly set up for your deck model.

    [![Icons](img/icons-thumb.png)](img/icons.png)

    Here is what the icons mean (in order from left to right):
    *   Add term in Kana form even it can be written in Kanji (e.g. べんきょうか).
    *   Add term as it appears in the dictionary including Kanji (e.g. 勉強家).
    *   Copy the expression, reading and definition for the term to the clipboard.

### Shortcuts ###

By request, I've added several keyboard shortcuts which make Yomichan even easier to use:

| Shortcut                    | Command                                             |
|-----------------------------|-----------------------------------------------------|
| <kbd>Shift</kbd>            | Search under cursor                                 |
| <kbd>]</kbd>                | Move search cursor forwards                         |
| <kbd>[</kbd>                | Move search cursor backwards                        |
| <kbd>Shift + Ctrl + #</kbd> | Add current Kanji at index 0 - 9 to deck            |
| <kbd>Ctrl + #</kbd>         | Add current term at index  0 - 9 to deck            |
| <kbd>Alt + #</kbd>          | Add current term at index 0 - 9 to deck as Hiragana |

### AnkiConnect ###

AnkiConnect is a new and revolutionary feature which allows external applications to communicate with Yomichan, making
it possible to query decks and create new flash cards directly. When enabled, Yomichan will initialize a simple
[AJAX](https://en.wikipedia.org/wiki/Ajax_(programming)) server running on port `8765` (only connections from
`localhost` are accepted for security reasons) and begin accepting requests for Anki-related tasks. This functionality
was developed primarily to support interfacing with the [Yomichan extension for Chrome](/projects/yomichan-chrome-ext),
thus making it possible to create new cards directly from your web browser.

### Importing Vocabulary ###

Yomichan is capable of importing vocabulary lists from plain text files and the vocabulary deck database the [Amazon
Kindle](http://en.wikipedia.org/wiki/Kindle) automatically generates when you look up words in the built-in dictionary
(this file can be found as `/system/vocabulary/vocab.db`). Note that importing does not create flash cards
automatically, but rather outputs the contents of the file to the Vocabulary and Kanji panes so that you can add facts
the same way as when reading within Yomichan.

## License ##

GPL

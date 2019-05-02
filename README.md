# Open Source Battle Bot
I've released the code to hopefully give everyone an opportunity to more easily complete dokkan events.
If you want to add a feature you've made feel free to submit a pull request.

The bot is made quite straightforwardly:
The packet module handles the encryption of packet data as well as the authorisation.
There shouldn't be too much reason to add to this file beyond fixing bugs.
  
The commands module is where the bulk of the code will be written for adding new features.

The dokkan module is where the command line/UI will be implemented, and will call the functions in the commands module.

The decryptor module uses: https://github.com/bssthu/pysqlsimplecipher
Although it's slow I preferred this code over pysqlcipher simply because it's easier to package it for distribution without running into issues.

# ToDo (lacking from paid bot)

[x] Omega farm (doing everything)
[x] Finish zbattle
[] Daily logins
[] Report - DS + Transfer Codes
[] 'daily' to complete daily grind events
[] 'finishquest' to complete all quest stages + bossrush
[] 'quest' for bot to finish quest on chosen difficulty
[] 'zbattle' for bot to continue a Z-Battle given its ID
[] 'zstage' for bot to complete a Z-Battle stage given its ID
[] 'finishzbattle' for bot to finish all current zbattles
[] 'listzbattle' for bot to list current Z-Battle IDs
[] 'rankup' for bot to attempt to gain ranks given instructions
[] 'story' for bot to attempt all current story events
[] 'liststory' to list current story events
[] 'strike' for bot to attempt all current strike events
[] 'liststrike' to list current strike events
[] 'potential' for bot to attempt all current potential events
[] 'listpotential' to list current potential events
[] 'listgrowth' to list current growth & special events...
[] 'dokkan' for bot to attempt all current dokkan events
[] 'listdokkan' to list current potential events
[] 'listlr' to list current LR events
[] 'listsbr' to list current SBR events
[] 'listmedals' to list all obtained medals
[] 'sellmedals' to sell medals by ID
[] 'listitems' to list all items
[] 'herculepunch' to complete punch machine event.
[] 'bossrush' to complete all bossrush stages
[] 'dragonballs' to collect all dragonballs and make a wish
[] 'cards' to see cards
[] 'deck' to change team configurations
[] 'summon' to perform a multi-summon, given summon ID
[] 'singlesummon' to perform a single-summon, given summon ID
[] 'listsummons' to see current summons
[] 'kagi' to use kagi keys to complete stages
[] 'stones' to change whether or not to use stones on regular stages
[] 'sell' to sell all N and R rank cards that arent locked
[] 'baba' to exchange SR rank cards that arent locked
[] 'sellhercule' to sell all Hercule Statues that arent locked
[] 'refresh' to reauthenticate client that has been idle...
[] 'exit' to terminate
[] 'list' to print master list of stages



# Installation

You might need to use sudo before every pip3 command.

```
pip3 install six
pip3 install pyinstaller
pip3 install colorama
pip3 install orator
pip3 install pycryptodome
pip3 install pysimplegui 
pip3 install requests
```

Then go to folder where your dokkan.py file is and: python3 dokkan.py

Happy testing!
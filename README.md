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

# Download
https://github.com/FlashChaser/Open-Source-Battle-Bot/releases

# Installation

You might need to use `sudo` before every `pip` command.

```
pip install --user pyinstaller
pip install --user colorama
pip install --user pyCryptodome
pip install --user PySimpleGUI
pip install --user requests
```

• Windows:
<br>
in the folder you downloaded; double click the `Windows.bat` file.
<br>if you want to do it manually; open command prompt then follow the mac guide.

• Mac:
<br>
open terminal & move directory to where the bot folder is e.g. `Downloads`
<br>enter `cd ./Downloads/Open-Source-Battle-Bot-development/Open-Source-Battle-Bot-development`
<br>then `python dokkan.py`

Happy testing!

# Pull Requests
Very happy to merge pull requests.
Until I can develop some tests be careful to make sure that all new commands that you implement accurately support JP translation.

e.g Check that you read from the global database, and if the data doesn't exist, read from the jp database.

```python
try:
    config.Model.set_connection_resolver(config.db_glb)
    config.Quests.find_or_fail(int(stage_id))
except:
    config.Model.set_connection_resolver(config.db_jp)
    config.Quests.find_or_fail(int(stage_id))
```

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

# Installation

You might need to use sudo before every pip3 command.

```
pip3 install six
pip3 install pyinstaller
pip3 install colorama
pip3 install orator
pip3 install pycrypto - https://github.com/dlitz/pycrypto
pip3 install PySimpleGUI
pip3 install requests
```

Then go to folder where your dokkan.py file is and: python3 dokkan.py

Happy testing!

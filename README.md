# Open Source Battle Bot
I've released the code to hopefully give everyone an opportunity to more easily complete dokkan events.
If you want to add a feature you've made feel free to submit a pull request.

The bot is made quite straightforwardly:
The packet module handles the encryption of packet data as well as the authorisation.
There shouldn't be too much reason to add to this file beyond fixing bugs.
  
The commands module is where the bulk of the code will be written for adding new features.

The dokkan module is where the command line/UI/saves will be implemented, and will call the functions in the commands module.

The decryptor module uses: https://github.com/bssthu/pysqlsimplecipher
Although it's slow I preferred this code over pysqlcipher simply because it's easier to package it for distribution without running into issues.

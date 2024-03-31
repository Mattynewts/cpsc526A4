CPSC 526 Assignment 4

Group Members:
Ariya Luangamath
Matthew Newton

This assignment includes the implementation of the following python files:

ncbot.py
    - Implemented a bot that is able to connect to Ncat-broker servers as specified
    - Able to check and authenticate commands if the check passes
    - Implemented status, shutdown, attack, and move commands

nccontroller.py 
    - Implemented a bot controller that also connects to Ncat-broker servers similarly to ncbot.py above.
    - Calculates appropriate nonces and MACs for controlling every bot on the server
    - Allows bots some time to send their responses back
    - Implemented being able to send status, shutdown, attack, and move commands to the bots

ircbot.py
    - Implemented a bot that is able to connect to IRC servers as specified, connection sequence and actions are the same as the above ncbot.py
    - Generates a random nickname upon launching the bot
    - Has all the same functionality as ncbot.py, but is also able to connect to Ncat-broker servers

irccontroller.py
    - Implemented a bot controller that connects to IRC servers as specified, behaves almost identically to nccontroller.py
    - Allows bots some time to send their responses back

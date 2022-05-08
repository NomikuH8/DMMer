# DMMer
A Discord-like Twitter bot for DMs (sends output only once)

### How to setup:
1. In the developer portal, access your app's authentication and turn on OAuth 1.0a, check "Read and write and Direct message" in App permissions;
1. Download credentials.txt and change for your api key;
1. Download the commands.json;
1. Change the callback for the one its in your Twitter's dev portal;
1. Change the commands (command:output);
1. Change the wait-time if you want (not recommended, twitter has that rate limit thing);
1. The user can run the command only once, to reset this, run "python DMMer.py reset" or "DMMer.exe reset" if you downloaded the binary.
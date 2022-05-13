import datetime
import tweepy
import json
import time
import sys
import os

tmp_json = json.loads(open('commands.json', 'r').read())
COMMAND_NOT_FOUND_MSG = tmp_json['not-found']
WAIT_TIME = tmp_json['wait-time']
CALLBACK = tmp_json['callback']
DM_COUNT_TO_GET = tmp_json['dm-count-to-get']
JSON_PATH = 'command_usage.json'

# how i want new command_usage.json to look:
#   [
#     {
#       id: "1234567891234567891",
#       user: "000000000",
#       command: "!sayhi"
#     },
#     <same>
#   ]

def get_cred(credential: str):
    ''' Gets credentials '''
    cred_dict = json.loads(open('credentials.json', 'r').read())
    return cred_dict[credential]

def set_cred(credential: str, value):
    ''' Sets credentials (used for token login) '''
    cred_dict = json.loads(open('credentials.json', 'r').read())
    cred_dict[credential] = value
    open('credentials.json', 'w').write(json.dumps(cred_dict, indent=2))


def load_commands(json: dict):
    ''' Creates a command array '''
    commands = []
    prefix = json['prefix']
    for i in json['commands'].keys():
        commands.append(prefix + i)
    return commands

def get_output(json: dict, command: str):
    ''' Gets the output for command '''
    comm = command.replace('!', '')
    for i in json['commands'].keys():
        if comm == i:
            return json['commands'][i]
    return COMMAND_NOT_FOUND_MSG

def check_for_commands(commands, comm):
    ''' Check if command is in commands '''
    for i in commands:
        if i == comm:
            return get_output(json.loads(open('commands.json').read()), i)
    return COMMAND_NOT_FOUND_MSG

def authenticate():
    ''' Authenticates twitter api '''
    api_key = get_cred('api-key')
    api_key_secret = get_cred('api-key-secret')
    access_token = get_cred('access-token')
    access_token_secret = get_cred('access-token-secret')

    if access_token == '':
        auth = tweepy.OAuth1UserHandler(
            api_key,
            api_key_secret,
            callback=CALLBACK
        )
        print('Get the auth:')
        print(auth.get_authorization_url())
        oauth_verifier = input('Paste oauth_verifier here (its in the redirected url): ')
        access_token, access_token_secret = (
            auth.get_access_token(
                oauth_verifier
            )
        )

        set_cred('access-token', access_token)
        set_cred('access-token-secret', access_token_secret)

    access_token = get_cred('access-token')
    access_token_secret = get_cred('access-token-secret')

    new_auth = tweepy.OAuth1UserHandler(
        api_key,
        api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    return tweepy.API(new_auth)

def get_dms(api: tweepy.API, prefix: str):
    ''' Gets all dms and check for the ones with prefix '''
    screen_name = api.get_settings()['screen_name']
    usr_json = api.get_user(screen_name=screen_name)._json
    my_id = usr_json['id_str']
    my_dms = api.get_direct_messages(count=DM_COUNT_TO_GET)
    valid_dms = []
    dms = []
    for dm in my_dms:
        dms.append(dm.message_create)
        # if dm.message_create['sender_id'] != my_id:
        if dm.message_create['message_data']['text'][0] == prefix:
            valid_dms.append({
                'msg_id': dm._json['id'],
                'sender': dm.message_create['sender_id'],
                'command': dm.message_create['message_data']['text'].lower()
            })

    open('lastdms.json', 'w').write(json.dumps(dms, indent=2))
    return valid_dms

def send_dms(api: tweepy.API, dms: list, commands: list, prefix: str):
    ''' Sends dms for the get_dms return '''
    for i in dms:
        if is_id_in_command(i['msg_id']):
            continue
        add_id_to_command(i['msg_id'], i['sender'], i['command'])
        output = check_for_commands(commands, i['command'])
        api.send_direct_message(i['sender'], output)
        time.sleep(5)

def is_id_in_command(msg_id: str):
    ''' Checks if user is in command's command_usage.json '''
    if not os.path.exists(JSON_PATH):
        return False
    usage_json = json.loads(open(JSON_PATH, 'r').read())
    for i in usage_json:
        if msg_id == i['msg_id']:
            return True
    return False
        

def add_id_to_command(msg_id: str, user_id: str, command: str):
    ''' Adds id to command_usage.json, to prevent duplicated messages '''
    usage_json = []
    if os.path.exists(JSON_PATH):
        usage_json = json.loads(open(JSON_PATH, 'r').read())
    usage_json.reverse()
    usage_json.append({
        "msg_id": msg_id,
        "user_id": user_id,
        "command": command
    })
    usage_json.reverse()
    open(JSON_PATH, 'w').write(json.dumps(usage_json, indent=2))

def delete_json():
    try:
        os.remove(JSON_PATH)
        print('Removed command usage log!')
    except:
        print("Couldn't remove command usage log! (maybe it doesn't exist)")

def run_timer():
    times_ran = 0
    wait_time = WAIT_TIME
    api = authenticate()
    while True:
        try:
            run(api)
            times_ran += 1
            for i in range(wait_time):
                print(f'                        ; Times ran: {times_ran}', end='\r')
                print(f'Time until next run: {wait_time - i}', end='\r')
                time.sleep(1)
        except KeyboardInterrupt:
            print('Exitting DMMer!')
            sys.exit(0)

def run(api: tweepy.API):
    ''' runs the bot once '''
    command_json = json.loads(open('commands.json').read())
    commands = load_commands(command_json)
    prefix = command_json['prefix']

    dms = get_dms(api, prefix)
    dms.reverse()
    send_dms(api, dms, commands, prefix)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'reset':
        delete_json()
        sys.exit(0)

    run_timer()

import requests
import os
import platform

PARAMS = CMD = USERNAME = PASSWORD = API = TOKEN = ""
HOST = "127.0.0.1"
PORT = "1104"

def __postcr__():
    return "http://"+HOST+":"+PORT+"/"+CMD+"?"

def __getticket__():
    return "http://"+HOST+":"+PORT+"/"+CMD+"/"+TOKEN

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def userAppMenu(rJson):
    clear()
    subResponse = rJson['message']
    while (True):
        print('\t< User: %s >' % rJson['username'])
        print('\t< %s >' % subResponse)
        print('''1. List of tickets
2. Create a ticket
3. Close a ticket
4. Logout
        ''')
        subResponse = ''
        subOption = raw_input('input> ')

        if (subOption == '1'):
            clear()
            token = rJson['token']
            PARAMS = {'token': token
                        }
            
            global CMD
            CMD = 'usergettickets'
            r = requests.get(__postcr__(), PARAMS).json()
            
            if (r):
                for row in r:
                    print("ticket id> \t%s" % row['id'])
                    print("subject> \t%s" % row['subject'])
                    print("body> \t\t%s" % row['body'])
                    print("status> \t%s" % row['status'])

                    token = rJson['token']
                    PARAMS = {'token': token,
                                'id': row['id']
                                }
                    
                    global CMD
                    CMD = 'getresponses'
                    r2 = requests.get(__postcr__(), PARAMS).json()
                    
                    if (r2):
                        for row2 in r2:
                            print("\t| response id> \t%s" % row2['id'])
                            print("\t| body> \t%s" % row2['body'])
                            print('')

                    else:
                        print('\t| No responses')
                        print('')

                    print('')
                subResponse = 'Your tickets received successfully!'

            else:
                subResponse = 'You have no tickets!'

        elif (subOption == '2'):
            clear()
            in_subject = raw_input('subject> ')
            in_body = raw_input('body> ')
            token = rJson['token']
            PARAMS = {'token': token,
                        'subject': in_subject,
                        'body': in_body
                        }
            
            global CMD
            CMD = 'createticket'
            r = requests.post(__postcr__(), PARAMS).json()
            subResponse = r['message']

        elif (subOption == '3'):
            clear()
            in_id = raw_input('id> ')
            token = rJson['token']
            PARAMS = {'token': token,
                        'id': in_id,
                        }
            
            global CMD
            CMD = 'closeticket'
            r = requests.post(__postcr__(), PARAMS).json()
            subResponse = r['message']

        elif (subOption == '4'):
            in_username = rJson['username']
            token = rJson['token']
            PARAMS = {'username': in_username,
                        'token': token
                        }
            
            global CMD
            CMD = 'logout'
            r = requests.post(__postcr__(), PARAMS).json()
            if (r['code'] < 200):
                return r['message']
            else:
                subResponse = r['message']

        else:
            subResponse = 'Wrong input!'
            clear()

def adminAppMenu(rJson):
    clear()
    subResponse = rJson['message']
    while (True):
        print('\t< Admin: %s >' % rJson['username'])
        print('\t< %s >' % subResponse)
        print('''1. List of tickets
2. Response to a ticket
3. Change status of a ticket
4. Promote a user to admin
5. Logout
        ''')
        subResponse = ''
        subOption = raw_input('input> ')

        if (subOption == '1'):
            clear()
            token = rJson['token']
            PARAMS = {'token': token
                        }
            
            global CMD
            CMD = 'admingettickets'
            r = requests.get(__postcr__(), PARAMS).json()
            
            if (r):
                for row in r:
                    print("Ticket id> \t%s" % row['id'])
                    print("subject> \t%s" % row['subject'])
                    print("body> \t\t%s" % row['body'])
                    print("status> \t%s" % row['status'])

                    token = rJson['token']
                    PARAMS = {'token': token,
                                'id': row['id']
                                }
                    
                    global CMD
                    CMD = 'getresponses'
                    r2 = requests.get(__postcr__(), PARAMS).json()
                    
                    if (r2):
                        for row2 in r2:
                            print("\t| response id> \t%s" % row2['id'])
                            print("\t| body> \t%s" % row2['body'])
                            print('')

                    else:
                        print('\t| No responses')
                        print('')

                    print('')
                
                subResponse = 'All tickets received successfully!'

            else:
                subResponse = 'There is no tickets!'

        elif (subOption == '2'):
            clear()
            in_id = raw_input('id> ')
            in_body = raw_input('body> ')
            token = rJson['token']
            PARAMS = {'token': token,
                        'id': in_id,
                        'body': in_body,
                        }
            
            global CMD
            CMD = 'response'
            r = requests.post(__postcr__(), PARAMS).json()
            subResponse = r['message']

        elif (subOption == '3'):
            clear()
            in_id = raw_input('id> ')
            in_status = raw_input('status> ')
            token = rJson['token']
            PARAMS = {'token': token,
                        'id': in_id,
                        'status': in_status,
                        }
            
            global CMD
            CMD = 'changestatus'
            r = requests.post(__postcr__(), PARAMS).json()
            subResponse = r['message']

        elif (subOption == '4'):
            clear()
            in_username = raw_input('username> ')
            token = rJson['token']
            PARAMS = {'username': in_username,
                        'token': token
                        }
            
            global CMD
            CMD = 'promote'
            r = requests.post(__postcr__(), PARAMS).json()
            subResponse = r['message']

        elif (subOption == '5'):
            in_username = rJson['username']
            token = rJson['token']
            PARAMS = {'username': in_username,
                        'token': token
                        }
            
            global CMD
            CMD = 'logout'
            r = requests.post(__postcr__(), PARAMS).json()
            if (r['code'] < 200):
                return r['message']
            else:
                subResponse = r['message']

        else:
            subResponse = 'Wrong input!'
            clear()


clear()
lastResponse = 'Wellcome'
while (True):
    if (lastResponse != ''):
        print('\t< %s >' % lastResponse)
    print('''1. SignUp
2. Login
3. Exit
    ''')
    lastResponse = ''
    selectedOption = raw_input('input> ')

    # Sign up
    if (selectedOption == '1'):
        clear()
        in_username = raw_input('username> ')
        in_password = raw_input('password> ')
        in_firstname = raw_input('firstname> ')
        in_lastname = raw_input('lastname> ')

        PARAMS = {'username': in_username,
                    'password': in_password,
                    'firstname': in_firstname,
                    'lastname': in_lastname
                    }

        CMD = 'signup'
        r = requests.post(__postcr__(), PARAMS).json()
        lastResponse = r['message']

    # Login
    elif (selectedOption == '2'):
        clear()
        in_username = raw_input('username> ')
        in_password = raw_input('password> ')
        PARAMS = {'username': in_username, 'password': in_password}
        CMD = 'login'
        r = requests.post(__postcr__(), PARAMS).json()
        if (r['code'] > 199):
            lastResponse = r['message']

        else:
            if (r['mode'] == 'User'):
                lastResponse = userAppMenu(r)
            else:
                lastResponse = adminAppMenu(r)

    # Exit
    elif (selectedOption == '3'):
        exit()

    # Wrong input
    else:
        lastResponse = 'Wrong intput'

    clear()
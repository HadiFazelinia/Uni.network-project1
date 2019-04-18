import torndb
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import os
import json
from binascii import hexlify

define("port", default=1104, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="tickets", help="database name")
define("mysql_user", default="x", help="database user")
define("mysql_password", default="y", help="database password")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # Post
            (r"/signup", signup),
            (r"/login", login),
            (r"/logout", logout),
            (r"/promote", promoteToAdmin),
            (r"/createticket", createTicket),
            (r"/closeticket", closeTicket),
            (r"/changestatus", changeStatus),
            (r"/response", responseToTicket),
            # Get
            (r"/usergettickets", getTickets),
            (r"/admingettickets", getAllTickets),
            (r"/getresponses", getResponses),
            # Default
            (r".*", defaulthandler),
        ]
        settings = dict()
        super(Application, self).__init__(handlers, **settings)
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def check_user(self, username):
        res = self.db.get("select * from users where username = %s", username)
        if (res):
            return True
        else:
            return False

    def check_id(self, id):
        res = self.db.get("select * from tickets where id = %s", id)
        if (res):
            return True
        else:
            return False

    def check_user_acces(self, username, id):
        res = self.db.get("select * from tickets where id = %s and user = %s", id, username)
        if (res):
            return True
        else:
            return False

    def get_user_mode(self, username):
        res = self.db.get("select * from users where username = %s", username)
        if (res):
            return res['mode']
        else:
            return '(not found!)'

    def get_user_mode_with_token(self, token):
        res = self.db.get("select * from users where token = %s", token)
        if (res):
            return res['mode']
        else:
            return False

    def get_user_name(self, token):
        res = self.db.get("select * from users where token = %s", token)
        if (res):
            return res['username']
        else:
            return False

    def signup_user(self, username, password, firstname, lastname):
        res = self.db.get("select * from users where username = %s", username)
        if (res):
            return False
        else:
            self.db.execute("""
            insert into users
            (username, password, firstname, lastname, mode)
            values
            (%s, %s, %s, %s, %s);
            """, username, password, firstname, lastname, 'User')
            return True

    def login_user(self, username, password):
        res = self.db.get("select * from users where username = %s and password = %s", username, password)
        if (res):
            if (res['token'] == None):
                token = str(hexlify(os.urandom(16)))
                self.db.execute("update users set token = %s where username = %s", token, username)
                output = {'code': 101,'mode': res['mode'], 'token': token}
            else:
                output = {'code': 206,'mode': res['mode'], 'token': res['token']}
            return output
        else:
            return False

    def logout_user(self, username, token):
        res = self.db.get("select * from users where username = %s and token = %s", username, token)
        if (res):
            outRes = self.db.execute("update users set token=NULL where username = %s", username)
            return True
        else:
            return False

    def promote_to_admin(self, username):
        res = self.db.get("select * from users where username = %s", username)
        if (res['mode'] == 'Admin'):
            return False
        self.db.execute("update users set mode='Admin' where username = %s", username)
        return True

    def create_ticket(self, token, subject, body):
        username = self.get_user_name(token)
        res = self.db.execute("""
            insert into tickets
            (user, subject, body, status)
            values
            (%s, %s, %s, %s);
            """, username, subject, body, 'Open')
        return True

    def get_tickets(self, token):
        username = self.get_user_name(token)
        rows = self.db.query("select * from tickets where user = %s", username)
        output = json.dumps(rows)
        print(output)
        return output

    def get_all_tickets(self):
        rows = self.db.query("select * from tickets")
        output = json.dumps(rows)
        print(output)
        return output

    def get_responses(self, id):
        rows = self.db.query("select * from responses where ticketID = %s", id)
        output = json.dumps(rows)
        print(output)
        return output

    def close_ticket(self, username, id):
        res = self.db.get("select * from tickets where id = %s and user = %s", id, username)
        if (res):
            self.db.execute("update tickets set status = 'Closed' where id = %s", id)
            return True
        else:
            return False

    def set_ticket_status(self, id, status):
        self.db.execute("update tickets set status=%s where id=%s", status, id)
        return True

    def response_to_ticket(self, body, id):
        self.db.execute("""
            insert into responses
            (body, ticketID)
            values
            (%s, %s);
            """, body, id)
        return True

class signup(BaseHandler):
    def post(self):
        print('signup called...')

        in_username = self.get_argument('username')
        in_password = self.get_argument('password')
        in_firstname = self.get_argument('firstname', None)
        in_lastname = self.get_argument('lastname', None)

        res = self.signup_user(in_username, in_password, in_firstname, in_lastname)
        if(res == False):
            resjson = {'message': 'User exists!', 'code': 200}
            print('====')
            print('try signup %s, but it exists...' % in_username)
            print('====')
            self.write(resjson)

        else:
            resjson = {'message': 'User added successfully!', 'code': 100}
            print('====')
            print('user added successfully...')
            print('username: %s' % in_username)
            print('password: %s' % in_password)
            print('firstname: %s' % in_firstname)
            print('lastname: %s' % in_lastname)
            print('====')
            self.write(resjson)


class login(BaseHandler):
    def post(self):
        print('login called...')

        in_username = self.get_argument('username')
        in_password = self.get_argument('password')
        res = self.login_user(in_password, in_password)
        
        if(res):
            mode = res['mode']
            token = res['token']

            if (res['code'] == 101):
                resjson = {'message': 'Login successfully!', 'code': 101,
                            'username': in_username, 'mode': mode, 'token': token}

                print('====')
                print('user login successfully...')
                print('username: %s' % in_username)
                print('password: %s' % in_password)
                print('mode: %s' % mode)
                print('token: %s' % token)
                print('====')
                self.write(resjson)

            else:
                resjson = {'message': 'Already login!', 'code': 206}

                print('====')
                print('try login to a online user')
                print('username: %s' % in_username)
                print('====')
                self.write(resjson)

        else:
            resjson = {'message': 'Wrong password!', 'code': 201}
            print('====')
            print('try login as %s with wrong password...' % in_username)
            print('====')
            self.write(resjson)

class logout(BaseHandler):
    def post(self):
        print('logout called...')

        in_username = self.get_argument('username')
        in_token = self.get_argument('token')

        res = self.logout_user(in_username, in_token)
        
        if (res):
            mode = self.get_user_mode(in_username)
            message = '{} logout successfully!'
            message = message.format(mode)
            resjson = {'message': message, 'code': 102}
            print('====')
            print('%s...' % message)
            print('username: %s' % in_username)
            print('token: %s' % in_token)
            print('====')
            self.write(resjson)

        else:
            resjson = {'message': 'Wrong token or username!', 'code': 202}
            print('====')
            print('try logout as %s with wrong token...' % in_username)
            print('====')
            self.write(resjson)

class promoteToAdmin(BaseHandler):
    def post(self):
        print('promoteToAdmin called...')

        in_token = self.get_argument('token')
        in_username = self.get_argument('username')

        authorized = self.get_user_mode_with_token(in_token)
        res = self.promote_to_admin(in_username)
        if (authorized == 'Admin'):
            if (res):
                resjson = {'message': 'Promoted successfully!', 'code': 103}
                print('====')
                print('%s promoted to admin...' % in_username)
                print('====')
                self.write(resjson)    

            else:
                resjson = {'message': 'Already admin!', 'code': 203}
                print('====')
                print('try promote (admin: %s) to admin...' % in_username)
                print('====')
                self.write(resjson)    

        else:
                resjson = {'message': 'You are not authorized!', 'code': 204}
                print('====')
                print('%s tried to promote someone to admin...' % self.get_user_name(in_token))
                print('target: %s' % in_username)
                print('====')
                self.write(resjson)    

class createTicket(BaseHandler):
    def post(self):
        print('createTicket called...')

        in_token = self.get_argument('token')
        in_subject = self.get_argument('subject')
        in_body = self.get_argument('body')

        self.create_ticket(in_token, in_subject, in_body)
        resjson = {'message': 'Ticket send successfully!', 'code': 104}
        print('====')
        print('ticket added...')
        print('subject: %s' % in_subject)
        print('body: %s' % in_body)
        print('user: %s' % self.get_user_name(in_token))
        print('====')
        self.write(resjson)    

class getTickets(BaseHandler):
    def get(self):
        print('getTickets called...')

        in_token = self.get_argument('token')

        res = self.get_tickets(in_token)
        print('====')
        print('getticket request received...')
        print('user: %s' % self.get_user_name(in_token))
        print('====')
        self.write(res)    

class getResponses(BaseHandler):
    def get(self):
        print('getResponses called...')

        in_token = self.get_argument('token')
        in_id = self.get_argument('id')
        username = self.get_user_name(in_token)
        mode = self.get_user_mode_with_token(in_token)

        res = self.get_responses(in_id) 
        print('====')
        print('getresponses request received...')
        explain = '{} : %s' % username
        explain = explain.format(mode)
        print(explain)
        print('====')
        self.write(res) 

class getAllTickets(BaseHandler):
    def get(self):
        print('getAllTickets called...')

        in_token = self.get_argument('token')
        authorized = self.get_user_mode_with_token(in_token)

        if (authorized == 'Admin'):
            res = self.get_all_tickets() 
            print('====')
            print('getallticket request received...')
            print('admin: %s' % self.get_user_name(in_token))
            print('====')
            self.write(res) 

        else:
            resjson = {'message': 'You are not authorized!', 'code': 204}
            print('====')
            print('%s tried to get all tickets...' % self.get_user_name(in_token))
            print('====')
            self.write(resjson)

class closeTicket(BaseHandler):
    def post(self):
        print('closeTicket called...')

        in_token = self.get_argument('token')
        in_id = self.get_argument('id')
        username = self.get_user_name(in_token)

        res = self.close_ticket(username, in_id)
        if (res):
            resjson = {'message': 'Ticket closed successfully!', 'code': 106}
            print('====')
            print('ticket closed...')
            print('id: %s' % in_id)
            print('====')
            self.write(resjson)

        else:
            resjson = {'message': 'You are not authorized!', 'code': 204}
            print('====')
            print('%s tried to change status of a ticket...' % self.get_user_name(in_token))
            print('id: %s' % in_id)
            print('====')
            self.write(resjson)  

class changeStatus(BaseHandler):
    def post(self):
        print('changeStatus called...')

        in_token = self.get_argument('token')
        in_id = self.get_argument('id')
        in_status = self.get_argument('status')

        authorized = self.get_user_mode_with_token(in_token)

        if (authorized == 'Admin'):
            res = self.set_ticket_status(in_id, in_status)
            resjson = {'message': 'Status changed successfully!', 'code': 105}
            print('====')
            print('status changed...')
            print('id: %s' % in_id)
            print('admin: %s' % self.get_user_name(in_token))
            print('====')
            self.write(resjson) 

        else:
            resjson = {'message': 'You are not authorized!', 'code': 204}
            print('====')
            print('%s tried to change status of a ticket...' % self.get_user_name(in_token))
            print('====')
            self.write(resjson)   

class responseToTicket(BaseHandler):
    def post(self):
        print('responseToTicket called...')

        in_token = self.get_argument('token')
        in_id = self.get_argument('id')
        in_body = self.get_argument('body')

        authorized = self.get_user_mode_with_token(in_token)

        if (authorized == 'Admin'):
            exist = self.check_id(in_id)

            if (exist):
                res = self.response_to_ticket(in_body, in_id)
                resjson = {'message': 'Responsed successfully!', 'code': 107}
                print('====')
                print('a ticket responsed...')
                print('id: %s' % in_id)
                print('admin: %s' % self.get_user_name(in_token))
                print('====')
                self.write(resjson) 

            else:
                resjson = {'message': 'Ticket not found!', 'code': 205}
                print('====')
                print('%s tried to response non-existing ticket...' % self.get_user_name(in_token))
                print('id: %s' % in_id)
                print('====')
                self.write(resjson) 

        else:
            resjson = {'message': 'You are not authorized!', 'code': 204}
            print('====')
            print('%s tried to change status of a ticket...' % self.get_user_name(in_token))
            print('====')
            self.write(resjson)   

class defaulthandler(BaseHandler):
    def get(self):
        print('defaulthandler(get) called...')
        resjson = {'message': 'failed', 'code': 300}
        self.write(resjson)

    def post(self):
        print('defaulthandler(post) called...')
        resjson = {'message': 'failed', 'code': 301}
        self.write(resjson)

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
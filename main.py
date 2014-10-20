import cgi
import datetime
import urllib
import wsgiref.handlers
import os

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
import webapp2

class Person(db.Model):
    name = db.StringProperty()
    age = db.IntegerProperty()

class Index(object):
    title = "A Student Registration System"
    loginUrl = "login"
    loginText = "Login"
    registerUrl = "register"
    registerText = "Register"


class MainPage(webapp2.RequestHandler):
    def get(self):
        templateValues = {
            'title' : Index.title,
            'loginUrl' : Index.loginUrl,
            'loginText' : Index.loginText,
            'registerUrl' : Index.registerUrl,
            'registerText' : Index.registerText,
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, templateValues))

app = webapp2.WSGIApplication([
                               ('/', MainPage)
                               ], debug=True)


def main():
    application.run()


if __name__ == '__main__':
    main()
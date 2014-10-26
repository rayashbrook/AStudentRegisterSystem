import cgi
import datetime
import urllib
import wsgiref.handlers
import os

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.api import users
import webapp2

from ASRS import Subject
from ASRS import Course
from ASRS import CourseSubject

class Index(object):
    title = "A Student Registration System"
    loginUrl = "login"
    loginText = "Login"
    registerUrl = "register"
    nonFirstYear = "non-first-year"
    registerText = "First Year Register"

    adminUrl = "admin"
    manageCourseUrl = "add-course"
    addCourseText = "Add New Course"
    manageSubjectUrl = "add-subject"
    addSubjectText = "Add New Subject"
    manageCourseSubjectUrl = "course"
    addCourseSubjectUrl = "add-subject-to-course"

class ParentKeys():
    course = ndb.Key("Entity", "course_key")
    subject = ndb.Key("Entity", "subject_key")
    courseSubject = ndb.Key("Entity", "course_subject_key")

class MainPage(webapp2.RequestHandler):
    def get(self):
        templateValues = {
            'title' : Index.title,
            'loginUrl' : Index.loginUrl,
            'loginText' : Index.loginText,
            'registerUrl' : Index.registerUrl,
            'registerText' : Index.registerText,
        }

        path = os.path.join(os.path.dirname(__file__), 'html/index.html')
        self.response.out.write(template.render(path, templateValues))

class Login(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Login Page")

class RegisterCourse(webapp2.RequestHandler):
    def get(self):
        return webapp2.redirect('/{0}/{1}'.format(Index.registerUrl,
                                Index.nonFirstYear))

class RegisterNonFirstYearCourse(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("First Year Register Page")

class RegisterNonFirstYearCourse(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Non First Year Register Page")

class Admin(webapp2.RequestHandler):
    def get(self):
        templateValues = {
            'title' : Index.title + ' - Admin',
            'addCourseUrl' : Index.adminUrl + "/" + Index.manageCourseUrl,
            'addCourseText' : Index.addCourseText,
            'addSubjectUrl' : Index.adminUrl + "/" + Index.manageSubjectUrl,
            'addSubjectText' : Index.addSubjectText,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/admin.html')
        self.response.out.write(template.render(path, templateValues))


class ManageCourse(webapp2.RequestHandler):
    def get(self):
        _code = cgi.escape(self.request.get('code'))
        _name = cgi.escape(self.request.get('name'))
        _year = cgi.escape(self.request.get('year'))
        _price = cgi.escape(self.request.get('price'))
        if(_code!="" and _name!="" and _year!="" and _price!=""):
            _credits = []
            for i in range(1, int(_year)+1):
                credit = cgi.escape(self.request.get('y'+str(i)))
                _credits.append(int(credit))
            Course(parent=ParentKeys.course,
                   code=_code,
                   name=_name,
                   year=int(_year),
                   credits=_credits,
                   price=float(_price)).put()
        
        courses = Course.query(ancestor=ParentKeys.course)
        templateValues = {
            'title' : Index.title + ' - Admin - Manage Courses',
            'action' : Index.manageCourseUrl,
            'method' : 'get',
            'code' : 'code',
            'name' : 'name',
            'year' : 'year',
            'price' : 'price',
            'courses' : courses,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/Course.html')
        self.response.out.write(template.render(path, templateValues))

class ManageSubject(webapp2.RequestHandler):
    def get(self):
        _code = cgi.escape(self.request.get('code'))
        _name = cgi.escape(self.request.get('name'))
        _year = cgi.escape(self.request.get('year'))
        _credit = cgi.escape(self.request.get('credit'))
        if(_code!="" and _name!="" and _credit!=""):
            Subject(parent=ParentKeys.subject,
                    code=_code,
                    name=_name,
                    year=int(_year),
                    credit=int(_credit)).put()
        
        subjects = Subject.query(ancestor=ParentKeys.subject)
        templateValues = {
            'title' : Index.title + ' - Admin - Add New Subject',
            'action' : Index.manageSubjectUrl,
            'method' : 'get',
            'subjectId' : 'code',
            'subjectName' : 'name',
            'subjectYear' : 'year',
            'subjectCredit' : 'credit',
            'subjects' : subjects,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/Subject.html')
        self.response.out.write(template.render(path, templateValues))

class ManageCourseSubject(webapp2.RequestHandler):
    def get(self):
        code = cgi.escape(self.request.get('code'))
        courses = Course.query(ancestor=ParentKeys.course)
        courses = courses.filter(Course.code == code)
        course = 0
        for c in courses:
            course = c
        courseSubjects = CourseSubject.query(ancestor=ParentKeys.courseSubject)
        courseSubjects = courseSubjects.filter(CourseSubject.courseCode == code)
        subjects = Subject.query(ancestor=ParentKeys.subject)
        listSubjects = []
        for courseSubject in courseSubjects:
            subjects = subjects.filter(Subject.code != courseSubject.subjectCode)
            listSubjects.append(courseSubject.subjectCode)
        mySubjects = Subject.query(Subject.code.IN(listSubjects))
        templateValues = {
            'title' : Index.title + ' - Admin - Add Subjects to a Course',
            'code' : code,
            'course' : course,
            'subjects' : subjects,
            'courseSubjects' : courseSubjects,
            'mySubjects' : mySubjects,
        }
    
        path = os.path.join(os.path.dirname(__file__), 'html/courseSubject.html')
        self.response.out.write(template.render(path, templateValues))

class AddCourseSubject(webapp2.RequestHandler):
    def get(self):
        courseCode = cgi.escape(self.request.get('courseCode'))
        subjectCode = cgi.escape(self.request.get('subjectCode'))
        compulsory = bool(int(cgi.escape(self.request.get('compulsory'))))
        CourseSubject(parent=ParentKeys.courseSubject,
                      courseCode=courseCode,
                      subjectCode=subjectCode,
                      compulsory=compulsory).put()

app = webapp2.WSGIApplication([
                               ('/',
                                MainPage),
                               ('/%s' % Index.loginUrl,
                                Login),
                               ('/%s' % Index.registerUrl,
                                RegisterCourse),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.nonFirstYear),
                                RegisterNonFirstYearCourse),
                               ('/%s' % Index.adminUrl,
                                Admin),
                               ('/{0}/{1}'.format(Index.adminUrl,
                                                  Index.manageCourseUrl),
                                ManageCourse),
                               ('/{0}/{1}'.format(Index.adminUrl,
                                                  Index.manageSubjectUrl),
                                ManageSubject),
                               ('/{0}/{1}'.format(Index.adminUrl,
                                                  Index.manageCourseSubjectUrl),
                                ManageCourseSubject),
                               ('/{0}/{1}'.format(Index.adminUrl,
                                                  Index.addCourseSubjectUrl),
                                AddCourseSubject),
                               ], debug=True)


def main():
    application.run()


if __name__ == '__main__':
    main()
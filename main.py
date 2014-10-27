import cgi
import datetime
import os

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.api import users

import webapp2
import logging
import time
from webapp2_extras import security
from webapp2_extras import sessions

from ASRS import Student
from ASRS import Subject
from ASRS import Course
from ASRS import CourseSubject
from ASRS import StudentSubject

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class Index(object):
    title = "A Student Registration System"
    loginUrl = "login"
    loginText = "Login to Register Course"
    registerUrl = "register"
    nonFirstYearUrl = "non-first-year"
    firstYearUrl = "first-year"
    showOptionalSubjectsUrl = "show-optional-subjects"
    processingFirstYearUrl = "first-year/processing"
    checkIdAvailableUrl = "first-year/check-available"
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
    student = ndb.Key("Entity", "student_key")
    studentSubject = ndb.Key("Entity", "student_subject_key")

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
        return webapp2.redirect('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.nonFirstYearUrl))

class RegisterCourse(webapp2.RequestHandler):
    def get(self):
        return webapp2.redirect('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.firstYearUrl))

class RegisterFirstYearCourse(webapp2.RequestHandler):
    def get(self):
        courses = Course.query(ancestor=ParentKeys.course)
        templateValues = {
            'title' : Index.title + ' - Register First Year Course',
            'action' : Index.processingFirstYearUrl,
            'checkAvailableUrl' : Index.checkIdAvailableUrl,
            'courses' : courses,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/RegisterFirstYear.html')
        self.response.out.write(template.render(path, templateValues))

class ShowOptionalSubjects(webapp2.RequestHandler):
    def get(self):
        courseCode = cgi.escape(self.request.get('courseCode'))
        year = int(cgi.escape(self.request.get('year')))
        courseSubjects = CourseSubject.query(ancestor=ParentKeys.courseSubject)
        courseSubjects = courseSubjects.filter(CourseSubject.courseCode==courseCode,
                                               CourseSubject.courseYear==year,
                                               CourseSubject.compulsory==False)
        subjects = []
        for courseSubject in courseSubjects:
            subject = Subject.query(ancestor=ParentKeys.subject)
            subject = subject.filter(Subject.code == courseSubject.subjectCode).get()
            subjects.append(subject)

        templateValues = {
            'subjects' : subjects,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/showOptionalSubjects.html')
        self.response.out.write(template.render(path, templateValues))


class ProcessingFirstYear(webapp2.RequestHandler):
    def get(self):
        fname = cgi.escape(self.request.get('firstname'))
        lname = cgi.escape(self.request.get('lastname'))
        id = cgi.escape(self.request.get('id'))
        password = cgi.escape(self.request.get('password'))
        year = int(cgi.escape(self.request.get('year')))
        month = int(cgi.escape(self.request.get('month')))
        day = int(cgi.escape(self.request.get('day')))
        address = cgi.escape(self.request.get('address'))
        course = cgi.escape(self.request.get('courses'))
        subjects = self.request.get_all('subject')

        _year = 1
        Student(parent=ParentKeys.student,
                fname=fname,
                lname=lname,
                id=id,
                pwd=password,
                birthday=datetime.date(year,month,day),
                address=address,
                courseId=course,
                year=_year).put()
        
        for subject in subjects:
            subject = cgi.escape(subject)
            StudentSubject(parent=ParentKeys.studentSubject,
                           studentId=id,
                           subjectCode=subject,
                           credit=0).put()
        courseSubjects = CourseSubject.query(ancestor=ParentKeys.courseSubject)
        courseSubjects = courseSubjects.filter(CourseSubject.courseCode==course,
                                               CourseSubject.compulsory==True)
        for courseSubject in courseSubjects:
            subject = courseSubject.subjectCode
            StudentSubject(parent=ParentKeys.studentSubject,
                           studentId=id,
                           subjectCode=subject,
                           credit=0).put()
        self.response.out.write("<h2>Success</h2>")

class CheckIdAvailable(webapp2.RequestHandler):
    def get(self):
        id = cgi.escape(self.request.get('id'))
        key = Student.query(Student.id==id).get()
        if key:
            self.response.out.write("yes")
        else:
            self.response.out.write("no")

class RegisterNonFirstYearCourse(BaseHandler):
    def get(self):
        logged = False
        sid = self.session.get('sid')
        loginMsg = ""
        key = False
        if not sid:
            logged = True
            login = cgi.escape(self.request.get('login'))
            if(login=="Login"):
               id = cgi.escape(self.request.get('id'))
               pwd = cgi.escape(self.request.get('pwd'))
               key = Student.query(Student.id==id,
                                   Student.pwd==pwd).get()
               if key:
                    self.session['sid'] = key.id
               else:
                    loginMsg = "ID or Password Wrong"
        else:
            key = Student.query(Student.id==sid).get()
            login = cgi.escape(self.request.get('login'))
            if(login=="Logout"):
                self.session.pop('sid')
                key = False
           
        templateValues = {
            'title' : Index.title + ' - Register Non-First Year Course',
            'action' : Index.nonFirstYearUrl,
            'loginMsg' : loginMsg,
            'key' : key,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/RegisterNonFirstYear.html')
        self.response.out.write(template.render(path, templateValues))

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
        year = cgi.escape(self.request.get('year'))
        if year == "":
            year = 1;
        else:
            year = int(year)
        courses = Course.query(ancestor=ParentKeys.course)
        courses = courses.filter(Course.code == code)
        course = 0
        for c in courses:
            course = c
        courseSubjects = CourseSubject.query(ancestor=ParentKeys.courseSubject)
        courseSubjects = courseSubjects.filter(CourseSubject.courseCode == code,
                                               CourseSubject.courseYear == year)
        subjects = Subject.query(ancestor=ParentKeys.subject)
        listSubjects = []
        for courseSubject in courseSubjects:
            subjects = subjects.filter(Subject.code != courseSubject.subjectCode)
            listSubjects.append(courseSubject.subjectCode)
        mySubjects = Subject.query(Subject.code.IN(listSubjects))
        years = range(1, course.year+1)
        url = Index.manageCourseSubjectUrl + "?code=" + code + "&year="
        templateValues = {
            'title' : Index.title + ' - Admin - Add Subjects to a Course',
            'code' : code,
            'course' : course,
            'subjects' : subjects,
            'courseSubjects' : courseSubjects,
            'mySubjects' : mySubjects,
            'years' : years,
            'yearSelect' : year,
            'url' : url,
        }
    
        path = os.path.join(os.path.dirname(__file__), 'html/CourseSubject.html')
        self.response.out.write(template.render(path, templateValues))

class AddCourseSubject(webapp2.RequestHandler):
    def get(self):
        courseCode = cgi.escape(self.request.get('courseCode'))
        subjectCode = cgi.escape(self.request.get('subjectCode'))
        compulsory = bool(int(cgi.escape(self.request.get('compulsory'))))
        courseYear = int(cgi.escape(self.request.get('courseYear')))
        CourseSubject(parent=ParentKeys.courseSubject,
                      courseCode=courseCode,
                      subjectCode=subjectCode,
                      compulsory=compulsory,
                      courseYear=courseYear).put()



config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

app = webapp2.WSGIApplication([
                               ('/',
                                MainPage),
                               ('/%s' % Index.loginUrl,
                                Login),
                               ('/%s' % Index.registerUrl,
                                RegisterCourse),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.firstYearUrl),
                                RegisterFirstYearCourse),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.showOptionalSubjectsUrl),
                                ShowOptionalSubjects),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.processingFirstYearUrl),
                                ProcessingFirstYear),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.checkIdAvailableUrl),
                                CheckIdAvailable),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.nonFirstYearUrl),
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
                               ],
                              debug=True,
                              config=config)


def main():
    application.run()


if __name__ == '__main__':
    main()
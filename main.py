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

from ASRS import *

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
    studentUrl = "student"
    firstYearUrl = "first-year"
    nonFirstYearUrl = "non-first-year"
    showOptionalSubjectsUrl = "show-optional-subjects"
    processingFirstYearUrl = "first-year/processing"
    checkIdAvailableUrl = "first-year/check-available"
    registerText = "First Year Register"

    adminUrl = "admin"
    manageCourseUrl = "add-course"
    addCourseText = "Course"
    manageSubjectUrl = "add-subject"
    addSubjectText = "Subject"
    manageCourseSubjectUrl = "course"
    addCourseSubjectUrl = "add-subject-to-course"
    
    payUrl = "pay"
    
    adminNavigator = {
        'course' : {
            'text' : addCourseText,
            'url' : manageCourseUrl
        },
        'subject' : {
            'text' : addSubjectText,
            'url' : manageSubjectUrl
        }
    }


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
        return webapp2.redirect('/{0}'.format(Index.studentUrl))

class Pay(BaseHandler):
    def get(self):
        sid = self.session.get('sid')
        templateValues = {
            'title' : Index.title + " - Payment",
        }
        if not sid:
            templateValues['login'] = False
            templateValues['loginUrl'] = Index.loginUrl
        else:
            action = cgi.escape(self.request.get('action'))
            student = Student.query(ancestor=ParentKeys.student)
            student = student.filter(Student.id==sid).get()
            templateValues['login'] = True
            if action == "pay":
                student.paid = True
                student.put()
                templateValues['paid'] = True
                templateValues['loginUrl'] = Index.loginUrl
            else:
                fee = 0
                subjects = student.getSubjects()
                for s in subjects:
                    fee += s.examFee
                    if not student.examOnly:
                        fee += s.generalFee
                templateValues['subjects'] = subjects
                templateValues['student'] = student
                templateValues['fee'] = fee
                templateValues['action'] = Index.payUrl
            
    

        path = os.path.join(os.path.dirname(__file__), 'html/Pay.html')
        self.response.out.write(template.render(path, templateValues))


class RegisterCourse(webapp2.RequestHandler):
    def get(self):
        return webapp2.redirect('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.firstYearUrl))

class RegisterNonFirstYearCourse(webapp2.RequestHandler):
    def get(self):
        action = cgi.escape(self.request.get('action'))
        studentId = cgi.escape(self.request.get('id'))
        if action == "submit":
            self.process(studentId)
            return
        student = Student.query(ancestor=ParentKeys.student)
        student = student.filter(Student.id==studentId).get()
        nextYear = student.year + 1
        course = student.getCourse()
        subjects = course.getSubjects(nextYear,"optional")
        
        templateValues = {
            'title' : Index.title + ' - Register Non First Year Course',
            'action' : Index.nonFirstYearUrl,
            'student' : student,
            'course' : course,
            'subjects' : subjects,
            'nextYear' : nextYear,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/RegisterNonFirstYear.html')
        self.response.out.write(template.render(path, templateValues))
    def process(self, id):
        student = Student.query(ancestor=ParentKeys.student)
        student = student.filter(Student.id==id).get()
        
        subjects = self.request.get_all('subject')
        examOnly = False
        if cgi.escape(self.request.get('examOnly')) == "1":
            examOnly = True

        student.year += 1
        student.examOnly=examOnly
        student.paid=False
        student.put()
        
        for subject in subjects:
            subject = cgi.escape(subject)
            StudentSubject(parent=ParentKeys.studentSubject,
                           studentId=id,
                           subjectCode=subject,
                           subjectYear=student.year,
                           credit=0).put()
        courseSubjects = CourseSubject.query(ancestor=ParentKeys.courseSubject)
        courseSubjects = courseSubjects.filter(CourseSubject.courseCode==student.courseId,
                                               CourseSubject.courseYear==student.year,
                                               CourseSubject.compulsory==True)
        for courseSubject in courseSubjects:
            subject = courseSubject.subjectCode
            StudentSubject(parent=ParentKeys.studentSubject,
                           studentId=id,
                           subjectCode=subject,
                           subjectYear=student.year,
                           credit=0).put()
        
        templateValues = {
            'title' : Index.title + ' - Payment',
            'payUrl' : "../../" + Index.payUrl,
            'loginUrl' : "../../" + Index.loginUrl,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/Payment.html')
        self.response.out.write(template.render(path, templateValues))
    

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


class ProcessingFirstYear(BaseHandler):
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
        examOnly = False
        if cgi.escape(self.request.get('examOnly')) == "1":
            examOnly = True

        _year = 1
        Student(parent=ParentKeys.student,
                fname=fname,
                lname=lname,
                id=id,
                pwd=password,
                birthday=datetime.date(year,month,day),
                address=address,
                courseId=course,
                year=_year,
                examOnly=examOnly,
                paid=False).put()
        
        for subject in subjects:
            subject = cgi.escape(subject)
            StudentSubject(parent=ParentKeys.studentSubject,
                           studentId=id,
                           subjectCode=subject,
                           subjectYear=_year,
                           credit=0).put()
        courseSubjects = CourseSubject.query(ancestor=ParentKeys.courseSubject)
        courseSubjects = courseSubjects.filter(CourseSubject.courseCode==course,
                                               CourseSubject.courseYear==_year,
                                               CourseSubject.compulsory==True)
        for courseSubject in courseSubjects:
            subject = courseSubject.subjectCode
            StudentSubject(parent=ParentKeys.studentSubject,
                           studentId=id,
                           subjectCode=subject,
                           subjectYear=_year,
                           credit=0).put()
            
        self.session['sid'] = id
        templateValues = {
            'title' : Index.title + ' - Payment',
            'payUrl' : "../../" + Index.payUrl,
            'loginUrl' : "../../" + Index.loginUrl,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/Payment.html')
        self.response.out.write(template.render(path, templateValues))


class CheckIdAvailable(webapp2.RequestHandler):
    def get(self):
        id = cgi.escape(self.request.get('id'))
        key = Student.query(Student.id==id).get()
        if key:
            self.response.out.write("yes")
        else:
            self.response.out.write("no")

class StudentBB(BaseHandler):
    def get(self):
        sid = self.session.get('sid')
        loginMsg = ""
        student = False
        course = None
        subjects = None
        creditRequired = 0
        creditEarned = 0
        if not sid:
            login = cgi.escape(self.request.get('login'))
            if(login=="Login"):
               id = cgi.escape(self.request.get('id'))
               pwd = cgi.escape(self.request.get('pwd'))
               student = Student.query(ancestor=ParentKeys.student)
               student = student.filter(Student.id==id,
                                   Student.pwd==pwd).get()
               if student:
                    self.session['sid'] = student.id
               else:
                    loginMsg = "ID or Password Wrong"
        sid = self.session.get('sid')
        if sid:
            student = Student.query(ancestor=ParentKeys.student)
            student = student.filter(Student.id==sid).get()
            login = cgi.escape(self.request.get('login'))
            if(login=="Logout"):
                self.session.pop('sid')
                student = False
            else:
                course = Course.query(ancestor=ParentKeys.course)
                course = course.filter(Course.code==student.courseId).get()
                studentSubjects = StudentSubject.query(ancestor=ParentKeys.studentSubject)
                studentSubjects = studentSubjects.filter(StudentSubject.studentId==student.id,
                                                         StudentSubject.subjectYear==student.year)
                subjects = []
                for studentSubject in studentSubjects:
                    subject = Subject.query(ancestor=ParentKeys.subject)
                    subject = subject.filter(Subject.code==studentSubject.subjectCode).get()
                    subject.credit = studentSubject.credit
                    subjects.append(subject)
                    creditEarned += subject.credit
                creditRequired = course.credits[student.year-1]
        
        templateValues = {
            'title' : Index.title + ' - Student BB',
            'action' : Index.studentUrl,
            'loginMsg' : loginMsg,
            'student' : student,
            'course' : course,
            'subjects' : subjects,
            'creditRequired' : creditRequired,
            'creditEarned' : creditEarned,
            'payUrl' : Index.payUrl,
            'nextYearUrl' : Index.registerUrl + "/" + Index.nonFirstYearUrl,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/StudentBB.html')
        self.response.out.write(template.render(path, templateValues))

class Admin(webapp2.RequestHandler):
    def get(self):
        templateValues = {
            'title' : Index.title + ' - Admin',
            'navigator' : Index.adminNavigator,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/admin.html')
        self.response.out.write(template.render(path, templateValues))


class ManageCourse(webapp2.RequestHandler):
    def get(self):
        action = cgi.escape(self.request.get('action'))
        code = cgi.escape(self.request.get('code'))
        name = cgi.escape(self.request.get('name'))
        year = cgi.escape(self.request.get('year'))
        _credits = self.request.get_all('credit')
        credits = [0, 0, 0, 0, 0]
        
        if(code!="" and name!="" and year!=""):
            i = 0
            for credit in _credits:
                if not credit:
                    credits[i] = 0
                else:
                    credits[i] = int(cgi.escape(credit))
                i += 1
            if(action == "add"):
                Course(parent=ParentKeys.course,
                       code=code,
                       name=name,
                       year=int(year),
                       credits=credits).put()
                return webapp2.redirect('/{0}/{1}'.format(Index.adminUrl,
                                                        Index.manageCourseUrl))
            elif(action == "update"):
                course = Course.query(ancestor=ParentKeys.course)
                course = course.filter(Course.code==code).get()
                course.name = name
                course.year = int(year)
                course.credits = credits
                course.put()
                return webapp2.redirect('/{0}/{1}'.format(Index.adminUrl,
                                                        Index.manageCourseUrl))
            elif(action == "delete"):
                course = Course.query(ancestor=ParentKeys.course)
                course = course.filter(Course.code==code).get()
                cs = CourseSubject.query(ancestor=ParentKeys.courseSubject)
                cs = cs.filter(CourseSubject.courseCode==code)
                for c in cs:
                    c.key.delete()
                course.key.delete()
                return webapp2.redirect('/{0}/{1}'.format(Index.adminUrl,
                                                        Index.manageCourseUrl))
            elif(action == "manage"):
                return webapp2.redirect('/{0}/{1}?code={2}'.format(Index.adminUrl,
                                                        Index.manageCourseSubjectUrl,
                                                        code))
                
                
        courses = Course.query(ancestor=ParentKeys.course)
        templateValues = {
            'title' : Index.title + ' - Admin - Manage Courses',
            'navigator' : Index.adminNavigator,
            'action' : Index.manageCourseUrl,
            'method' : 'get',
            'courses' : courses,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/Course.html')
        self.response.out.write(template.render(path, templateValues))

class ManageSubject(webapp2.RequestHandler):
    def get(self):
        action = cgi.escape(self.request.get('action'))
        code = cgi.escape(self.request.get('code'))
        name = cgi.escape(self.request.get('name'))
        year = cgi.escape(self.request.get('year'))
        credit = cgi.escape(self.request.get('credit'))
        generalFee = cgi.escape(self.request.get('generalFee'))
        examFee = cgi.escape(self.request.get('examFee'))
        
        if(action=="add"):
            Subject(parent=ParentKeys.subject,
                    code=code,
                    name=name,
                    year=int(year),
                    credit=int(credit),
                    generalFee=float(generalFee),
                    examFee=float(examFee)).put()
            
            return webapp2.redirect('/{0}/{1}'.format(Index.adminUrl,
                                                  Index.manageSubjectUrl))
        elif(action=="update"):
            subject = Subject.query(ancestor=ParentKeys.subject)
            subject = subject.filter(Subject.code==code).get()
            subject.name = name
            subject.year = int(year)
            subject.credit = int(credit)
            subject.generalFee = float(generalFee)
            subject.examFee = float(examFee)
            subject.put()
            return webapp2.redirect('/{0}/{1}'.format(Index.adminUrl,
                                                  Index.manageSubjectUrl))
        elif(action=="delete"):
            subject = Subject.query(ancestor=ParentKeys.subject)
            subject = subject.filter(Subject.code==code).get()
            subject.key.delete()
            return webapp2.redirect('/{0}/{1}'.format(Index.adminUrl,
                                                  Index.manageSubjectUrl))
            
        
        subjects = Subject.query(ancestor=ParentKeys.subject)
        templateValues = {
            'title' : Index.title + ' - Admin - Add New Subject',
            'navigator' : Index.adminNavigator,
            'action' : Index.manageSubjectUrl,
            'method' : 'get',
            'subjects' : subjects,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'html/Subject.html')
        self.response.out.write(template.render(path, templateValues))

class ManageCourseSubject(webapp2.RequestHandler):
    def get(self):
        action = cgi.escape(self.request.get('action'))
        courseCode = cgi.escape(self.request.get('courseCode'))
        subjectCode = cgi.escape(self.request.get('subjectCode'))
        compulsory = cgi.escape(self.request.get('compulsory'))
        courseYear = cgi.escape(self.request.get('courseYear'))
        if action == "delete":
            cs = CourseSubject.query(ancestor=ParentKeys.courseSubject)
            cs = cs.filter(CourseSubject.courseCode==courseCode,
                CourseSubject.subjectCode==subjectCode,
                CourseSubject.compulsory==bool(int(compulsory)),
                CourseSubject.courseYear==int(courseYear)).get()
            cs.key.delete()
            return webapp2.redirect('/{0}/{1}?code={2}&year={3}'.format(Index.adminUrl,
                                                  Index.manageCourseSubjectUrl,
                                                  courseCode,
                                                  courseYear))
        
        code = cgi.escape(self.request.get('code'))
        year = cgi.escape(self.request.get('year'))
        if year == "":
            year = 1;
        else:
            year = int(year)
        course = Course.query(ancestor=ParentKeys.course)
        course = course.filter(Course.code == code).get()
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
            'navigator' : Index.adminNavigator,
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
                               ('/%s' % Index.payUrl,
                                Pay),
                               ('/%s' % Index.registerUrl,
                                RegisterCourse),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.firstYearUrl),
                                RegisterFirstYearCourse),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.nonFirstYearUrl),
                                RegisterNonFirstYearCourse),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.showOptionalSubjectsUrl),
                                ShowOptionalSubjects),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.processingFirstYearUrl),
                                ProcessingFirstYear),
                               ('/{0}/{1}'.format(Index.registerUrl,
                                                  Index.checkIdAvailableUrl),
                                CheckIdAvailable),
                               ('/{0}'.format(Index.studentUrl),
                                StudentBB),
                               ('/%s/' % Index.adminUrl,
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
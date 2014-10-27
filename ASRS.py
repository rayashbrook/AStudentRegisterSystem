from google.appengine.ext import ndb

class Student(ndb.Model):
    id = ndb.StringProperty()
    pwd = ndb.StringProperty()
    fname = ndb.StringProperty()
    lname = ndb.StringProperty()
    birthday = ndb.DateProperty()
    address = ndb.StringProperty()
    courseId = ndb.StringProperty()
    year = ndb.IntegerProperty()

class Course(ndb.Model):
    code = ndb.StringProperty()
    name = ndb.StringProperty()
    credits = ndb.IntegerProperty(repeated=True)
    year = ndb.IntegerProperty()
    price = ndb.FloatProperty()

class Subject(ndb.Model):
    code = ndb.StringProperty()
    name = ndb.StringProperty()
    year = ndb.IntegerProperty()
    credit = ndb.IntegerProperty()


class CourseSubject(ndb.Model):
    courseCode = ndb.StringProperty()
    courseYear = ndb.IntegerProperty()
    subjectCode = ndb.StringProperty()
    compulsory = ndb.BooleanProperty()

class StudentSubject(ndb.Model):
    studentId = ndb.StringProperty()
    subjectCode = ndb.StringProperty()
    credit = ndb.IntegerProperty()
    subjectYear = ndb.IntegerProperty()
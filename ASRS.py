from google.appengine.ext import ndb

class Student(ndb.Model):
    id = ndb.StringProperty()
    pwd = ndb.StringProperty()
    name = ndb.StringProperty()
    age = ndb.IntegerProperty()
    address = ndb.StringProperty()
    year = ndb.IntegerProperty()


class Course(ndb.Model):
    code = ndb.StringProperty()
    name = ndb.StringProperty()
    credits = ndb.IntegerProperty(repeated=True)
    year = ndb.IntegerProperty();
    price = ndb.FloatProperty();


class CourseSubject(ndb.Model):
    courseCode = ndb.StringProperty()
    subjectCode = ndb.StringProperty()
    compulsory = ndb.BooleanProperty()

class Subject(ndb.Model):
    code = ndb.StringProperty()
    name = ndb.StringProperty()
    year = ndb.IntegerProperty()
    credit = ndb.IntegerProperty()


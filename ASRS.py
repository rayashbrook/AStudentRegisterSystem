from google.appengine.ext import ndb

class User:
    def __init__(self, id, pwd, name, age, address):
        self.id = id
        self.pwd = pwd
        self.name = name
        self.age = age
        self.address = address

class Student(User):
    def __init__(self, id, pwd, name, age, address):
        super(Student, self).__init__(id, pwd, name, age, address)
    def setYear(year):
        self.year = year

class Stuff(User):
    def __init__(self, id, pwd, name, age, address):
        super(Stuff, self).__init__(id, pwd, name, age, address)

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


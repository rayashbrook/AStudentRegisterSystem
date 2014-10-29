from google.appengine.ext import ndb

class ParentKeys():
    course = ndb.Key("Entity", "course_key")
    subject = ndb.Key("Entity", "subject_key")
    courseSubject = ndb.Key("Entity", "course_subject_key")
    student = ndb.Key("Entity", "student_key")
    studentSubject = ndb.Key("Entity", "student_subject_key")

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
    
    def getSubjects(self, year=0):
        subjects = []
        courseSubjects = CourseSubject.query(ancestor=ParentKeys.courseSubject);
        courseSubjects = courseSubjects.filter(CourseSubject.courseCode==self.code)
        if year != 0:
            courseSubjects = courseSubjects.filter(CourseSubject.courseYear==year)
        for courseSubject in courseSubjects:
            subject = Subject.query(ancestor=ParentKeys.subject)
            subject = subject.filter(Subject.code==courseSubject.subjectCode)
            subjects.append(subject)
        return subjects
        
    
    def addSubject(self, subject, year=1, compulsory=True):
        CourseSubject(parent=ParentKeys.courseSubject,
                      courseCode=self.code,
                      courseYear=year,
                      subjectCode=subject.code,
                      compulsory=compulsory).put()
        
    
    

class Subject(ndb.Model):
    code = ndb.StringProperty()
    name = ndb.StringProperty()
    year = ndb.IntegerProperty()
    credit = ndb.IntegerProperty()
    generalFee = ndb.FloatProperty()
    examFee = ndb.FloatProperty()

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
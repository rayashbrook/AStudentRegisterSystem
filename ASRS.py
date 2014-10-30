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
    examOnly = ndb.BooleanProperty()
    paid = ndb.BooleanProperty()
    
    def getSubjects(self):
        ss = StudentSubject.query(ancestor=ParentKeys.studentSubject)
        ss = ss.filter(StudentSubject.studentId==self.id,
                       StudentSubject.subjectYear==self.year)
        codes = []
        subjects = []
        for s in ss:
            codes.append(s.subjectCode)
        subjects = Subject.query(ancestor=ParentKeys.subject)
        #subjects = subjects.filter(Subject.code.IN(codes))
        for code in codes:
            subject = subjects.filter(Subject.code==code)
            subjects.append(subject)
        return subjects
    
    def getCourse(self):
        course = Course.query(ancestor=ParentKeys.course)
        course = course.filter(Course.code==self.courseId).get()
        return course
    

class Course(ndb.Model):
    code = ndb.StringProperty()
    name = ndb.StringProperty()
    credits = ndb.IntegerProperty(repeated=True)
    year = ndb.IntegerProperty()  
    
    def getSubjects(self, year=0, filter="all"):
        subjects = []
        courseSubjects = CourseSubject.query(ancestor=ParentKeys.courseSubject);
        courseSubjects = courseSubjects.filter(CourseSubject.courseCode==self.code)
        if year != 0:
            courseSubjects = courseSubjects.filter(CourseSubject.courseYear==year)
        if filter == "optional":
            courseSubjects = courseSubjects.filter(CourseSubject.compulsory==False)
        elif filter == "compulsory":
            courseSubjects = courseSubjects.filter(CourseSubject.compulsory==True)
        for courseSubject in courseSubjects:
            subject = Subject.query(ancestor=ParentKeys.subject)
            subject = subject.filter(Subject.code==courseSubject.subjectCode).get()
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
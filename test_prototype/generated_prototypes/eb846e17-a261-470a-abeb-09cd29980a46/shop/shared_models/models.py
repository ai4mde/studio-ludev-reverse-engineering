from django.db import models
from django.utils import timezone


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=50)
    hire_date = models.DateField()

    def years_of_experience(self):
        return timezone.now().year - self.hire_date.year


class Course(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def duration_in_weeks(self):
        return (self.end_date - self.start_date).days // 7

    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class TeacherService(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.OneToOneField(Teacher, null=True, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, null=True)

    def get_experienced_teachers(self, min_years=5):
        experienced = []
        for teacher in Teacher.objects.all():
            if teacher.years_of_experience() >= min_years:
                experienced.append(teacher)
        return experienced

    def assign_teacher_to_course(self, teacher: Teacher, course: Course):
        course.teacher = teacher
        course.save()
        return course


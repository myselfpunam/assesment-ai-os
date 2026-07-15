from django.db import models
from core.models import BaseModel


class AttemptStatus(models.TextChoices):
    IN_PROGRESS = 'in_progress', 'In Progress'
    SUBMITTED   = 'submitted',   'Submitted'
    GRADED      = 'graded',      'Graded'
    TIMED_OUT   = 'timed_out',   'Timed Out'


class StudentAttempt(BaseModel):
    """
    One attempt by a student on an Assessment.
    Auto-graded immediately on submission for MCQ / True-False.
    Short Answer / Essay flagged for manual lecturer review.
    """
    student    = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='attempts')
    assessment = models.ForeignKey('assessments.Assessment',  on_delete=models.CASCADE, related_name='attempts')
    status     = models.CharField(max_length=20, choices=AttemptStatus.choices, default=AttemptStatus.IN_PROGRESS)
    attempt_number   = models.PositiveSmallIntegerField(default=1)
    started_at       = models.DateTimeField(auto_now_add=True)
    submitted_at     = models.DateTimeField(null=True, blank=True)
    total_score      = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    max_score        = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    percentage       = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_passed        = models.BooleanField(default=False)
    needs_manual_grading = models.BooleanField(default=False)

    class Meta:
        db_table = 'student_attempts'
        ordering = ['-created_at']
        unique_together = [['student', 'assessment', 'attempt_number']]

    def __str__(self):
        return f"{self.student.student_id} — {self.assessment.title} (Attempt {self.attempt_number})"


class StudentAnswer(BaseModel):
    """
    Student's answer for one question within an attempt.
    selected_options → MCQ / True-False (auto-graded)
    text_answer      → Short Answer / Essay (manual grading)
    """
    attempt          = models.ForeignKey(StudentAttempt, on_delete=models.CASCADE, related_name='answers')
    question         = models.ForeignKey('assessments.Question', on_delete=models.CASCADE, related_name='student_answers')
    selected_options = models.ManyToManyField('assessments.QuestionOption', blank=True, related_name='selected_in_answers')
    text_answer      = models.TextField(blank=True, default='')
    is_correct       = models.BooleanField(null=True, blank=True)  # null = not yet graded
    marks_obtained   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    graded_by        = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_answers')
    graded_at        = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'student_answers'
        unique_together = [['attempt', 'question']]

    def __str__(self):
        return f"Answer: {self.question} by {self.attempt.student.student_id}"

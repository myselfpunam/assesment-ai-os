from django.db import models
from core.models import BaseModel


class AssessmentType(models.TextChoices):
    QUIZ = 'quiz', 'Quiz'
    ASSIGNMENT = 'assignment', 'Assignment'
    EXAM = 'exam', 'Exam'
    PRACTICE = 'practice', 'Practice'


class QuestionType(models.TextChoices):
    MCQ = 'mcq', 'Multiple Choice'
    TRUE_FALSE = 'true_false', 'True / False'
    SHORT_ANSWER = 'short_answer', 'Short Answer'
    ESSAY = 'essay', 'Essay'


class Assessment(BaseModel):
    """
    An assessment (quiz/assignment/exam) assigned to a CourseSection.
    Contains questions and controls timing/attempts.
    """
    section = models.ForeignKey(
        'courses.CourseSection',
        on_delete=models.CASCADE,
        related_name='assessments',
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assessments',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    assessment_type = models.CharField(
        max_length=20,
        choices=AssessmentType.choices,
        default=AssessmentType.QUIZ,
    )
    total_marks = models.PositiveIntegerField(default=0)
    pass_marks = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text='Time allowed in minutes',
    )
    start_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the assessment becomes available',
    )
    end_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Deadline / closing time',
    )
    allow_multiple_attempts = models.BooleanField(default=False)
    max_attempts = models.PositiveIntegerField(default=1)
    shuffle_questions = models.BooleanField(default=False)
    show_result_immediately = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'assessments'
        verbose_name = 'Assessment'
        verbose_name_plural = 'Assessments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.assessment_type})"

    def recalculate_total_marks(self):
        total = self.questions.aggregate(
            total=models.Sum('marks')
        )['total'] or 0
        self.total_marks = total
        self.save(update_fields=['total_marks', 'updated_at'])


class Question(BaseModel):
    """
    A question inside an Assessment.
    Supports MCQ, True/False, Short Answer, Essay.
    """
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MCQ,
    )
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)
    explanation = models.TextField(
        blank=True,
        default='',
        help_text='Shown to student after submission',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'questions'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:60]}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.assessment.recalculate_total_marks()


class QuestionOption(BaseModel):
    """
    An answer option for MCQ or True/False questions.
    One or more options can be marked as correct.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
    )
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'question_options'
        verbose_name = 'Question Option'
        verbose_name_plural = 'Question Options'
        ordering = ['order']

    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.option_text[:50]}"

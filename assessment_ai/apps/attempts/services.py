from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.assessments.models import Assessment, Question
from apps.students.models import StudentProfile, Enrollment
from .models import StudentAttempt, StudentAnswer, AttemptStatus


class AttemptService:

    @staticmethod
    def start_attempt(assessment_id, student_profile_id):
        assessment = get_object_or_404(
            Assessment, id=assessment_id, is_published=True, is_active=True, deleted_at__isnull=True
        )
        student = get_object_or_404(StudentProfile, id=student_profile_id, deleted_at__isnull=True)

        # Student must be enrolled in the section
        enrolled = Enrollment.objects.filter(
            student=student,
            section=assessment.section,
            status='enrolled',
            deleted_at__isnull=True,
        ).exists()
        if not enrolled:
            raise ValueError("You are not enrolled in this course section.")

        # Check existing attempts
        existing_count = StudentAttempt.objects.filter(
            student=student,
            assessment=assessment,
            deleted_at__isnull=True,
        ).count()

        if not assessment.allow_multiple_attempts and existing_count >= 1:
            raise ValueError("You have already attempted this assessment.")

        if assessment.allow_multiple_attempts and existing_count >= assessment.max_attempts:
            raise ValueError(f"Maximum attempts ({assessment.max_attempts}) reached.")

        # Check if there's already an in-progress attempt
        in_progress = StudentAttempt.objects.filter(
            student=student,
            assessment=assessment,
            status=AttemptStatus.IN_PROGRESS,
            deleted_at__isnull=True,
        ).first()
        if in_progress:
            return in_progress

        attempt = StudentAttempt.objects.create(
            student=student,
            assessment=assessment,
            attempt_number=existing_count + 1,
            max_score=assessment.total_marks,
        )
        return attempt

    @staticmethod
    @transaction.atomic
    def submit_attempt(attempt_id, answers_data):
        """
        answers_data: list of dicts
        [
          { "question_id": "uuid", "selected_option_ids": ["uuid", ...] },  # MCQ / T-F
          { "question_id": "uuid", "text_answer": "some text" },            # Short / Essay
        ]
        """
        attempt = get_object_or_404(
            StudentAttempt, id=attempt_id, deleted_at__isnull=True
        )

        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise ValueError("This attempt has already been submitted.")

        needs_manual = False
        total_score = 0

        for answer_data in answers_data:
            question = get_object_or_404(
                Question, id=answer_data['question_id'], deleted_at__isnull=True
            )

            student_answer, _ = StudentAnswer.objects.get_or_create(
                attempt=attempt,
                question=question,
            )
            student_answer.text_answer = answer_data.get('text_answer', '')
            student_answer.selected_options.clear()

            if question.question_type in ('mcq', 'true_false'):
                option_ids = answer_data.get('selected_option_ids', [])
                if option_ids:
                    from apps.assessments.models import QuestionOption
                    options = QuestionOption.objects.filter(
                        id__in=option_ids, question=question
                    )
                    student_answer.selected_options.set(options)

                    # Auto-grade: selected options must exactly match correct options
                    correct_ids = set(
                        question.options.filter(is_correct=True).values_list('id', flat=True)
                    )
                    selected_ids = set(options.values_list('id', flat=True))
                    is_correct = (selected_ids == correct_ids)
                    student_answer.is_correct = is_correct
                    student_answer.marks_obtained = question.marks if is_correct else 0
                else:
                    student_answer.is_correct = False
                    student_answer.marks_obtained = 0

                total_score += student_answer.marks_obtained

            else:
                # short_answer / essay → needs manual grading
                student_answer.is_correct = None
                student_answer.marks_obtained = 0
                needs_manual = True

            student_answer.save()

        # Tally score (only auto-graded questions counted now)
        attempt.total_score = total_score
        attempt.max_score = attempt.assessment.total_marks
        attempt.percentage = (
            (total_score / attempt.max_score * 100) if attempt.max_score else 0
        )
        attempt.is_passed = total_score >= attempt.assessment.pass_marks
        attempt.needs_manual_grading = needs_manual
        attempt.status = AttemptStatus.SUBMITTED
        attempt.submitted_at = timezone.now()

        if not needs_manual:
            attempt.status = AttemptStatus.GRADED

        attempt.save()
        return attempt

    @staticmethod
    def get_attempt(attempt_id):
        return get_object_or_404(StudentAttempt, id=attempt_id, deleted_at__isnull=True)

    @staticmethod
    def get_attempts_for_assessment(assessment_id):
        return StudentAttempt.objects.filter(
            assessment_id=assessment_id,
            deleted_at__isnull=True,
        ).select_related('student__user').order_by('-created_at')

    @staticmethod
    def get_attempts_for_student(student_profile_id):
        return StudentAttempt.objects.filter(
            student_id=student_profile_id,
            deleted_at__isnull=True,
        ).select_related('assessment__section__course').order_by('-created_at')

    @staticmethod
    def manual_grade_answer(answer_id, marks, grader):
        from django.utils import timezone
        answer = get_object_or_404(StudentAnswer, id=answer_id, deleted_at__isnull=True)
        answer.marks_obtained = marks
        answer.is_correct = marks > 0
        answer.graded_by = grader
        answer.graded_at = timezone.now()
        answer.save()

        # Recalculate attempt total
        attempt = answer.attempt
        total = sum(
            a.marks_obtained for a in attempt.answers.all()
        )
        attempt.total_score = total
        attempt.percentage = (total / attempt.max_score * 100) if attempt.max_score else 0
        attempt.is_passed = total >= attempt.assessment.pass_marks

        # Check if all answers are graded
        ungraded = attempt.answers.filter(is_correct__isnull=True).count()
        if ungraded == 0:
            attempt.status = AttemptStatus.GRADED
            attempt.needs_manual_grading = False

        attempt.save()
        return answer

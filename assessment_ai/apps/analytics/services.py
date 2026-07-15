from django.db.models import Avg, Max, Min, Count, Q
from django.shortcuts import get_object_or_404

from apps.assessments.models import Assessment
from apps.attempts.models import StudentAttempt, AttemptStatus
from apps.students.models import StudentProfile, Enrollment
from apps.courses.models import CourseSection


class AssessmentAnalyticsService:

    @staticmethod
    def get_assessment_summary(assessment_id):
        assessment = get_object_or_404(
            Assessment, id=assessment_id, deleted_at__isnull=True
        )

        attempts = StudentAttempt.objects.filter(
            assessment=assessment,
            deleted_at__isnull=True,
        )

        graded = attempts.filter(status=AttemptStatus.GRADED)
        submitted = attempts.filter(status__in=[AttemptStatus.SUBMITTED, AttemptStatus.GRADED])

        stats = graded.aggregate(
            avg_score=Avg('total_score'),
            avg_pct=Avg('percentage'),
            highest=Max('total_score'),
            lowest=Min('total_score'),
        )

        total_graded = graded.count()
        passed = graded.filter(is_passed=True).count()
        pass_rate = round((passed / total_graded * 100), 1) if total_graded else 0

        # Score distribution in 5 bands
        distribution = {'0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0}
        for attempt in graded.values_list('percentage', flat=True):
            pct = float(attempt)
            if pct <= 20:
                distribution['0-20'] += 1
            elif pct <= 40:
                distribution['21-40'] += 1
            elif pct <= 60:
                distribution['41-60'] += 1
            elif pct <= 80:
                distribution['61-80'] += 1
            else:
                distribution['81-100'] += 1

        return {
            'assessment_id': str(assessment.id),
            'assessment_title': assessment.title,
            'assessment_type': assessment.assessment_type,
            'course': assessment.section.course.name,
            'section': assessment.section.section_code,
            'total_marks': assessment.total_marks,
            'pass_marks': assessment.pass_marks,
            'total_attempts': attempts.count(),
            'submitted': submitted.count(),
            'graded': total_graded,
            'passed': passed,
            'failed': total_graded - passed,
            'pass_rate_percent': pass_rate,
            'needs_manual_grading': attempts.filter(needs_manual_grading=True).count(),
            'average_score': round(float(stats['avg_score'] or 0), 2),
            'average_percentage': round(float(stats['avg_pct'] or 0), 2),
            'highest_score': float(stats['highest'] or 0),
            'lowest_score': float(stats['lowest'] or 0),
            'score_distribution': distribution,
        }

    @staticmethod
    def get_leaderboard(assessment_id, limit=10):
        assessment = get_object_or_404(
            Assessment, id=assessment_id, deleted_at__isnull=True
        )

        top_attempts = (
            StudentAttempt.objects
            .filter(
                assessment=assessment,
                status=AttemptStatus.GRADED,
                deleted_at__isnull=True,
            )
            .select_related('student__user')
            .order_by('-total_score', 'submitted_at')[:limit]
        )

        leaderboard = []
        for rank, attempt in enumerate(top_attempts, start=1):
            leaderboard.append({
                'rank': rank,
                'student_name': attempt.student.user.get_full_name(),
                'student_id': attempt.student.student_id,
                'score': float(attempt.total_score),
                'max_score': float(attempt.max_score),
                'percentage': float(attempt.percentage),
                'is_passed': attempt.is_passed,
                'submitted_at': attempt.submitted_at,
            })

        return {
            'assessment_title': assessment.title,
            'total_marks': assessment.total_marks,
            'leaderboard': leaderboard,
        }


class StudentAnalyticsService:

    @staticmethod
    def get_student_report(student_profile_id):
        student = get_object_or_404(
            StudentProfile, id=student_profile_id, deleted_at__isnull=True
        )

        attempts = StudentAttempt.objects.filter(
            student=student,
            status=AttemptStatus.GRADED,
            deleted_at__isnull=True,
        ).select_related('assessment__section__course')

        overall_stats = attempts.aggregate(
            avg_pct=Avg('percentage'),
            best_pct=Max('percentage'),
            total=Count('id'),
        )

        passed = attempts.filter(is_passed=True).count()
        total = overall_stats['total'] or 0
        pass_rate = round((passed / total * 100), 1) if total else 0

        # Per-assessment breakdown
        by_assessment = []
        seen = set()
        for attempt in attempts.order_by('-total_score'):
            aid = str(attempt.assessment_id)
            if aid not in seen:
                seen.add(aid)
                by_assessment.append({
                    'assessment_id': aid,
                    'assessment_title': attempt.assessment.title,
                    'assessment_type': attempt.assessment.assessment_type,
                    'course': attempt.assessment.section.course.name,
                    'course_code': attempt.assessment.section.course.code,
                    'section': attempt.assessment.section.section_code,
                    'best_score': float(attempt.total_score),
                    'max_score': float(attempt.max_score),
                    'best_percentage': float(attempt.percentage),
                    'is_passed': attempt.is_passed,
                    'submitted_at': attempt.submitted_at,
                })

        return {
            'student': {
                'id': str(student.id),
                'student_id': student.student_id,
                'name': student.user.get_full_name(),
                'email': student.user.email,
                'programme': student.programme.name,
                'batch': student.batch.name if student.batch else None,
            },
            'overall': {
                'total_graded_attempts': total,
                'passed': passed,
                'failed': total - passed,
                'pass_rate_percent': pass_rate,
                'average_percentage': round(float(overall_stats['avg_pct'] or 0), 2),
                'best_percentage': round(float(overall_stats['best_pct'] or 0), 2),
            },
            'by_assessment': by_assessment,
        }


class SectionAnalyticsService:

    @staticmethod
    def get_section_report(section_id):
        section = get_object_or_404(
            CourseSection, id=section_id, deleted_at__isnull=True
        )

        enrollments = Enrollment.objects.filter(
            section=section, deleted_at__isnull=True
        )
        enrolled_count = enrollments.count()

        assessments = Assessment.objects.filter(
            section=section,
            is_published=True,
            deleted_at__isnull=True,
        ).prefetch_related('attempts')

        assessment_reports = []
        for assessment in assessments:
            graded = StudentAttempt.objects.filter(
                assessment=assessment,
                status=AttemptStatus.GRADED,
                deleted_at__isnull=True,
            )
            graded_count = graded.count()
            passed = graded.filter(is_passed=True).count()
            stats = graded.aggregate(avg=Avg('percentage'), high=Max('percentage'))

            assessment_reports.append({
                'assessment_id': str(assessment.id),
                'title': assessment.title,
                'type': assessment.assessment_type,
                'total_marks': assessment.total_marks,
                'total_attempts': graded_count,
                'passed': passed,
                'pass_rate_percent': round((passed / graded_count * 100), 1) if graded_count else 0,
                'average_percentage': round(float(stats['avg'] or 0), 2),
                'highest_percentage': round(float(stats['high'] or 0), 2),
            })

        # Top 5 students in this section (by average score across all assessments)
        student_scores = []
        for enrollment in enrollments.select_related('student__user'):
            sp = enrollment.student
            avg = StudentAttempt.objects.filter(
                student=sp,
                assessment__section=section,
                status=AttemptStatus.GRADED,
                deleted_at__isnull=True,
            ).aggregate(avg=Avg('percentage'))['avg']
            if avg is not None:
                student_scores.append({
                    'student_id': sp.student_id,
                    'name': sp.user.get_full_name(),
                    'average_percentage': round(float(avg), 2),
                })

        student_scores.sort(key=lambda x: x['average_percentage'], reverse=True)

        return {
            'section': {
                'id': str(section.id),
                'code': section.section_code,
                'course': section.course.name,
                'course_code': section.course.code,
                'semester': section.semester.name,
            },
            'enrolled_students': enrolled_count,
            'published_assessments': assessments.count(),
            'assessments': assessment_reports,
            'top_students': student_scores[:5],
        }

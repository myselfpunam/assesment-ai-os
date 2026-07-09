from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    AssessmentListSerializer,
    AssessmentDetailSerializer,
    AssessmentCreateSerializer,
    QuestionSerializer,
    QuestionCreateSerializer,
    QuestionOptionSerializer,
    QuestionOptionCreateSerializer,
)
from .services import AssessmentService, QuestionService, QuestionOptionService
from .document_extractor import extract_text
from .ai_generator import generate_questions_with_ai
from core.utils.response import ApiResponse
from apps.courses.services import CourseMaterialService


class AssessmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        assessments = AssessmentService.get_assessments_for_section(section_id)
        serializer = AssessmentListSerializer(assessments, many=True)
        return ApiResponse.success(serializer.data, 'Assessments retrieved successfully.')

    def post(self, request, section_id):
        serializer = AssessmentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error('Validation failed.', serializer.errors)
        assessment = AssessmentService.create_assessment(
            section_id=section_id,
            user=request.user,
            data=serializer.validated_data,
        )
        return ApiResponse.created(
            AssessmentDetailSerializer(assessment).data,
            'Assessment created successfully.',
        )


class AssessmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id):
        assessment = AssessmentService.get_assessment(assessment_id)
        serializer = AssessmentDetailSerializer(assessment)
        return ApiResponse.success(serializer.data, 'Assessment retrieved successfully.')

    def delete(self, request, assessment_id):
        AssessmentService.delete_assessment(assessment_id)
        return ApiResponse.success(None, 'Assessment deleted successfully.')


class AssessmentPublishView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, assessment_id):
        assessment = AssessmentService.publish_assessment(assessment_id)
        return ApiResponse.success(
            AssessmentDetailSerializer(assessment).data,
            'Assessment published successfully.',
        )


class QuestionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id):
        assessment = AssessmentService.get_assessment(assessment_id)
        questions = assessment.questions.filter(
            is_active=True, deleted_at__isnull=True
        ).prefetch_related('options')
        serializer = QuestionSerializer(questions, many=True)
        return ApiResponse.success(serializer.data, 'Questions retrieved successfully.')

    def post(self, request, assessment_id):
        serializer = QuestionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error('Validation failed.', serializer.errors)
        question = QuestionService.add_question(
            assessment_id=assessment_id,
            data=serializer.validated_data,
        )
        return ApiResponse.created(
            QuestionSerializer(question).data,
            'Question added successfully.',
        )


class QuestionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, question_id):
        QuestionService.delete_question(question_id)
        return ApiResponse.success(None, 'Question deleted successfully.')


class QuestionOptionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        from .models import Question
        from django.shortcuts import get_object_or_404
        question = get_object_or_404(Question, id=question_id, deleted_at__isnull=True)
        options = question.options.filter(deleted_at__isnull=True)
        serializer = QuestionOptionSerializer(options, many=True)
        return ApiResponse.success(serializer.data, 'Options retrieved successfully.')

    def post(self, request, question_id):
        serializer = QuestionOptionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error('Validation failed.', serializer.errors)
        option = QuestionOptionService.add_option(
            question_id=question_id,
            data=serializer.validated_data,
        )
        return ApiResponse.created(
            QuestionOptionSerializer(option).data,
            'Option added successfully.',
        )


class QuestionOptionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, option_id):
        QuestionOptionService.delete_option(option_id)
        return ApiResponse.success(None, 'Option deleted successfully.')


class AIQuizGenerateView(APIView):
    """
    Upload a PDF/DOCX/PPTX file and let Claude AI generate quiz questions automatically.

    Form fields:
        file          — PDF, DOCX, or PPTX file (required)
        section_id    — UUID of the CourseSection (required)
        title         — Assessment title (required)
        num_questions — How many questions to generate (default: 10)
        question_type — mcq | true_false | mixed | short_answer (default: mcq)
        topic         — Optional: focus on a specific topic within the document
        pass_marks    — Optional: passing score (default: 0)
        duration_minutes — Optional: time limit in minutes (default: 30)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        section_id = request.data.get('section_id')
        if not section_id:
            return ApiResponse.error('section_id is required.')

        title = request.data.get('title', 'AI Generated Quiz')
        num_questions = int(request.data.get('num_questions', 10))
        question_type = request.data.get('question_type', 'mcq')
        topic = request.data.get('topic', '')
        pass_marks = int(request.data.get('pass_marks', 0))
        duration_minutes = int(request.data.get('duration_minutes', 30))

        if num_questions < 1 or num_questions > 50:
            return ApiResponse.error('num_questions must be between 1 and 50.')

        valid_types = ['mcq', 'true_false', 'mixed', 'short_answer']
        if question_type not in valid_types:
            return ApiResponse.error(f'question_type must be one of: {", ".join(valid_types)}')

        # ── Get text: from saved material OR freshly uploaded file ──
        material_id = request.data.get('material_id')
        source_name = ''

        if material_id:
            # Lecturer already uploaded the material before — reuse stored text
            try:
                material = CourseMaterialService.get_material(material_id)
                extracted_text = material.extracted_text
                source_name = material.original_filename
            except Exception:
                return ApiResponse.error('Material not found. Check material_id.')
        else:
            # Direct file upload (one-time)
            file = request.FILES.get('file')
            if not file:
                return ApiResponse.error(
                    'Provide either material_id (saved material) or upload a file.'
                )
            try:
                file_bytes = file.read()
                extracted_text = extract_text(file_bytes, file.name)
                source_name = file.name
            except ValueError as e:
                return ApiResponse.error(str(e))
            except Exception as e:
                return ApiResponse.error(f'Failed to read file: {str(e)}')

        if len(extracted_text.strip()) < 100:
            return ApiResponse.error(
                'Not enough text in the material. Make sure the file has readable content.'
            )

        # ── Generate questions via Groq AI ────────────────────
        try:
            ai_questions = generate_questions_with_ai(
                text=extracted_text,
                num_questions=num_questions,
                question_type=question_type,
                topic=topic,
            )
        except ValueError as e:
            return ApiResponse.error(str(e))
        except Exception as e:
            return ApiResponse.error(f'AI generation failed: {str(e)}')

        # ── Create Assessment in DB ───────────────────────────
        assessment = AssessmentService.create_assessment(
            section_id=section_id,
            user=request.user,
            data={
                'title': title,
                'description': f'AI-generated from: {source_name}' + (f' | Topic: {topic}' if topic else ''),
                'assessment_type': 'quiz',
                'pass_marks': pass_marks,
                'duration_minutes': duration_minutes,
                'allow_multiple_attempts': False,
                'max_attempts': 1,
                'shuffle_questions': True,
                'show_result_immediately': True,
            },
        )

        # ── Save Questions + Options ──────────────────────────
        created_questions = []
        for idx, q_data in enumerate(ai_questions, start=1):
            question = QuestionService.add_question(
                assessment_id=assessment.id,
                data={
                    'question_text': q_data.get('question_text', ''),
                    'question_type': q_data.get('question_type', question_type if question_type != 'mixed' else 'mcq'),
                    'marks': q_data.get('marks', 1),
                    'order': q_data.get('order', idx),
                    'explanation': q_data.get('explanation', ''),
                },
            )
            for opt in q_data.get('options', []):
                QuestionOptionService.add_option(
                    question_id=question.id,
                    data={
                        'option_text': opt.get('option_text', ''),
                        'is_correct': opt.get('is_correct', False),
                        'order': opt.get('order', 1),
                    },
                )
            created_questions.append(question)

        assessment.refresh_from_db()

        return ApiResponse.created(
            {
                'assessment': AssessmentDetailSerializer(assessment).data,
                'questions_generated': len(created_questions),
                'source': source_name,
                'topic': topic or 'General (full document)',
            },
            f'Successfully generated {len(created_questions)} questions from "{source_name}".',
        )

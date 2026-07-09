from django.urls import path
from .views import (
    AssessmentListCreateView,
    AssessmentDetailView,
    AssessmentPublishView,
    QuestionListCreateView,
    QuestionDeleteView,
    QuestionOptionListCreateView,
    QuestionOptionDeleteView,
    AIQuizGenerateView,
)

urlpatterns = [
    # AI auto-generate quiz from uploaded file
    path('generate-from-file/', AIQuizGenerateView.as_view(), name='ai-quiz-generate'),

    # Assessments under a section
    path('sections/<uuid:section_id>/assessments/', AssessmentListCreateView.as_view(), name='assessment-list-create'),

    # Assessment detail
    path('<uuid:assessment_id>/', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('<uuid:assessment_id>/publish/', AssessmentPublishView.as_view(), name='assessment-publish'),

    # Questions under an assessment
    path('<uuid:assessment_id>/questions/', QuestionListCreateView.as_view(), name='question-list-create'),
    path('questions/<uuid:question_id>/', QuestionDeleteView.as_view(), name='question-delete'),

    # Options under a question
    path('questions/<uuid:question_id>/options/', QuestionOptionListCreateView.as_view(), name='option-list-create'),
    path('options/<uuid:option_id>/', QuestionOptionDeleteView.as_view(), name='option-delete'),
]

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Company, KBEntry, QueryLog
from .permissions import IsAdminUser


class RegisterView(APIView):
    """POST /api/auth/register/ - public endpoint (no token required)."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        company_name = (data.get('company_name') or '').strip()
        email = (data.get('email') or '').strip()

        if not username or not password or not company_name:
            return Response(
                {'error': 'username, password and company_name are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'A user with that username already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # The post_save signal auto-creates the Company profile and its
        # api_key - it is never set manually here. `role` is never read
        # from the request body; it always defaults to CLIENT.
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # The signal seeds company_name from the email; update it with the
        # real company name supplied at registration.
        company = user.company
        company.company_name = company_name
        company.save(update_fields=['company_name'])

        return Response(
            {
                'username': user.username,
                'company_name': company.company_name,
                'api_key': company.api_key,
                'access': str(RefreshToken.for_user(user).access_token),
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """POST /api/auth/login/ - public endpoint (no token required)."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        company = user.company
        return Response(
            {
                'access': str(RefreshToken.for_user(user).access_token),
                'company_name': company.company_name,
                'api_key': company.api_key,
            }
        )


class KBQueryView(APIView):
    """POST /api/kb/query/ - protected by JWT via global DRF defaults."""

    def post(self, request):
        search_term = (request.data.get('search') or '').strip()
        if not search_term:
            return Response(
                {'error': "'search' field is required and cannot be blank."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # The company is always taken from the authenticated user,
        # never from the request body.
        company = request.user.company

        # The search and the QueryLog write must succeed together or
        # not at all.
        with transaction.atomic():
            results = KBEntry.objects.filter(
                Q(question__icontains=search_term) |
                Q(answer__icontains=search_term)
            )
            count = results.count()
            QueryLog.objects.create(
                company=company,
                search_term=search_term,
                results_count=count
            )

        return Response(
            {
                'search': search_term,
                'count': count,
                'results': [
                    {
                        'id': entry.id,
                        'question': entry.question,
                        'answer': entry.answer,
                        'category': entry.category,
                    }
                    for entry in results
                ],
            }
        )


class UsageSummaryView(APIView):
    """GET /api/admin/usage-summary/ - admin-only usage dashboard."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        total_queries = QueryLog.objects.aggregate(total=Count('id'))['total']
        active_companies = QueryLog.objects.values('company').distinct().count()
        top_search_terms = list(
            QueryLog.objects
            .values('search_term')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        return Response(
            {
                'total_queries': total_queries,
                'active_companies': active_companies,
                'top_search_terms': top_search_terms,
            }
        )

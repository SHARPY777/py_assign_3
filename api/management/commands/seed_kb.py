"""Seed the knowledge base with Q&A entries and create a demo admin account."""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from api.models import Company, KBEntry

KB_ENTRIES = [
    (
        'What is select_related in Django ORM?',
        'select_related performs a SQL JOIN and fetches related objects in a '
        'single query. Use it for forward ForeignKey and OneToOneField '
        'relations to avoid the N+1 query problem.',
        KBEntry.Category.DATABASE,
    ),
    (
        'When should I use select_related vs prefetch_related?',
        'select_related follows forward ForeignKey/OneToOne relations using a '
        'SQL JOIN, while prefetch_related issues a separate query and is used '
        'for reverse relations and ManyToMany fields. Both reduce query counts.',
        KBEntry.Category.DATABASE,
    ),
    (
        'How does transaction.atomic() work in Django?',
        'transaction.atomic() starts a transaction. Every database operation '
        'inside the with block must succeed together; if any operation raises '
        'an exception, the whole block is rolled back.',
        KBEntry.Category.DATABASE,
    ),
    (
        'What is a JWT token?',
        'A JSON Web Token (JWT) is a signed token that carries claims such as '
        'the user id and expiry. APIs use it for stateless authentication: '
        'the server verifies the signature instead of storing session state.',
        KBEntry.Category.API,
    ),
    (
        'How do I refresh a JWT access token with SimpleJWT?',
        'POST your refresh token to the /api/token/refresh/ endpoint. '
        'SimpleJWT verifies it and returns a new signed access token.',
        KBEntry.Category.API,
    ),
    (
        'When should I use Q objects in Django?',
        'Q objects encapsulate a single query condition and can be combined '
        'with & (AND), | (OR) and ~ (NOT). Use them for complex filters such '
        'as searching multiple fields: Q(question__icontains=s) | Q(answer__icontains=s).',
        KBEntry.Category.FRAMEWORK,
    ),
    (
        'How do Django signals work?',
        'Signals let decoupled apps react to events. For example, a post_save '
        'signal on the User model fires after save() completes and can '
        'auto-create a related profile object.',
        KBEntry.Category.FRAMEWORK,
    ),
    (
        'What is a REST API?',
        'A REST API exposes resources over HTTP: nouns in URLs, verbs like '
        'GET, POST, PUT, PATCH and DELETE for actions, and status codes to '
        'communicate outcomes. It is stateless and cacheable.',
        KBEntry.Category.API,
    ),
    (
        'What is Docker and why use it for PostgreSQL?',
        'Docker packages software into containers. A docker-compose.yml file '
        'can start PostgreSQL with a fixed version, port and credentials '
        'without installing anything on the host machine.',
        KBEntry.Category.CLOUD,
    ),
    (
        'How do I connect Django to PostgreSQL?',
        'Configure the DATABASES setting with the postgresql engine plus '
        'NAME, USER, PASSWORD, HOST and PORT. Keep credentials in a .env file '
        'and load them with python-dotenv, never hardcode them in settings.',
        KBEntry.Category.DATABASE,
    ),
    (
        'What is the N+1 query problem?',
        'Iterating over related objects and triggering one extra query per '
        'item causes N+1 queries. Fix it with select_related (JOIN) or '
        'prefetch_related (second batched query).',
        KBEntry.Category.DATABASE,
    ),
    (
        'What is Django REST Framework?',
        'DRF is a toolkit for building Web APIs on Django. It provides '
        'serializers, generic views, authentication classes like JWT, and '
        'permissions such as IsAuthenticated and custom BasePermission classes.',
        KBEntry.Category.FRAMEWORK,
    ),
    (
        'What is a database index?',
        'An index is a data structure (usually a B-tree) that speeds up reads '
        'on a column at the cost of slower writes and extra storage. Add '
        'db_index=True or Meta indexes to frequently filtered fields.',
        KBEntry.Category.DATABASE,
    ),
    (
        'What is horizontal scaling in the cloud?',
        'Horizontal scaling adds more machines to spread load, while vertical '
        'scaling makes a single machine bigger. Horizontal scaling is usually '
        'more fault tolerant and cost effective in cloud infrastructure.',
        KBEntry.Category.CLOUD,
    ),
]

ADMIN_USERNAME = 'teamboard_admin'
ADMIN_PASSWORD = 'adminpass123'
ADMIN_COMPANY_NAME = 'TeamBoard Platform'


class Command(BaseCommand):
    help = 'Seed the knowledge base with Q&A entries and create a demo admin user.'

    def handle(self, *args, **options):
        KBEntry.objects.all().delete()
        for question, answer, category in KB_ENTRIES:
            KBEntry.objects.create(
                question=question,
                answer=answer,
                category=category
            )
        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(KB_ENTRIES)} KB entries.'
        ))

        if User.objects.filter(username=ADMIN_USERNAME).exists():
            self.stdout.write('Demo admin user already exists - skipped.')
            return

        admin_user = User.objects.create_user(
            username=ADMIN_USERNAME,
            email='admin@teamboard.io',
            password=ADMIN_PASSWORD
        )
        # The post_save signal already created the Company profile;
        # promote it to the ADMIN role.
        company = admin_user.company
        company.company_name = ADMIN_COMPANY_NAME
        company.role = Company.Role.ADMIN
        company.save(update_fields=['company_name', 'role'])
        self.stdout.write(self.style.SUCCESS(
            f'Created demo admin user "{ADMIN_USERNAME}" '
            f'(company: {ADMIN_COMPANY_NAME}, role: admin).'
        ))

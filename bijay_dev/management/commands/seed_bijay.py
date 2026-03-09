"""Management command to seed bijay_dev with realistic portfolio data.

Usage:
    python manage.py seed_bijay          — create seed data (skip if already present)
    python manage.py seed_bijay --flush  — delete existing bijay_dev data, then re-seed
"""

from __future__ import annotations

import logging
from datetime import date

from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone

from bijay_dev.models import (
    BlogCategory,
    BlogPost,
    BlogTag,
    Book,
    Certification,
    Education,
    Experience,
    Project,
    ReadingList,
    SkillCategory,
    TechStack,
    Thought,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Seed the bijay_dev app with realistic portfolio data for frontend testing."""

    help = "Populate bijay_dev with realistic seed data across all 12 models."

    def add_arguments(self, parser: CommandParser) -> None:
        """Register optional --flush flag.

        Args:
            parser: The argument parser instance.
        """
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing bijay_dev data before seeding.",
        )

    def handle(self, *args: object, **kwargs: object) -> None:
        """Execute the seed logic.

        Args:
            *args: Positional arguments (unused).
            **kwargs: Parsed keyword arguments including 'flush'.
        """
        flush: bool = kwargs["flush"]

        if flush:
            self.stdout.write(self.style.WARNING("Flushing bijay_dev data..."))
            self._flush_all()
            self.stdout.write(self.style.SUCCESS("bijay_dev data flushed."))

        skills = self._seed_skill_categories_and_tech_stack()
        self._seed_projects(skills)
        self._seed_experience()
        self._seed_education()
        self._seed_certifications()
        categories = self._seed_blog_categories()
        tags = self._seed_blog_tags()
        self._seed_blog_posts(categories, tags)
        self._seed_reading_list()
        self._seed_thoughts()
        self._seed_books()

        self.stdout.write(self.style.SUCCESS("\nbijay_dev seed complete."))

    # ------------------------------------------------------------------
    # Flush
    # ------------------------------------------------------------------

    def _flush_all(self) -> None:
        """Delete all bijay_dev data in dependency-safe order."""
        BlogPost.objects.all().delete()
        BlogTag.objects.all().delete()
        BlogCategory.objects.all().delete()
        Project.objects.all().delete()
        TechStack.objects.all().delete()
        SkillCategory.objects.all().delete()
        Experience.objects.all().delete()
        Education.objects.all().delete()
        Certification.objects.all().delete()
        ReadingList.objects.all().delete()
        Thought.objects.all().delete()
        Book.objects.all().delete()

    # ------------------------------------------------------------------
    # Skills & Tech Stack
    # ------------------------------------------------------------------

    def _seed_skill_categories_and_tech_stack(self) -> dict[str, TechStack]:
        """Create skill categories and tech stack entries.

        Returns:
            Dict mapping skill name → TechStack instance for M2M linking.
        """
        categories_data: list[dict] = [
            {
                "name": "Backend",
                "order": 1,
                "skills": [
                    {"name": "Python", "is_featured": True, "order": 1},
                    {"name": "Django", "is_featured": True, "order": 2},
                    {"name": "Django REST Framework", "is_featured": True, "order": 3},
                    {"name": "FastAPI", "is_featured": False, "order": 4},
                    {"name": "Celery", "is_featured": False, "order": 5},
                ],
            },
            {
                "name": "Database",
                "order": 2,
                "skills": [
                    {"name": "PostgreSQL", "is_featured": True, "order": 1},
                    {"name": "Redis", "is_featured": True, "order": 2},
                    {"name": "MongoDB", "is_featured": False, "order": 3},
                    {"name": "SQLite", "is_featured": False, "order": 4},
                ],
            },
            {
                "name": "DevOps & Cloud",
                "order": 3,
                "skills": [
                    {"name": "Docker", "is_featured": True, "order": 1},
                    {"name": "Nginx", "is_featured": False, "order": 2},
                    {"name": "GitHub Actions", "is_featured": False, "order": 3},
                    {"name": "AWS (EC2, S3, RDS)", "is_featured": False, "order": 4},
                    {"name": "Linux / VPS", "is_featured": False, "order": 5},
                ],
            },
            {
                "name": "Tools & Workflow",
                "order": 4,
                "skills": [
                    {"name": "Git", "is_featured": False, "order": 1},
                    {"name": "VS Code", "is_featured": False, "order": 2},
                    {"name": "Postman", "is_featured": False, "order": 3},
                    {"name": "pytest", "is_featured": False, "order": 4},
                    {"name": "Ruff / Black", "is_featured": False, "order": 5},
                ],
            },
            {
                "name": "Frontend (Basics)",
                "order": 5,
                "skills": [
                    {"name": "HTML / CSS", "is_featured": False, "order": 1},
                    {"name": "JavaScript", "is_featured": False, "order": 2},
                    {"name": "Next.js", "is_featured": False, "order": 3},
                    {"name": "Tailwind CSS", "is_featured": False, "order": 4},
                ],
            },
        ]

        skill_map: dict[str, TechStack] = {}

        for cat_data in categories_data:
            category, _ = SkillCategory.objects.get_or_create(
                name=cat_data["name"],
                defaults={"order": cat_data["order"]},
            )
            for skill_data in cat_data["skills"]:
                tech, created = TechStack.objects.get_or_create(
                    category=category,
                    name=skill_data["name"],
                    defaults={
                        "is_featured": skill_data["is_featured"],
                        "order": skill_data["order"],
                    },
                )
                skill_map[tech.name] = tech
                if created:
                    logger.debug("Created TechStack: %s", tech)

        total = TechStack.objects.count()
        self.stdout.write(
            f"  Skills: {len(categories_data)} categories, {total} tech stack entries."
        )
        return skill_map

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def _seed_projects(self, skills: dict[str, TechStack]) -> None:
        """Create portfolio projects with M2M tech stack links.

        Args:
            skills: Dict mapping skill name → TechStack instance.
        """
        projects_data: list[dict] = [
            {
                "title": "Portfolio Backend API",
                "description": (
                    "<p>A production-grade <strong>Django REST API</strong> monorepo powering "
                    "three developer portfolio sites. Features include JWT auth, "
                    "rate limiting, OpenAPI docs, and CKEditor 5 rich content.</p>"
                ),
                "github_url": "https://github.com/bijay-example/portfolio-backend",
                "live_url": "https://api.bijay.dev",
                "status": Project.Status.ACTIVE,
                "is_featured": True,
                "order": 1,
                "tech_stack": [
                    "Django",
                    "Django REST Framework",
                    "PostgreSQL",
                    "Docker",
                    "Nginx",
                ],
            },
            {
                "title": "Real-Time Chat Service",
                "description": (
                    "<p>WebSocket-based chat service built with <strong>Django Channels</strong> "
                    "and <strong>Redis</strong>. Supports private messaging, group chats, "
                    "typing indicators, and message read receipts.</p>"
                ),
                "github_url": "https://github.com/bijay-example/chat-service",
                "live_url": "",
                "status": Project.Status.ACTIVE,
                "is_featured": True,
                "order": 2,
                "tech_stack": ["Django", "Redis", "PostgreSQL", "Docker"],
            },
            {
                "title": "E-Commerce REST API",
                "description": (
                    "<p>A full-featured e-commerce backend with product catalog, cart, "
                    "checkout flow, Stripe integration, and order management. "
                    "Built following DDD principles.</p>"
                ),
                "github_url": "https://github.com/bijay-example/ecommerce-api",
                "live_url": "https://shop-api.bijay.dev",
                "status": Project.Status.ACTIVE,
                "is_featured": True,
                "order": 3,
                "tech_stack": [
                    "Django",
                    "Django REST Framework",
                    "PostgreSQL",
                    "Redis",
                    "Celery",
                ],
            },
            {
                "title": "Task Queue Dashboard",
                "description": (
                    "<p>Monitoring dashboard for <strong>Celery</strong> task queues. "
                    "Shows real-time task status, worker health, retry counts, "
                    "and historical trends via Chart.js graphs.</p>"
                ),
                "github_url": "https://github.com/bijay-example/task-dashboard",
                "live_url": "",
                "status": Project.Status.ACTIVE,
                "is_featured": False,
                "order": 4,
                "tech_stack": ["Python", "Celery", "Redis", "Docker"],
            },
            {
                "title": "Blog CMS (Legacy)",
                "description": (
                    "<p>An early Django blog project with basic CRUD. "
                    "Retired in favour of the new portfolio blog module.</p>"
                ),
                "github_url": "https://github.com/bijay-example/old-blog",
                "live_url": "",
                "status": Project.Status.ARCHIVED,
                "is_featured": False,
                "order": 0,
                "tech_stack": ["Django", "SQLite"],
            },
        ]

        created_count = 0
        for data in projects_data:
            tech_names = data.pop("tech_stack")
            project, created = Project.objects.get_or_create(
                title=data["title"],
                defaults=data,
            )
            if created:
                tech_objects = [skills[name] for name in tech_names if name in skills]
                project.tech_stack.set(tech_objects)
                created_count += 1

        self.stdout.write(
            f"  Projects: {created_count} created, {len(projects_data) - created_count} skipped."
        )

    # ------------------------------------------------------------------
    # Experience
    # ------------------------------------------------------------------

    def _seed_experience(self) -> None:
        """Create work history entries."""
        entries: list[dict] = [
            {
                "title": "Backend Developer at TechCorp Nepal",
                "company": "TechCorp Nepal",
                "role": "Backend Developer",
                "description": (
                    "Led development of internal REST APIs using Django & DRF. "
                    "Migrated legacy PHP services to Python. Improved API response "
                    "times by 40% via query optimisation and Redis caching."
                ),
                "start_date": date(2023, 3, 1),
                "end_date": None,
                "is_current": True,
                "company_url": "https://techcorp.example.com",
                "location": "Kathmandu, Nepal",
            },
            {
                "title": "Junior Developer at WebSolutions",
                "company": "WebSolutions Pvt. Ltd.",
                "role": "Junior Backend Developer",
                "description": (
                    "Built and maintained Django web apps for clients. "
                    "Implemented user authentication, payment integrations, "
                    "and automated CI/CD with GitHub Actions."
                ),
                "start_date": date(2021, 6, 1),
                "end_date": date(2023, 2, 28),
                "is_current": False,
                "company_url": "https://websolutions.example.com",
                "location": "Lalitpur, Nepal",
            },
            {
                "title": "Intern at DevHouse",
                "company": "DevHouse",
                "role": "Software Engineering Intern",
                "description": (
                    "Worked on a Django-based inventory management system. "
                    "Wrote unit tests, fixed bugs, and learned REST API design "
                    "from senior engineers."
                ),
                "start_date": date(2021, 1, 15),
                "end_date": date(2021, 5, 31),
                "is_current": False,
                "company_url": "https://devhouse.example.com",
                "location": "Remote",
            },
        ]

        created_count = 0
        for data in entries:
            _, created = Experience.objects.get_or_create(
                title=data["title"],
                defaults=data,
            )
            if created:
                created_count += 1

        self.stdout.write(
            f"  Experience: {created_count} created, {len(entries) - created_count} skipped."
        )

    # ------------------------------------------------------------------
    # Education
    # ------------------------------------------------------------------

    def _seed_education(self) -> None:
        """Create education entries."""
        entries: list[dict] = [
            {
                "title": "B.Sc. Computer Science — Tribhuvan University",
                "institution": "Tribhuvan University",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science & Information Technology",
                "start_date": date(2018, 8, 1),
                "end_date": date(2022, 7, 15),
                "description": (
                    "Focused on software engineering, data structures, and algorithms. "
                    "Final year project: RESTful API gateway with load balancing."
                ),
            },
            {
                "title": "Higher Secondary — National School of Sciences",
                "institution": "National School of Sciences",
                "degree": "+2 Science",
                "field_of_study": "Physical Science",
                "start_date": date(2016, 7, 1),
                "end_date": date(2018, 6, 30),
                "description": "",
            },
        ]

        created_count = 0
        for data in entries:
            _, created = Education.objects.get_or_create(
                title=data["title"],
                defaults=data,
            )
            if created:
                created_count += 1

        self.stdout.write(
            f"  Education: {created_count} created, {len(entries) - created_count} skipped."
        )

    # ------------------------------------------------------------------
    # Certifications
    # ------------------------------------------------------------------

    def _seed_certifications(self) -> None:
        """Create certification entries."""
        entries: list[dict] = [
            {
                "title": "AWS Certified Cloud Practitioner",
                "issuer": "Amazon Web Services",
                "issued_date": date(2024, 5, 10),
                "credential_url": "https://aws.amazon.com/verification/example-123",
            },
            {
                "title": "Django for Professionals",
                "issuer": "TestDriven.io",
                "issued_date": date(2023, 11, 20),
                "credential_url": "https://testdriven.io/certificates/example-456",
            },
            {
                "title": "REST API Design Best Practices",
                "issuer": "Coursera / Google",
                "issued_date": date(2023, 3, 5),
                "credential_url": "https://coursera.org/verify/example-789",
            },
        ]

        created_count = 0
        for data in entries:
            _, created = Certification.objects.get_or_create(
                title=data["title"],
                issuer=data["issuer"],
                defaults=data,
            )
            if created:
                created_count += 1

        self.stdout.write(
            f"  Certifications: {created_count} created, {len(entries) - created_count} skipped."
        )

    # ------------------------------------------------------------------
    # Blog Categories
    # ------------------------------------------------------------------

    def _seed_blog_categories(self) -> dict[str, BlogCategory]:
        """Create blog categories.

        Returns:
            Dict mapping category name → BlogCategory instance.
        """
        names: list[dict[str, str]] = [
            {
                "name": "Backend Engineering",
                "meta_description": "Articles about Django, DRF, APIs, databases, and server architecture.",
            },
            {
                "name": "DevOps & Deployment",
                "meta_description": "CI/CD, Docker, Linux server management, and cloud deployment guides.",
            },
            {
                "name": "Career & Learning",
                "meta_description": "Personal reflections on career growth, learning resources, and developer life.",
            },
            {
                "name": "Open Source",
                "meta_description": "Contributing to open source, maintaining libraries, and community work.",
            },
        ]

        cat_map: dict[str, BlogCategory] = {}
        for data in names:
            cat, _ = BlogCategory.objects.get_or_create(
                name=data["name"],
                defaults={"meta_description": data["meta_description"]},
            )
            cat_map[cat.name] = cat

        self.stdout.write(f"  Blog categories: {len(cat_map)} total.")
        return cat_map

    # ------------------------------------------------------------------
    # Blog Tags
    # ------------------------------------------------------------------

    def _seed_blog_tags(self) -> dict[str, BlogTag]:
        """Create blog tags.

        Returns:
            Dict mapping tag name → BlogTag instance.
        """
        tags_data: list[dict[str, str]] = [
            {"name": "Django", "color_hex": "#0C4B33"},
            {"name": "Python", "color_hex": "#3776AB"},
            {"name": "PostgreSQL", "color_hex": "#336791"},
            {"name": "REST API", "color_hex": "#E53E3E"},
            {"name": "Docker", "color_hex": "#2496ED"},
            {"name": "Testing", "color_hex": "#38A169"},
            {"name": "Security", "color_hex": "#D69E2E"},
            {"name": "Performance", "color_hex": "#DD6B20"},
        ]

        tag_map: dict[str, BlogTag] = {}
        for data in tags_data:
            tag, _ = BlogTag.objects.get_or_create(
                name=data["name"],
                defaults={"color_hex": data["color_hex"]},
            )
            tag_map[tag.name] = tag

        self.stdout.write(f"  Blog tags: {len(tag_map)} total.")
        return tag_map

    # ------------------------------------------------------------------
    # Blog Posts
    # ------------------------------------------------------------------

    def _seed_blog_posts(
        self,
        categories: dict[str, BlogCategory],
        tags: dict[str, BlogTag],
    ) -> None:
        """Create blog posts with categories, tags, and related posts.

        Args:
            categories: Dict mapping category name → BlogCategory.
            tags: Dict mapping tag name → BlogTag.
        """
        posts_data: list[dict] = [
            {
                "title": "Building Production-Grade REST APIs with Django",
                "excerpt": (
                    "A comprehensive guide to structuring Django REST Framework projects "
                    "for real-world production use — from serializers to throttling."
                ),
                "content": (
                    "<h2>Why structure matters</h2>"
                    "<p>Most Django tutorials stop at the basics. This post covers "
                    "what happens after the tutorial — response envelopes, error handling, "
                    "pagination, and API documentation with drf-spectacular.</p>"
                    "<h2>Project layout</h2>"
                    "<p>I recommend splitting your project into <code>core/</code> "
                    "(shared), and per-feature apps. Each app owns its models, "
                    "serializers, views, and URLs.</p>"
                    "<h3>Response envelope</h3>"
                    "<p>Wrap every response in a consistent envelope: "
                    "<code>{status, data, message, meta}</code>.</p>"
                    "<h2>Throttling &amp; security</h2>"
                    "<p>Always declare <code>throttle_classes</code> explicitly. "
                    "Set CORS origins per environment — never use "
                    "<code>CORS_ALLOW_ALL_ORIGINS = True</code>.</p>"
                    "<h2>Conclusion</h2>"
                    "<p>Production APIs demand attention to detail. These patterns "
                    "have served me well across multiple projects.</p>"
                ),
                "status": BlogPost.Status.PUBLISHED,
                "is_featured": True,
                "published_at": timezone.now() - timezone.timedelta(days=3),
                "meta_title": "Production-Grade REST APIs with Django | Bijay",
                "meta_description": "Learn how to build scalable, well-structured Django REST APIs for production.",
                "og_title": "Building Production-Grade REST APIs with Django",
                "og_description": "Structure, security, and best practices for Django REST Framework.",
                "categories": ["Backend Engineering"],
                "tags": ["Django", "REST API", "Python", "Security"],
            },
            {
                "title": "PostgreSQL Performance Tips for Django Developers",
                "excerpt": (
                    "Practical PostgreSQL optimisation techniques you can apply today — "
                    "indexing strategies, query analysis, and connection pooling."
                ),
                "content": (
                    "<h2>Before you optimise</h2>"
                    "<p>Always measure first. Use <code>django-debug-toolbar</code> "
                    "and <code>EXPLAIN ANALYZE</code> to find real bottlenecks.</p>"
                    "<h2>Indexing strategies</h2>"
                    "<p>Add indexes for columns used in <code>WHERE</code>, "
                    "<code>ORDER BY</code>, and <code>JOIN</code> clauses. "
                    "Composite indexes should match query column order.</p>"
                    "<h2>select_related vs prefetch_related</h2>"
                    "<p>Use <code>select_related</code> for FK/OneToOne joins, "
                    "<code>prefetch_related</code> for M2M and reverse FKs.</p>"
                    "<h2>Connection pooling</h2>"
                    "<p>Use <code>pgBouncer</code> or "
                    "<code>django-db-connection-pool</code> to avoid "
                    "connection overhead in high-traffic deployments.</p>"
                ),
                "status": BlogPost.Status.PUBLISHED,
                "is_featured": False,
                "published_at": timezone.now() - timezone.timedelta(days=10),
                "meta_title": "PostgreSQL Performance Tips for Django | Bijay",
                "meta_description": "Optimise your Django app's database performance with these PostgreSQL tips.",
                "og_title": "PostgreSQL Performance Tips for Django Developers",
                "og_description": "Indexes, query analysis, and connection pooling for Django + PostgreSQL.",
                "categories": ["Backend Engineering"],
                "tags": ["PostgreSQL", "Django", "Performance"],
            },
            {
                "title": "Docker for Django: A Practical Guide",
                "excerpt": (
                    "Step-by-step guide to containerising a Django application "
                    "with Docker and Docker Compose for local development and production."
                ),
                "content": (
                    "<h2>Why Docker?</h2>"
                    "<p>Reproducible environments, easy onboarding, and consistent "
                    "deployments across dev, staging, and production.</p>"
                    "<h2>Dockerfile</h2>"
                    "<p>Start with <code>python:3.12-slim</code>. Use multi-stage "
                    "builds to keep the final image lean. Install system deps, "
                    "pip install, then copy source code.</p>"
                    "<h2>docker-compose.yml</h2>"
                    "<p>Define services: <code>web</code>, <code>db</code> (PostgreSQL), "
                    "<code>redis</code>. Use volumes for persistent data and "
                    "<code>.env</code> for secrets.</p>"
                    "<h2>Production considerations</h2>"
                    "<p>Use gunicorn as the WSGI server, nginx as reverse proxy, "
                    "and health checks for container orchestration.</p>"
                ),
                "status": BlogPost.Status.PUBLISHED,
                "is_featured": False,
                "published_at": timezone.now() - timezone.timedelta(days=20),
                "meta_title": "Docker for Django: Practical Guide | Bijay",
                "meta_description": "Learn to containerise Django apps with Docker and Compose.",
                "og_title": "Docker for Django: A Practical Guide",
                "og_description": "Containerise your Django app with Docker and Docker Compose.",
                "categories": ["DevOps & Deployment"],
                "tags": ["Docker", "Django", "Python"],
            },
            {
                "title": "Writing Effective Tests for Django REST APIs",
                "excerpt": (
                    "How to write fast, reliable tests for DRF endpoints using "
                    "pytest, factory_boy, and DRF's APIClient."
                ),
                "content": (
                    "<h2>Test structure</h2>"
                    "<p>Organise tests by app: <code>tests/test_models.py</code>, "
                    "<code>tests/test_views.py</code>, <code>tests/test_serializers.py</code>.</p>"
                    "<h2>Factories over fixtures</h2>"
                    "<p>Use <code>factory_boy</code> to generate test data. "
                    "Factories are composable and avoid brittle JSON fixtures.</p>"
                    "<h2>Testing endpoints</h2>"
                    "<p>Use <code>APIClient</code> from DRF. Assert status codes, "
                    "response structure, and data integrity.</p>"
                    "<h2>Coverage goals</h2>"
                    "<p>Aim for 80%+ coverage on business logic. "
                    "Don't test Django internals — trust the framework.</p>"
                ),
                "status": BlogPost.Status.DRAFT,
                "is_featured": False,
                "published_at": None,
                "meta_title": "",
                "meta_description": "",
                "og_title": "",
                "og_description": "",
                "categories": ["Backend Engineering"],
                "tags": ["Django", "Testing", "Python"],
            },
        ]

        created_posts: list[BlogPost] = []
        for data in posts_data:
            cat_names = data.pop("categories")
            tag_names = data.pop("tags")

            post, created = BlogPost.objects.get_or_create(
                title=data["title"],
                defaults=data,
            )
            if created:
                post.categories.set(
                    [categories[n] for n in cat_names if n in categories]
                )
                post.tags.set([tags[n] for n in tag_names if n in tags])
                created_posts.append(post)

        # Link related posts (first two reference each other)
        if len(created_posts) >= 2:
            created_posts[0].related_posts.add(created_posts[1])
            created_posts[1].related_posts.add(created_posts[0])

        self.stdout.write(
            f"  Blog posts: {len(created_posts)} created, {len(posts_data) - len(created_posts)} skipped."
        )

    # ------------------------------------------------------------------
    # Reading List
    # ------------------------------------------------------------------

    def _seed_reading_list(self) -> None:
        """Create reading list items."""
        items: list[dict] = [
            {
                "heading": "The Twelve-Factor App",
                "url": "https://12factor.net/",
                "added_date": date(2025, 12, 1),
            },
            {
                "heading": "Django Performance Optimization Tips — Real Python",
                "url": "https://realpython.com/django-performance-optimization/",
                "added_date": date(2025, 11, 15),
            },
            {
                "heading": "Designing Data-Intensive Applications (DDIA) Notes",
                "url": "https://dataintensive.net/",
                "added_date": date(2025, 10, 20),
            },
            {
                "heading": "How to build an API that developers love",
                "url": "https://blog.stoplight.io/api-design-best-practices",
                "added_date": date(2025, 9, 5),
            },
        ]

        created_count = 0
        for data in items:
            _, created = ReadingList.objects.get_or_create(
                heading=data["heading"],
                defaults=data,
            )
            if created:
                created_count += 1

        self.stdout.write(
            f"  Reading list: {created_count} created, {len(items) - created_count} skipped."
        )

    # ------------------------------------------------------------------
    # Thoughts
    # ------------------------------------------------------------------

    def _seed_thoughts(self) -> None:
        """Create short thought entries."""
        items: list[dict[str, str]] = [
            {
                "title": "On writing clean code",
                "description": (
                    "Clean code isn't about being clever — it's about being kind "
                    "to the next person who reads it (including future you)."
                ),
            },
            {
                "title": "APIs are products",
                "description": (
                    "Treat your API like a product: consistent naming, predictable "
                    "responses, proper error messages, and great documentation."
                ),
            },
            {
                "title": "The value of side projects",
                "description": (
                    "Side projects forced me to learn Docker, CI/CD, and proper "
                    "deployment — things no tutorial taught me properly."
                ),
            },
            {
                "title": "PostgreSQL is underrated",
                "description": (
                    "Every time I learn a new PostgreSQL feature (CTEs, window functions, "
                    "partial indexes), I'm amazed at how much work it can do for you."
                ),
            },
            {
                "title": "Documentation as a first-class citizen",
                "description": (
                    "If your API isn't documented, it doesn't exist. "
                    "drf-spectacular + Swagger UI changed how I think about API design."
                ),
            },
        ]

        created_count = 0
        for data in items:
            _, created = Thought.objects.get_or_create(
                title=data["title"],
                defaults=data,
            )
            if created:
                created_count += 1

        self.stdout.write(
            f"  Thoughts: {created_count} created, {len(items) - created_count} skipped."
        )

    # ------------------------------------------------------------------
    # Books
    # ------------------------------------------------------------------

    def _seed_books(self) -> None:
        """Create book entries with reading progress."""
        items: list[dict] = [
            {
                "title": "Designing Data-Intensive Applications",
                "author": "Martin Kleppmann",
                "date_started": date(2025, 8, 1),
                "percent_read": 72,
                "summary": (
                    "Foundational read on distributed systems, replication, "
                    "partitioning, and stream processing. Dense but incredibly rewarding."
                ),
            },
            {
                "title": "Two Scoops of Django",
                "author": "Audrey & Daniel Feldroy",
                "date_started": date(2024, 5, 10),
                "percent_read": 100,
                "summary": (
                    "Best practices for Django development. Covers project structure, "
                    "security, testing, and deployment. A must-read for Django devs."
                ),
            },
            {
                "title": "Clean Code",
                "author": "Robert C. Martin",
                "date_started": date(2024, 1, 15),
                "percent_read": 100,
                "summary": (
                    "Classic software engineering book on writing readable, "
                    "maintainable code. Some examples are Java-heavy but "
                    "the principles are universal."
                ),
            },
            {
                "title": "The Pragmatic Programmer",
                "author": "David Thomas & Andrew Hunt",
                "date_started": date(2025, 11, 1),
                "percent_read": 35,
                "summary": (
                    "Currently reading. Great insights on professional software "
                    "development, from DRY principles to career advice."
                ),
            },
        ]

        created_count = 0
        for data in items:
            _, created = Book.objects.get_or_create(
                title=data["title"],
                author=data["author"],
                defaults=data,
            )
            if created:
                created_count += 1

        self.stdout.write(
            f"  Books: {created_count} created, {len(items) - created_count} skipped."
        )

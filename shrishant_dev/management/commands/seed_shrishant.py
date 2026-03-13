"""Management command to seed shrishant_dev with realistic portfolio data.

Usage:
    python manage.py seed_shrishant          — create seed data (skip if already present)
    python manage.py seed_shrishant --flush  — delete existing shrishant_dev data, then re-seed
"""

from __future__ import annotations

import logging
from datetime import date

from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone

from shrishant_dev.models import (
    BlogCategory,
    BlogPost,
    BlogTag,
    Certification,
    Education,
    Experience,
    Project,
    ProjectImage,
    SkillCategory,
    TechStack,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Seed the shrishant_dev app with realistic frontend portfolio data."""

    help = "Populate shrishant_dev with realistic seed data across all 10 models."

    def add_arguments(self, parser: CommandParser) -> None:
        """Register optional --flush flag.

        Args:
            parser: The argument parser instance.
        """
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing shrishant_dev data before seeding.",
        )

    def handle(self, *args: object, **kwargs: object) -> None:
        """Execute the seed logic.

        Args:
            *args: Positional arguments (unused).
            **kwargs: Parsed keyword arguments including 'flush'.
        """
        flush: bool = kwargs["flush"]

        if flush:
            self.stdout.write(self.style.WARNING("Flushing shrishant_dev data..."))
            self._flush_all()
            self.stdout.write(self.style.SUCCESS("shrishant_dev data flushed."))

        skills = self._seed_skill_categories_and_tech_stack()
        self._seed_projects(skills)
        self._seed_experience()
        self._seed_education()
        self._seed_certifications()
        categories = self._seed_blog_categories()
        tags = self._seed_blog_tags()
        self._seed_blog_posts(categories, tags)

        self.stdout.write(self.style.SUCCESS("\nshrishant_dev seed complete."))

    # ------------------------------------------------------------------
    # Flush
    # ------------------------------------------------------------------

    def _flush_all(self) -> None:
        """Delete all shrishant_dev data in dependency-safe order."""
        BlogPost.objects.all().delete()
        BlogTag.objects.all().delete()
        BlogCategory.objects.all().delete()
        ProjectImage.objects.all().delete()
        Project.objects.all().delete()
        TechStack.objects.all().delete()
        SkillCategory.objects.all().delete()
        Experience.objects.all().delete()
        Education.objects.all().delete()
        Certification.objects.all().delete()

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
                "name": "Languages",
                "order": 1,
                "skills": [
                    {
                        "name": "JavaScript",
                        "icon_cdn": "https://api.iconify.design/logos:javascript.svg",
                        "is_featured": True,
                        "order": 1,
                    },
                    {
                        "name": "TypeScript",
                        "icon_cdn": "https://api.iconify.design/logos:typescript-icon.svg",
                        "is_featured": True,
                        "order": 2,
                    },
                    {
                        "name": "HTML5",
                        "icon_cdn": "https://api.iconify.design/logos:html-5.svg",
                        "is_featured": False,
                        "order": 3,
                    },
                    {
                        "name": "CSS3",
                        "icon_cdn": "https://api.iconify.design/logos:css-3.svg",
                        "is_featured": False,
                        "order": 4,
                    },
                ],
            },
            {
                "name": "Frameworks & Libraries",
                "order": 2,
                "skills": [
                    {
                        "name": "React",
                        "icon_cdn": "https://api.iconify.design/logos:react.svg",
                        "is_featured": True,
                        "order": 1,
                    },
                    {
                        "name": "Next.js",
                        "icon_cdn": "https://api.iconify.design/logos:nextjs-icon.svg",
                        "is_featured": True,
                        "order": 2,
                    },
                    {
                        "name": "Vue.js",
                        "icon_cdn": "https://api.iconify.design/logos:vue.svg",
                        "is_featured": False,
                        "order": 3,
                    },
                    {
                        "name": "Svelte",
                        "icon_cdn": "https://api.iconify.design/logos:svelte-icon.svg",
                        "is_featured": False,
                        "order": 4,
                    },
                ],
            },
            {
                "name": "Styling",
                "order": 3,
                "skills": [
                    {
                        "name": "Tailwind CSS",
                        "icon_cdn": "https://api.iconify.design/logos:tailwindcss-icon.svg",
                        "is_featured": True,
                        "order": 1,
                    },
                    {
                        "name": "Sass / SCSS",
                        "icon_cdn": "https://api.iconify.design/logos:sass.svg",
                        "is_featured": False,
                        "order": 2,
                    },
                    {
                        "name": "Styled Components",
                        "icon_cdn": "https://api.iconify.design/simple-icons:styledcomponents.svg",
                        "is_featured": False,
                        "order": 3,
                    },
                    {
                        "name": "Framer Motion",
                        "icon_cdn": "https://api.iconify.design/simple-icons:framer.svg",
                        "is_featured": False,
                        "order": 4,
                    },
                ],
            },
            {
                "name": "Build Tools & Bundlers",
                "order": 4,
                "skills": [
                    {
                        "name": "Vite",
                        "icon_cdn": "https://api.iconify.design/logos:vitejs.svg",
                        "is_featured": False,
                        "order": 1,
                    },
                    {
                        "name": "Webpack",
                        "icon_cdn": "https://api.iconify.design/logos:webpack.svg",
                        "is_featured": False,
                        "order": 2,
                    },
                    {
                        "name": "ESLint / Prettier",
                        "icon_cdn": "https://api.iconify.design/logos:eslint.svg",
                        "is_featured": False,
                        "order": 3,
                    },
                    {
                        "name": "Turborepo",
                        "icon_cdn": "https://api.iconify.design/simple-icons:turborepo.svg",
                        "is_featured": False,
                        "order": 4,
                    },
                ],
            },
            {
                "name": "Testing",
                "order": 5,
                "skills": [
                    {
                        "name": "Jest",
                        "icon_cdn": "https://api.iconify.design/simple-icons:jest.svg",
                        "is_featured": False,
                        "order": 1,
                    },
                    {
                        "name": "React Testing Library",
                        "icon_cdn": "https://api.iconify.design/simple-icons:testinglibrary.svg",
                        "is_featured": False,
                        "order": 2,
                    },
                    {
                        "name": "Cypress",
                        "icon_cdn": "https://api.iconify.design/simple-icons:cypress.svg",
                        "is_featured": False,
                        "order": 3,
                    },
                    {
                        "name": "Playwright",
                        "icon_cdn": "https://api.iconify.design/simple-icons:playwright.svg",
                        "is_featured": False,
                        "order": 4,
                    },
                ],
            },
            {
                "name": "Tools & Workflow",
                "order": 6,
                "skills": [
                    {
                        "name": "Git",
                        "icon_cdn": "https://api.iconify.design/logos:git-icon.svg",
                        "is_featured": False,
                        "order": 1,
                    },
                    {
                        "name": "VS Code",
                        "icon_cdn": "https://api.iconify.design/logos:visual-studio-code.svg",
                        "is_featured": False,
                        "order": 2,
                    },
                    {
                        "name": "Figma",
                        "icon_cdn": "https://api.iconify.design/logos:figma.svg",
                        "is_featured": False,
                        "order": 3,
                    },
                    {
                        "name": "Vercel",
                        "icon_cdn": "https://api.iconify.design/logos:vercel-icon.svg",
                        "is_featured": False,
                        "order": 4,
                    },
                    {
                        "name": "Docker",
                        "icon_cdn": "https://api.iconify.design/logos:docker-icon.svg",
                        "is_featured": False,
                        "order": 5,
                    },
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
                        "icon_cdn": skill_data["icon_cdn"],
                        "is_featured": skill_data["is_featured"],
                        "order": skill_data["order"],
                    },
                )
                if tech.icon_cdn != skill_data["icon_cdn"]:
                    tech.icon_cdn = skill_data["icon_cdn"]
                    tech.save(update_fields=["icon_cdn", "updated_at"])
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
        """Create portfolio projects with M2M tech stack links and gallery images.

        Args:
            skills: Dict mapping skill name → TechStack instance.
        """
        projects_data: list[dict] = [
            {
                "title": "Developer Portfolio",
                "description": (
                    "<p>A modern, responsive <strong>developer portfolio</strong> built "
                    "with Next.js 14 and Tailwind CSS. Features dark mode, smooth "
                    "page transitions with Framer Motion, server-side rendering, "
                    "and a headless CMS integration.</p>"
                ),
                "github_url": "https://github.com/shrishant-example/portfolio",
                "live_url": "https://shrishant.dev",
                "status": Project.Status.ACTIVE,
                "is_featured": True,
                "order": 1,
                "tech_stack": [
                    "Next.js",
                    "TypeScript",
                    "Tailwind CSS",
                    "Framer Motion",
                ],
                "images": [
                    {
                        "caption": "Homepage hero section with animated gradient",
                        "alt_text": "Portfolio homepage showing hero section",
                        "order": 1,
                    },
                    {
                        "caption": "Projects grid with hover effects",
                        "alt_text": "Portfolio projects page showing card grid",
                        "order": 2,
                    },
                ],
            },
            {
                "title": "E-Commerce Storefront",
                "description": (
                    "<p>A full <strong>e-commerce storefront</strong> with product "
                    "listing, filtering, cart management, and Stripe checkout. "
                    "Uses React Query for server-state caching and Zustand for "
                    "client-side cart state.</p>"
                ),
                "github_url": "https://github.com/shrishant-example/ecom-store",
                "live_url": "https://store.shrishant.dev",
                "status": Project.Status.ACTIVE,
                "is_featured": True,
                "order": 2,
                "tech_stack": [
                    "React",
                    "TypeScript",
                    "Tailwind CSS",
                    "Vite",
                ],
                "images": [
                    {
                        "caption": "Product listing page with sidebar filters",
                        "alt_text": "Store product listing with category filters",
                        "order": 1,
                    },
                    {
                        "caption": "Cart drawer with quantity controls",
                        "alt_text": "Shopping cart slide-over panel",
                        "order": 2,
                    },
                    {
                        "caption": "Stripe checkout integration",
                        "alt_text": "Checkout page with Stripe payment form",
                        "order": 3,
                    },
                ],
            },
            {
                "title": "Real-Time Dashboard",
                "description": (
                    "<p>An analytics <strong>dashboard</strong> featuring live-updating "
                    "charts, WebSocket data feeds, and responsive data tables. "
                    "Built with React, Recharts, and a custom hook system for "
                    "WebSocket state management.</p>"
                ),
                "github_url": "https://github.com/shrishant-example/realtime-dash",
                "live_url": "https://dash.shrishant.dev",
                "status": Project.Status.ACTIVE,
                "is_featured": True,
                "order": 3,
                "tech_stack": [
                    "React",
                    "TypeScript",
                    "Styled Components",
                    "Vite",
                ],
                "images": [
                    {
                        "caption": "Main dashboard view with KPI cards and charts",
                        "alt_text": "Dashboard overview with metrics and line charts",
                        "order": 1,
                    },
                ],
            },
            {
                "title": "Component Library",
                "description": (
                    "<p>A reusable <strong>React component library</strong> published "
                    "to npm. Includes buttons, modals, form controls, and layout "
                    "primitives. Documented with Storybook and tested with "
                    "React Testing Library + Jest.</p>"
                ),
                "github_url": "https://github.com/shrishant-example/ui-kit",
                "live_url": "https://ui.shrishant.dev",
                "status": Project.Status.ACTIVE,
                "is_featured": False,
                "order": 4,
                "tech_stack": [
                    "React",
                    "TypeScript",
                    "Sass / SCSS",
                    "Jest",
                    "React Testing Library",
                ],
                "images": [
                    {
                        "caption": "Storybook documentation for Button component",
                        "alt_text": "Storybook page showing button variants",
                        "order": 1,
                    },
                ],
            },
            {
                "title": "Blog Starter (Legacy)",
                "description": (
                    "<p>An early blog project built with Gatsby and Markdown. "
                    "Replaced by the current Next.js portfolio blog module. "
                    "Kept for reference.</p>"
                ),
                "github_url": "https://github.com/shrishant-example/old-blog",
                "live_url": "",
                "status": Project.Status.ARCHIVED,
                "is_featured": False,
                "order": 0,
                "tech_stack": ["JavaScript", "CSS3"],
                "images": [],
            },
        ]

        created_count = 0
        for data in projects_data:
            tech_names = data.pop("tech_stack")
            images_data = data.pop("images")
            project, created = Project.objects.get_or_create(
                title=data["title"],
                defaults=data,
            )
            if created:
                tech_objects = [skills[name] for name in tech_names if name in skills]
                project.tech_stack.set(tech_objects)
                for img_data in images_data:
                    ProjectImage.objects.create(
                        project=project,
                        caption=img_data["caption"],
                        alt_text=img_data["alt_text"],
                        order=img_data["order"],
                    )
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
                "title": "Frontend Developer at PixelCraft Agency",
                "company": "PixelCraft Agency",
                "role": "Frontend Developer",
                "description": (
                    "Lead frontend development for client projects using React "
                    "and Next.js. Implemented design systems, improved Core Web "
                    "Vitals scores by 30%, and mentored junior developers on "
                    "component architecture and TypeScript best practices."
                ),
                "start_date": date(2023, 6, 1),
                "end_date": None,
                "is_current": True,
                "company_url": "https://pixelcraft.example.com",
                "location": "Kathmandu, Nepal",
            },
            {
                "title": "Junior Frontend Developer at WebWorks",
                "company": "WebWorks Pvt. Ltd.",
                "role": "Junior Frontend Developer",
                "description": (
                    "Built responsive landing pages and SPAs for small business "
                    "clients. Migrated legacy jQuery codebases to React. "
                    "Implemented accessibility improvements achieving WCAG 2.1 AA."
                ),
                "start_date": date(2022, 1, 1),
                "end_date": date(2023, 5, 31),
                "is_current": False,
                "company_url": "https://webworks.example.com",
                "location": "Lalitpur, Nepal",
            },
            {
                "title": "Frontend Intern at StartupHub",
                "company": "StartupHub",
                "role": "Frontend Engineering Intern",
                "description": (
                    "Contributed to a SaaS dashboard built with Vue.js. "
                    "Wrote unit tests, implemented responsive layouts, and "
                    "learned modern CSS architecture from senior engineers."
                ),
                "start_date": date(2021, 7, 1),
                "end_date": date(2021, 12, 31),
                "is_current": False,
                "company_url": "https://startuphub.example.com",
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
                    "Focused on web technologies, HCI, and software engineering. "
                    "Final year project: Accessible component library for Nepali "
                    "government web portals."
                ),
            },
            {
                "title": "Higher Secondary — SOS Hermann Gmeiner School",
                "institution": "SOS Hermann Gmeiner School",
                "degree": "+2 Science",
                "field_of_study": "Computer Science",
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
                "title": "Meta Front-End Developer Professional Certificate",
                "issuer": "Meta (via Coursera)",
                "issued_date": date(2024, 2, 15),
                "credential_url": "https://coursera.org/verify/professional-cert/example-meta-fe",
            },
            {
                "title": "JavaScript Algorithms and Data Structures",
                "issuer": "freeCodeCamp",
                "issued_date": date(2023, 9, 10),
                "credential_url": "https://freecodecamp.org/certification/shrishant/javascript-algorithms",
            },
            {
                "title": "Responsive Web Design",
                "issuer": "freeCodeCamp",
                "issued_date": date(2023, 4, 20),
                "credential_url": "https://freecodecamp.org/certification/shrishant/responsive-web-design",
            },
            {
                "title": "React — The Complete Guide",
                "issuer": "Udemy (Maximilian Schwarzmüller)",
                "issued_date": date(2022, 11, 5),
                "credential_url": "https://udemy.com/certificate/example-react-complete",
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
                "name": "Frontend Engineering",
                "meta_description": "Articles on React, Next.js, TypeScript, component architecture, and modern frontend patterns.",
            },
            {
                "name": "CSS & Styling",
                "meta_description": "Deep dives into Tailwind CSS, CSS Grid, animations, responsive design, and styling strategies.",
            },
            {
                "name": "Performance & Accessibility",
                "meta_description": "Core Web Vitals, Lighthouse audits, WCAG compliance, and frontend performance optimisation.",
            },
            {
                "name": "Career & Learning",
                "meta_description": "Personal reflections on learning frontend engineering, career growth, and developer life.",
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
            {"name": "React", "color_hex": "#61DAFB"},
            {"name": "Next.js", "color_hex": "#000000"},
            {"name": "TypeScript", "color_hex": "#3178C6"},
            {"name": "Tailwind CSS", "color_hex": "#06B6D4"},
            {"name": "Performance", "color_hex": "#DD6B20"},
            {"name": "Accessibility", "color_hex": "#38A169"},
            {"name": "CSS", "color_hex": "#1572B6"},
            {"name": "Testing", "color_hex": "#C21325"},
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
                "title": "Building Accessible React Components from Scratch",
                "excerpt": (
                    "A practical guide to building keyboard-navigable, screen-reader-friendly "
                    "React components — covering ARIA roles, focus management, and testing."
                ),
                "content": (
                    "<h2>Why accessibility matters</h2>"
                    "<p>Over 1 billion people worldwide live with some form of disability. "
                    "Writing accessible frontends isn't optional — it's a responsibility.</p>"
                    "<h2>ARIA roles and attributes</h2>"
                    "<p>Use <code>role</code>, <code>aria-label</code>, and "
                    "<code>aria-expanded</code> to expose the UI structure to assistive "
                    "technologies. Don't overuse ARIA — native HTML elements are preferable.</p>"
                    "<h2>Focus management</h2>"
                    "<p>Trap focus inside modals, move focus to new content on route "
                    "changes, and use <code>tabIndex</code> wisely. Never remove the "
                    "focus outline without providing an alternative.</p>"
                    "<h2>Testing accessibility</h2>"
                    "<p>Use <code>jest-axe</code> for automated checks, "
                    "<code>Testing Library</code> queries like <code>getByRole</code>, "
                    "and manual screen-reader testing with VoiceOver or NVDA.</p>"
                    "<h2>Conclusion</h2>"
                    "<p>Accessibility is an iterative journey. Start with semantic HTML, "
                    "add ARIA where needed, and test with real assistive tools.</p>"
                ),
                "status": BlogPost.Status.PUBLISHED,
                "is_featured": True,
                "published_at": timezone.now() - timezone.timedelta(days=5),
                "meta_title": "Building Accessible React Components | Shrishant",
                "meta_description": "Learn to build keyboard-navigable, WCAG-compliant React components.",
                "og_title": "Building Accessible React Components from Scratch",
                "og_description": "ARIA roles, focus management, and accessibility testing in React.",
                "categories": ["Frontend Engineering", "Performance & Accessibility"],
                "tags": ["React", "Accessibility", "TypeScript"],
            },
            {
                "title": "Tailwind CSS Tips I Wish I Knew Earlier",
                "excerpt": (
                    "Practical Tailwind CSS patterns that improved my workflow — "
                    "from design tokens to responsive utilities to custom plugins."
                ),
                "content": (
                    "<h2>Design tokens in tailwind.config</h2>"
                    "<p>Define your colour palette, spacing scale, and typography "
                    "in <code>tailwind.config.ts</code>. Extend the default theme "
                    "rather than overriding it to keep utility classes intact.</p>"
                    "<h2>Responsive utilities</h2>"
                    "<p>Mobile-first is Tailwind's default. Use <code>sm:</code>, "
                    "<code>md:</code>, <code>lg:</code> prefixes intentionally. "
                    "Avoid adding breakpoints you don't need.</p>"
                    "<h2>Component extraction</h2>"
                    "<p>When a class list gets too long, extract it into a React "
                    "component — not <code>@apply</code>. <code>@apply</code> breaks "
                    "the utility-first philosophy and makes refactoring harder.</p>"
                    "<h2>Dark mode</h2>"
                    "<p>Use <code>dark:</code> variant with <code>class</code> strategy "
                    "for full control. Store the user preference in "
                    "<code>localStorage</code> and sync with system preference.</p>"
                    "<h2>Custom plugins</h2>"
                    "<p>Write Tailwind plugins for project-specific utilities: "
                    "text gradients, scrollbar styling, or glassmorphism effects.</p>"
                ),
                "status": BlogPost.Status.PUBLISHED,
                "is_featured": False,
                "published_at": timezone.now() - timezone.timedelta(days=12),
                "meta_title": "Tailwind CSS Tips I Wish I Knew | Shrishant",
                "meta_description": "Practical Tailwind CSS patterns for design tokens, responsive utilities, and plugins.",
                "og_title": "Tailwind CSS Tips I Wish I Knew Earlier",
                "og_description": "Design tokens, dark mode, and custom plugins for Tailwind CSS.",
                "categories": ["CSS & Styling"],
                "tags": ["Tailwind CSS", "CSS"],
            },
            {
                "title": "Server Components in Next.js 14: A Deep Dive",
                "excerpt": (
                    "Understanding React Server Components in Next.js 14 — when to use "
                    "them, how they affect bundle size, and migration patterns."
                ),
                "content": (
                    "<h2>What are Server Components?</h2>"
                    "<p>Server Components render on the server and send HTML to the "
                    "client. They never ship JavaScript to the browser, reducing "
                    "bundle size dramatically.</p>"
                    "<h2>When to use them</h2>"
                    "<p>Use Server Components for data fetching, static content, "
                    "and layouts. Switch to Client Components (<code>'use client'</code>) "
                    "for interactivity: event handlers, hooks, and browser APIs.</p>"
                    "<h2>Data fetching patterns</h2>"
                    "<p>Fetch data directly in Server Components with <code>async</code> "
                    "functions. No need for <code>useEffect</code> or client-side "
                    "caching for initial page data.</p>"
                    "<h2>Migration strategy</h2>"
                    "<p>Start by making page-level components server-rendered. "
                    "Pull interactive parts into small Client Component islands. "
                    "Use <code>Suspense</code> boundaries for loading states.</p>"
                    "<h2>Performance wins</h2>"
                    "<p>After migrating our dashboard, initial JS bundle dropped "
                    "by 42%. Time to interactive improved by 1.2 seconds on mobile.</p>"
                ),
                "status": BlogPost.Status.PUBLISHED,
                "is_featured": False,
                "published_at": timezone.now() - timezone.timedelta(days=22),
                "meta_title": "Server Components in Next.js 14 | Shrishant",
                "meta_description": "Deep dive into React Server Components in Next.js 14 — patterns and migration.",
                "og_title": "Server Components in Next.js 14: A Deep Dive",
                "og_description": "Server vs Client Components, data fetching, and migration patterns.",
                "categories": ["Frontend Engineering"],
                "tags": ["Next.js", "React", "TypeScript", "Performance"],
            },
            {
                "title": "Writing Reliable Frontend Tests with Playwright",
                "excerpt": (
                    "How to set up Playwright for end-to-end testing of modern "
                    "frontend apps — from configuration to CI integration."
                ),
                "content": (
                    "<h2>Why Playwright?</h2>"
                    "<p>Playwright runs tests in real browsers (Chromium, Firefox, "
                    "WebKit). It's faster than Selenium, auto-waits for elements, "
                    "and has first-class TypeScript support.</p>"
                    "<h2>Configuration</h2>"
                    "<p>Configure <code>playwright.config.ts</code> with base URL, "
                    "browser projects, and parallel workers. Use "
                    "<code>webServer</code> to auto-start your dev server.</p>"
                    "<h2>Writing tests</h2>"
                    "<p>Use locators like <code>getByRole</code> and "
                    "<code>getByText</code> for resilient selectors. Avoid "
                    "CSS selectors tied to implementation details.</p>"
                    "<h2>CI integration</h2>"
                    "<p>Run Playwright in GitHub Actions with a matrix of browsers. "
                    "Use <code>--shard</code> to parallelise across runners. "
                    "Archive trace files for debugging failures.</p>"
                ),
                "status": BlogPost.Status.DRAFT,
                "is_featured": False,
                "published_at": None,
                "meta_title": "",
                "meta_description": "",
                "og_title": "",
                "og_description": "",
                "categories": ["Frontend Engineering"],
                "tags": ["Testing", "TypeScript"],
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

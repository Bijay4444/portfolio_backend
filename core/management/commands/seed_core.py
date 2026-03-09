"""Management command to seed the core app with realistic test data.

Usage:
    python manage.py seed_core          — create seed data (skip if already present)
    python manage.py seed_core --flush  — delete existing core data, then re-seed
"""

from __future__ import annotations

import logging

from django.core.management.base import BaseCommand, CommandParser

from core.models import ContactSubmission, Profile, SocialLink

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Seed the core app with a Profile, SocialLinks, and ContactSubmissions."""

    help = "Populate the core app with realistic seed data for frontend testing."

    def add_arguments(self, parser: CommandParser) -> None:
        """Register optional --flush flag.

        Args:
            parser: The argument parser instance.
        """
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing core data before seeding.",
        )

    def handle(self, *args: object, **kwargs: object) -> None:
        """Execute the seed logic.

        Args:
            *args: Positional arguments (unused).
            **kwargs: Parsed keyword arguments including 'flush'.
        """
        flush: bool = kwargs["flush"]

        if flush:
            self.stdout.write(self.style.WARNING("Flushing core data..."))
            ContactSubmission.objects.all().delete()
            SocialLink.objects.all().delete()
            Profile.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Core data flushed."))

        profile = self._seed_profile()
        self._seed_social_links(profile)
        self._seed_contact_submissions()

        self.stdout.write(self.style.SUCCESS("Core seed complete."))

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    def _seed_profile(self) -> Profile:
        """Create the singleton Profile if it does not exist.

        Returns:
            The existing or newly created Profile instance.
        """
        if Profile.objects.exists():
            profile = Profile.objects.first()
            self.stdout.write(f"  Profile already exists: {profile}")
            return profile

        profile = Profile(
            full_name="Bijay Adhikari",
            tagline="Backend Engineer — building APIs that scale.",
            bio=(
                "<p>I'm a backend developer from Kathmandu, Nepal, specialising in "
                "<strong>Django</strong>, <strong>PostgreSQL</strong>, and "
                "<strong>REST API</strong> design. I enjoy solving hard problems "
                "with clean, well-tested code.</p>"
            ),
            role="Backend Engineer",
            email="bijay@example.com",
            phone="+977-9800000000",
            location="Kathmandu, Nepal",
            is_available=True,
        )
        profile.full_clean()
        profile.save()
        self.stdout.write(self.style.SUCCESS(f"  Created Profile: {profile}"))
        return profile

    # ------------------------------------------------------------------
    # Social Links
    # ------------------------------------------------------------------

    def _seed_social_links(self, profile: Profile) -> None:
        """Create social links for the profile.

        Args:
            profile: The Profile instance to attach links to.
        """
        links_data: list[dict[str, str | bool]] = [
            {
                "platform": SocialLink.Platform.GITHUB,
                "url": "https://github.com/bijay-example",
                "is_active": True,
            },
            {
                "platform": SocialLink.Platform.LINKEDIN,
                "url": "https://linkedin.com/in/bijay-example",
                "is_active": True,
            },
            {
                "platform": SocialLink.Platform.TWITTER,
                "url": "https://twitter.com/bijay_example",
                "is_active": True,
            },
            {
                "platform": SocialLink.Platform.DEVTO,
                "url": "https://dev.to/bijay-example",
                "is_active": True,
            },
            {
                "platform": SocialLink.Platform.MEDIUM,
                "url": "https://medium.com/@bijay-example",
                "is_active": False,
            },
        ]

        created_count = 0
        for data in links_data:
            _, created = SocialLink.objects.get_or_create(
                profile=profile,
                platform=data["platform"],
                defaults={"url": data["url"], "is_active": data["is_active"]},
            )
            if created:
                created_count += 1

        self.stdout.write(
            f"  Social links — {created_count} created, {len(links_data) - created_count} skipped."
        )

    # ------------------------------------------------------------------
    # Contact Submissions
    # ------------------------------------------------------------------

    def _seed_contact_submissions(self) -> None:
        """Create sample contact form submissions."""
        if ContactSubmission.objects.count() >= 3:
            self.stdout.write("  Contact submissions already seeded — skipping.")
            return

        submissions = [
            {
                "full_name": "Alice Johnson",
                "email": "alice@example.com",
                "subject": "Freelance project inquiry",
                "message": (
                    "Hi Bijay, I came across your portfolio and was impressed with "
                    "your API work. Would you be available for a 3-month freelance "
                    "engagement building a REST API for our SaaS platform?"
                ),
                "is_read": True,
            },
            {
                "full_name": "Bob Sharma",
                "email": "bob.sharma@example.com",
                "subject": "Speaking opportunity",
                "message": (
                    "Hello! We're organising a backend engineering meetup in Kathmandu "
                    "next month and would love to have you speak about Django best "
                    "practices. Let me know if you're interested!"
                ),
                "is_read": False,
            },
            {
                "full_name": "Charlie Gurung",
                "email": "charlie.g@example.com",
                "subject": "Open-source collaboration",
                "message": (
                    "Hey Bijay, I'm working on an open-source Django library for "
                    "rate limiting and noticed you're passionate about backend security. "
                    "Would love to collaborate!"
                ),
                "is_read": False,
            },
        ]

        for data in submissions:
            ContactSubmission.objects.create(**data)

        self.stdout.write(
            self.style.SUCCESS(f"  Created {len(submissions)} contact submissions.")
        )

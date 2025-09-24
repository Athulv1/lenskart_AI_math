import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from app.models import Project
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Deletes projects older than a specified number of months (default: 2).'

    def add_arguments(self, parser):
        parser.add_argument('--months', type=int, default=2, help='Specify the number of months of data to keep.')
        parser.add_argument('--dry-run', action='store_true', help='Simulate the command without deleting anything.')

    def handle(self, *args, **options):
        months_to_keep = options['months']
        dry_run = options['dry_run']

        if months_to_keep < 1:
            raise CommandError("Number of months must be at least 1.")

        cutoff_date = timezone.now() - relativedelta(months=months_to_keep)
        self.stdout.write(f"Searching for projects created before {cutoff_date.strftime('%Y-%m-%d %H:%M:%S %Z')}...")

        projects_to_delete = Project.objects.filter(created_at__lt=cutoff_date)
        project_count = projects_to_delete.count()

        if project_count == 0:
            self.stdout.write(self.style.SUCCESS("No old projects found to delete."))
            return

        self.stdout.write(self.style.WARNING(f"Found {project_count} project(s) to delete."))
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS("DRY RUN: No projects will be deleted."))
            for project in projects_to_delete:
                self.stdout.write(f"  - (Dry Run) Would delete project: '{project.name}' (ID: {project.id}, Created: {project.created_at.strftime('%Y-%m-%d')})")
            return

        confirm = input(f"Are you sure you want to permanently delete these {project_count} projects and all their associated files? (yes/no): ")

        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR("Operation cancelled by user."))
            return

        deleted_count, _ = projects_to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} project(s)."))

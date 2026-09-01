"""
WSGI config for painaima_core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "painaima_core.settings")

# Handle Vercel serverless database initialization
if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
    try:
        import django
        django.setup()
        from django.core.management import call_command
        from django.contrib.sites.models import Site
        
        # Run migrations on writable /tmp directory
        call_command("migrate", interactive=False)
        
        # Ensure Site object with ID=1 exists for allauth
        site, _ = Site.objects.get_or_create(id=1, defaults={"domain": "painaima.vercel.app", "name": "Painaima"})
        if site.domain != "painaima.vercel.app":
            site.domain = "painaima.vercel.app"
            site.save()
    except Exception as e:
        print("Vercel DB setup error:", e)

application = get_wsgi_application()
app = application

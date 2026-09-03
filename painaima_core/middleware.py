import traceback
from django.http import HttpResponse
from django.conf import settings


class ExceptionDiagnosticMiddleware:
    """Middleware to catch and display detailed exception tracebacks for debugging."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        tb = traceback.format_exc()
        print(f"=== UNCAUGHT EXCEPTION AT {request.path} ===")
        print(tb)

        # Provide diagnostic info on error
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Painaima Diagnostic Error</title>
</head>
<body style="background:#0f172a; color:#f8fafc; font-family:system-ui,-apple-system,sans-serif; padding:30px; line-height:1.6;">
    <div style="max-width:800px; margin:0 auto; background:#1e293b; padding:24px; border-radius:12px; border:1px solid #334155;">
        <h2 style="color:#f43f5e; margin-top:0;">⚠️ Exception Details ({exception.__class__.__name__})</h2>
        <p style="color:#94a3b8;"><strong>Path:</strong> {request.path}</p>
        <p style="color:#94a3b8;"><strong>Error:</strong> {str(exception)}</p>
        <h3 style="color:#38bdf8; margin-top:20px;">Traceback:</h3>
        <pre style="background:#090d16; color:#fda4af; padding:16px; border-radius:8px; overflow-x:auto; font-size:13px; border:1px solid #475569; white-space:pre-wrap;">{tb}</pre>
    </div>
</body>
</html>"""
        return HttpResponse(html, status=500)

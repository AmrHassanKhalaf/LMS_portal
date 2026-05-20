"""
Context Processors
====================

WHY THIS FILE EXISTS:
    Context processors inject variables into ALL templates automatically.
    This saves us from having to pass `user.profile` from every single view.

HOW IT CONNECTS:
    Registered in config/settings.py under TEMPLATES['OPTIONS']['context_processors'].
"""

def user_profile(request):
    """
    Injects the user's profile into the template context if authenticated.
    Allows easy checks like {% if profile.is_admin %} in any template.
    """
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        return {'profile': request.user.profile}
    return {}

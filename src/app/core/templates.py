from pathlib import Path
from typing import (
    Any,
    Optional,
)

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse as TemplateResponse

from .i18n import get_translations

TEMPLATES: Optional[Jinja2Templates] = None
ERROR_TEMPLATE = "error.html"
ERROR_NO_SERVER_TEMPLATE = "error_no_server.html"


def get_templates() -> Jinja2Templates:
    """Get Jinja2Templates instance."""
    global TEMPLATES

    if TEMPLATES is not None:
        return TEMPLATES

    templates_dir = Path(__file__).parent.parent.parent / "templates"
    templates = Jinja2Templates(directory=templates_dir)

    from .render import RENDER_HELPERS

    templates.env.globals.update(**RENDER_HELPERS)
    templates.env.add_extension("jinja2.ext.i18n")

    # Set translations
    translations = get_translations()
    templates.env.install_gettext_translations(translations)

    TEMPLATES = templates
    return templates


def render_template(
    template_name: str,
    request: Request,
    **kwargs: Any,
) -> TemplateResponse:
    """Render template by name and context."""
    templates = get_templates()
    context = {"request": request, **kwargs}

    if base_context := get_base_context(request):
        context.update(base_context)

    return templates.TemplateResponse(template_name, context=context)


def get_base_context(request: Request) -> dict:
    """Base context for all templates."""
    from .settings import get_settings

    settings = get_settings()
    return {
        "branding_title": settings.ui.branding_title,
        "branding_image": settings.ui.branding_image,
        "branding_text": settings.ui.branding_text,
    }

from django.templatetags.static import static


UNFOLD = {
    "SITE_TITLE": "NIA-OS",
    "SITE_HEADER": "NIA-OS",
    "SITE_ICON": lambda request: static("images/favicon.svg"),
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("images/favicon.svg"),
        },
    ],
    "COLORS": {
        "primary": {
            "50": "#E3F2FD",
            "100": "#BBDEFB",
            "200": "#90CAF9",
            "300": "#64B5F6",
            "400": "#42A5F5",
            "500": "#2196F3",
            "600": "#1E88E5",
            "700": "#1976D2",
            "800": "#1565C0",
            "900": "#0D47A1",
            "950": "#0B3C91",
        },
    },
    "SHOW_BACK_BUTTON": True,
    "SHOW_LANGUAGES": True,
    "SIDEBAR": {
        "show_search": True,
    },
}

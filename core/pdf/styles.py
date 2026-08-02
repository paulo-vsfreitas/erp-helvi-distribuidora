from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT,
    TA_RIGHT,
)

from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)

from . import colors


styles = getSampleStyleSheet()


TITLE = ParagraphStyle(
    "HelviTitle",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
    alignment=TA_LEFT,
    textColor=colors.HELVI_BLACK,
    spaceAfter=18,
)

SUBTITLE = ParagraphStyle(
    "HelviSubtitle",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=18,
    alignment=TA_LEFT,
    textColor=colors.HELVI_GOLD,
    spaceAfter=10,
)

TEXT = ParagraphStyle(
    "HelviText",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10,
    leading=14,
    textColor=colors.GRAY_900,
)

LABEL = ParagraphStyle(
    "HelviLabel",
    parent=TEXT,
    fontName="Helvetica-Bold",
)

CENTER = ParagraphStyle(
    "HelviCenter",
    parent=TEXT,
    alignment=TA_CENTER,
)

RIGHT = ParagraphStyle(
    "HelviRight",
    parent=TEXT,
    alignment=TA_RIGHT,
)

FOOTER = ParagraphStyle(
    "HelviFooter",
    parent=TEXT,
    fontSize=8,
    leading=10,
    alignment=TA_CENTER,
    textColor=colors.GRAY_500,
)
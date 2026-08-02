from .elements.company import build_company


def build_header(story):

    story.extend(
        build_company()
    )
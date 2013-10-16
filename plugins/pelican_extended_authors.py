# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from pelican.contents import Content, is_valid_content
from pelican.generators import Generator
from pelican import signals


logger = logging.getLogger(__name__)


class AuthorBiography(Content):
    mandatory_properties = ('slug',)
    default_template = 'page'


class AuthorBiographyManager(object):
    def __init__(self):
        self.contents = {}

    def add(self, content):
        if not isinstance(content, AuthorBiography):
            raise Exception("This manager only accepts 'AuthorBiography' objects")

        self.contents[content.slug] = content

    def get(self, slug):
        content = self.contents.get(slug, "")
        return getattr(content, "content", "")


class AuthorBiographyGenerator(Generator):
    def __init__(self, *args, **kwargs):
        self.authors_info = AuthorBiographyManager()
        super(AuthorBiographyGenerator, self).__init__(*args, **kwargs)

    def generate_context(self):
        for author_file in self.get_files(self.settings.get('AUTHOR_DIR', 'authors'),
                                          exclude=self.settings.get('AUTHOR_EXCLUDES', '')):
            try:
                author = self.readers.read_file(
                    base_path=self.path, path=author_file, content_class=AuthorBiography,
                    context=self.context
                )

            except Exception as e:
                logger.warning("Could not process author {0}\n{1}".format(author_file, e))
                continue

            if is_valid_content(author, author_file):
                self.authors_info.add(author)

        self._update_context(('authors_info',))
        self.context['authors_info'] = self.authors_info


def get_generators(generators):
    return AuthorBiographyGenerator

def register():
    signals.get_generators.connect(get_generators)

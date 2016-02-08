"""
    twtxt.mentions
    ~~~~~~~~~~~~~~

    This module implements functions for handling mentions in twtxt.

    :copyright: (c) 2016 by buckket.
    :license: MIT, see LICENSE for more details.
"""

import re

import click

mention_re = re.compile(r'@<(?:(?P<name>.*?)\s)?(?P<url>.*?://.*?)>')
short_mention_re = re.compile(r'@(?P<name>\S+)')


def get_source_by_url(url):
    conf = click.get_current_context().obj["conf"]
    if url == conf.twturl:
        return conf.source
    return next((source for source in conf.following if source.url == url), None)


def get_source_by_name(nick):
    conf = click.get_current_context().obj["conf"]
    if nick == conf.nick and conf.twturl:
        return conf.source
    return next((source for source in conf.following if source.nick == nick), None)


def expand_mentions(text, embed_names=True):
    """Searches the given text for mentions and expands them.

    For example:
    "@source.nick" will be expanded to "@<source.nick source.url>".
    """
    if embed_names:
        mention_format = "@<{name} {url}>"
    else:
        mention_format = "@<{url}>"

    def handle_mention(match):
        source = get_source_by_name(match.group(1))
        if source is None:
            return "@{}".format(match.group(1))
        return mention_format.format(
            name=source.nick,
            url=source.url)

    return short_mention_re.sub(handle_mention, text)


def format_mentions(text, embedded_names=False):
    """Searches the given text for mentions generated by `expand_mention()` and returns a human-readable form.

    For example:
    "@<bob http://example.org/twtxt.txt>" will result in "@bob"

    If you follow a Source: source.nick will be bold
    If you are the mentioned Source: nick.nick will be bold and coloured
    If nothing from the above is true: nick will be unstyled
    """

    def handle_mention(match):
        name, url = match.groups()
        source = get_source_by_url(url)
        if source is not None and (not name or embedded_names is False):
            if source.nick == click.get_current_context().obj["conf"].nick:
                mention = click.style("@{}".format(source.nick), fg="magenta", bold=True)
            else:
                mention = click.style("@{}".format(source.nick), bold=True)
        else:
            mention = "@{}".format(name)
        return mention

    return mention_re.sub(handle_mention, text)

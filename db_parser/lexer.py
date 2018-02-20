import re
from collections import OrderedDict

import six

from db_parser.common import DbSyntaxError
from db_parser.tokens import TokenTypes


class Token(object):
    """
    Class representing a lexer token.
    Args:
        type: the type of this token. Should be one of TokenTypes
        linenum: the line number this token was found on
        colnum: the column number this token was found on
        contents: the original text that this token was parsed from
    """
    def __init__(self, type, linenum, colnum, contents=None):
        self.type = type
        self.contents = contents

        self.line = linenum
        self.col = colnum

    def __str__(self):
        return "{} (contents={})".format(self.type, self.contents)

    def __eq__(self, other):
        try:
            return self.type == other.type
        except AttributeError:
            return False


def escape(var):
    """
    Returns the input variable escaped and wrapped in a regex capture group.
    """
    return "({})".format(re.escape(var))


class Lexer(six.Iterator):
    """
    Lexer, tokenises the database file into
    """

    """
    Tokens to ignore. These are never returned from __next__
    """
    IGNORED_TOKENS = [TokenTypes.WHITESPACE, TokenTypes.COMMENT, TokenTypes.MACRO]

    """
    This provides a mapping between regexes and lexer tokens.

    The regexes are tried in order, the first one that matches get's it's token produced.
    """
    TOKEN_MAPPING = OrderedDict([
        (escape("record"),          TokenTypes.RECORD),
        (escape("field"),           TokenTypes.FIELD),
        (escape("info"),            TokenTypes.INFO),
        (escape("alias"),           TokenTypes.ALIAS),
        (escape("("),               TokenTypes.L_BRACKET),
        (escape(")"),               TokenTypes.R_BRACKET),
        (escape("{"),               TokenTypes.L_BRACE),
        (escape("}"),               TokenTypes.R_BRACE),
        (escape(","),               TokenTypes.COMMA),
        (r"(\".*?[^\\]\"|\"\")",    TokenTypes.QUOTED_STRING),
        (r"([a-zA-Z0-9]+)",         TokenTypes.LITERAL),
        (r"(\#.*)",                 TokenTypes.COMMENT),
        (r"(\$\(.*\).*)",           TokenTypes.MACRO),
        (r"(\s+)",                  TokenTypes.WHITESPACE),
    ])

    def __init__(self, filepath):
        self.filepath = filepath
        self.gen = None

    def token_generator(self):
        """
        Token generator function.
        yields:
            Tokens corresponding to the lexed input.
        """
        with open(self.filepath) as f:
            lines = f.readlines()
            for linenum, line in enumerate(lines, 1):
                line = line.strip()
                column = 0
                while column < len(line):
                    for regexp in Lexer.TOKEN_MAPPING:
                        match_text = self._text_matches_regex(line[column:], regexp)
                        if match_text is not None:
                            column += len(match_text)
                            yield Token(Lexer.TOKEN_MAPPING[regexp], linenum, column, match_text)
                            break
                    else:
                        raise DbSyntaxError("No matching rules found at {}:{}. Line contents: '{}'"
                                            .format(linenum, column, line))

            yield Token(TokenTypes.EOF, len(lines), len(lines[len(lines)-1]))

    def __next__(self):
        """
        Generator of this Lexer's tokens
        """
        if self.gen is None:
            self.gen = self.token_generator()

        tok = next(self.gen)
        while tok.type in [TokenTypes.WHITESPACE, TokenTypes.COMMENT, TokenTypes.MACRO]:
            tok = next(self.gen)
        return tok

    @staticmethod
    def _text_matches_regex(text, rx):
        """
        Attempts to match the given text with a given regex.

        Args:
            text:
            rx: the regex to apply
        Returns:
             The text of the match if the match succeeded, None otherwise
        """
        match = re.match(rx, text)
        if match:
            try:
                return match.group(1)
            except IndexError:
                return None
        return None
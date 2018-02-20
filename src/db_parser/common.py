class DbSyntaxError(ValueError):
    """
    Error that gets raised if there was a problem with the syntax of a DB file.
    """


def parse_db_from_filepath(filepath):
    from src.db_parser.parser import Parser
    from src.db_parser.lexer import Lexer
    with open(filepath) as f:
        return Parser(Lexer(f.read())).db()

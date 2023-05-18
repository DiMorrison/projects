"""
Iznimka za regularni izraz
"""


class InvalidRegexException(Exception):
    """
    Iznimka koja se baca kada je regularni izraz neispravan.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self, message)

    def __str__(self):
        return self.message

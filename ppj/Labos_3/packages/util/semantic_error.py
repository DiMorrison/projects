class SemanticError(Exception):
    def __init__(self, inner_object):
        self.inner_object = inner_object

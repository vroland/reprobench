from loguru import logger
import os

from pathspec import PathSpec
from pathlib import Path
from .base import BaseTaskSource


class FileSource(BaseTaskSource):
    TYPE = "file"

    def __init__(self, path=None, patterns="", resolve=False, **kwargs):
        super().__init__(path)
        if not os.path.exists(path):
            logger.error(f"Path does not exist: '{path}'")
            raise FileNotFoundError(path)
        self.patterns = patterns
        self.__resolve = resolve

    def setup(self):
        spec = PathSpec.from_lines("gitwildmatch", self.patterns.splitlines())
        matches = spec.match_tree(self.path)
        if self.__resolve:
            return map(lambda match: (Path(self.path).resolve(), match), matches)
        else:
            return map(lambda match: (Path(self.path), match), matches)

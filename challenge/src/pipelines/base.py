from abc import ABC, abstractmethod
from pathlib import Path
import logging

import polars as pl

logger = logging.getLogger(__name__)


class Pipeline(ABC):
    """ETL lifecycle: extract → transform → validate → deliver."""

    def __init__(self, file_path: str | Path, name: str):
        self.file_path = Path(file_path)
        self._name = name

    # ------------------------------------------------------------------
    # Extract
    # ------------------------------------------------------------------

    def extract(self) -> pl.DataFrame:
        df = pl.read_csv(self.file_path)
        logger.info("%s: %d records extracted", self._name, len(df))
        return df

    # ------------------------------------------------------------------
    # Transform  (abstract)
    # ------------------------------------------------------------------

    @abstractmethod
    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Validate  (abstract)
    # ------------------------------------------------------------------

    @abstractmethod
    def validate(self, df: pl.DataFrame) -> None:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self) -> pl.DataFrame:
        logger.info("═ %s: processing started ═", self._name)
        df = self.extract()
        df = self.transform(df)
        self.validate(df)
        logger.info("═ %s: processing finished ═", self._name)
        return df

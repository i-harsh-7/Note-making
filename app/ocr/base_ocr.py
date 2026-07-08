from abc import ABC, abstractmethod
import numpy as np


class OCRProvider(ABC):
    name: str = "base"

    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """Extract text from an image file path."""

    @abstractmethod
    def extract_text_from_array(self, image: np.ndarray) -> str:
        """Extract text from a numpy HWC uint8 image array."""

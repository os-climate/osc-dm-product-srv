# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created:  2024-04-15 by eric.broda@brodagroupsoftware.com

from abc import ABC, abstractmethod
from typing import Dict, Any


class AbstractMetadata(ABC):
    """
    Abstract base class for metadata objects.

    This class serves as a template for various types of metadata,
    providing a consistent interface for loading and querying metadata.
    Subclasses are expected to implement the specific details of these
    operations based on their respective metadata formats.

    Methods to be implemented by subclasses:
        - __init__(**kwargs): Initialize the metadata object.
        - load(): Load metadata from a source.
        - query(text: str): Perform a query on the metadata.
    """

    @abstractmethod
    def __init__(self, **kwargs):
        """
        Initialize the metadata object.

        Subclasses should provide an implementation that initializes
        the metadata object, potentially using the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments that can be used for initialization.
        """
        pass

    @abstractmethod
    def load(self):
        """
        Load metadata
        """
        pass

    @abstractmethod
    def info(self):
        """
        Return info (metadata)
        """
        pass

    @abstractmethod
    def query(self, **kwargs):
        """
        Perform a query on the metadata.

        This method should be implemented by subclasses to allow querying
        the metadata based on the provided text. The nature of the query and
        the return value can vary based on the subclass implementation.

        Args:
            text (str): The query string to be used for searching the metadata.

        Returns:
            The result of the query, the format of which depends on the subclass implementation.
        """
        pass
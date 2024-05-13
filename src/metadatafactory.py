# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created:  2024-04-15 by eric.broda@brodagroupsoftware.com

from typing import Type, Dict

from abstractmetadata import AbstractMetadata
from simplemetadata import SimpleMetadata

class MetadataFactory:
    """
    Factory class for creating instances of various metadata types.

    This class uses a mapping of metadata type names to their corresponding
    classes to instantiate and return metadata objects. The factory expects
    metadata type names and associated keyword arguments for initialization.

    Attributes:
        metadatas (Dict[str, Type[AbstractMetadata]]): A mapping of metadata type
            names to their corresponding classes.

    Example:
        simple_metadata = MetadataFactory.cnew_instance("simple", name="example", value="data")
    """

    metadatas: Dict[str, Type[AbstractMetadata]] = {
        "simple": SimpleMetadata,
    }

    @staticmethod
    def new_instance(type: str, **kwargs) -> AbstractMetadata:
        """
        Creates and returns an instance of the specified metadata type.

        This method dynamically selects the appropriate metadata class based on the
        metadata_type argument. It then initializes and returns an instance of that class,
        passing the provided keyword arguments to the class constructor.

        Args:
            metadata_type (str): The type of metadata to create. Must be a key in the
                'metadatas' class attribute.
            **kwargs: Arbitrary keyword arguments passed to the metadata class constructor.

        Returns:
            AbstractMetadata: An instance of the requested metadata type.

        Raises:
            ValueError: If the specified metadata_type is not recognized.
            ValidationError: If the provided keyword arguments do not match the expected
                fields for the specified metadata type (using Pydantic validation).
        """

        metadata_class = MetadataFactory.metadatas.get(type)
        if metadata_class:
            return metadata_class(**kwargs)
        else:
            raise ValueError(f"Unknown metadata type: {type}")


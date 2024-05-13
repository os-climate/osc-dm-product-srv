# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created:  2024-04-15 by eric.broda@brodagroupsoftware.com

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from typing import List
import yaml
import json
import os
from datetime import datetime

from abstractmetadata import AbstractMetadata
from bgsexception import BgsException, BgsNotFoundException
import models

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(module)s:%(funcName)s %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
logger = logging.getLogger(__name__)

class SimpleMetadata(AbstractMetadata):
    """
    SimpleMetadata is a concrete implementation of the AbstractMetadata class.
    It is designed to load and query metadata from a structured directory containing
    YAML files for products, artifacts, and publishers.
    """

    def __init__(self, **kwargs):
        """
        Initializes the SimpleMetadata object with the provided keyword arguments.

        Keyword arguments:
            'directory' which denotes the path to the metadata files.

        Raises:
            ValueError: If the mandatory 'directory' keyword argument is not provided.
        """
        logger.info(f"Initialization kwargs:{kwargs}")
        self.directory = self._param(kwargs, "directory")

        uuids: models.UUIDs = self._load_uuids()
        logger.info(f"Loaded UUIDs:{uuids}")
        self.product_uuid = uuids.product_uuid
        logger.info(f"Using product UUID:{self.product_uuid}")
        self.artifact_uuids = {}
        for artifact_uuid in uuids.artifact_uuids:
            for artifact_name, artifact_uuid in artifact_uuid.items():
                self.artifact_uuids[artifact_name] = artifact_uuid
        logger.info(f"Using artifact UUIDs:{self.artifact_uuids}")


    def load(self):
        self.metadata: models.FQProduct = self._load_metadata()
        logger.info(f"Loaded metadata:{self.metadata}")


    def info(self):
        return self.metadata


    def query(self, **kwargs):
        logger.info(f"Querying kwargs:{kwargs}")
        self.artifact_uuid = self._param(kwargs, "artifact")
        # Find the artifact by UUID in the metadata cache (cache is self.metadata)


    def _load_uuids(self):
        file_path = os.path.join(self.directory, "uuids.yaml")
        logger.info(f"Loading uuids from path:{file_path}")

        if not os.path.exists(file_path):
            msg = f"File not found:{file_path}"
            logger.error(msg)
            raise BgsNotFoundException(msg)

        uuids: models.UUIDs = None
        with open(file_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
                uuids = models.UUIDs(**data)
            except yaml.YAMLError as e:
                msg = f"Error reading YAML file:{file_path}, exception:{e}"
                logger.error(msg, exc_info=True)
                raise BgsException(msg, e)
        return uuids


    def _load_metadata(self):
        """
        Loads the metadata from the specified directory.

        This method initiates the process of reading metadata from various YAML files located in
        the directory specified by the 'directory' attribute of this class.

        Returns:
            models.FQProduct: A fully qualified data product object representing the loaded metadata,
            which includes product information, a list of artifacts, and publisher data.

        Raises:
            BgsException: If any of the YAML files are malformed or if there are issues reading
            the files.
        """

        # Load the product, and set UUID for the product
        # (from the loaded UUIDs)
        product: models.Product = self._load_product()
        product.uuid = self.product_uuid
        logger.info(f"Loaded product:{product}")

        # Load the artifacts, and set UUID for each artifact
        # (from the loaded UUIDs)
        artifacts: List[models.Artifact] = self._load_artifacts(product)
        for artifact in artifacts:
            artifact.uuid = self.artifact_uuids[artifact.name]
            artifact.productuuid = product.uuid

        fqproduct = models.FQProduct(
            product = product,
            artifacts = artifacts
        )

        return fqproduct


    def _load_product(self):
        fqpath = os.path.join(self.directory, "product.yaml")
        logger.info(f"Loading product fqpath:{fqpath}")

        product: models.Product = None
        try:
            with open(fqpath, 'r') as f:
                data = yaml.safe_load(f)
                data = data["product"]
                product = models.Product(**data)
        except yaml.YAMLError as e:
            msg = f"Error reading YAML fqpath:{fqpath} exception:{e}"
            logger.error(msg, exc_info=True)
            raise BgsException(msg, e)
        except Exception as e:
            msg = f"Error reading fqpath:{fqpath} exception:{e}"
            logger.error(msg, exc_info=True)
            raise BgsException(msg, e)

        return product


    def _load_publisher(self):
        file_path = os.path.join(self.directory, "publisher.yaml")
        logger.info(f"Loading publisher:{file_path}")

        publisher: models.Publisher = None
        with open(file_path, 'r') as f:
            try:
                logger.info(f"Loading owner:{file_path}")
                data = yaml.safe_load(f)
                data = data["publisher"]
                publisher = models.Publisher(**data)
            except yaml.YAMLError as e:
                msg = f"Error reading YAML file {file_path}: {e}"
                logger.error(msg, exc_info=True)
                raise BgsException(msg, e)
        return publisher


    def _load_artifacts(self, product: models.Product):
        artifacts: List[models.Artifact] = []
        for root, dirs, files in os.walk(self.directory):
            if root.endswith("artifacts"):
                logger.info(f"Loading artifacts:{files}")
                for file in files:
                    if file.endswith(".yaml") or file.endswith(".yml"):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            try:
                                logger.info(f"Loading artifact:{file_path}")
                                data = yaml.safe_load(f)
                                data = data["artifact"]
                                # logger.info(f"Loading data:{data}")
                                # logger.info(f"Loading data:{json.dumps(data)}")
                                artifact = models.Artifact(**data)
                                artifact.productnamespace = product.namespace
                                artifact.productname = product.name
                                artifact.createtimestamp = datetime.now().isoformat(sep=' ', timespec='milliseconds')
                                artifact.updatetimestamp = artifact.createtimestamp
                                artifacts.append(artifact)
                            except yaml.YAMLError as e:
                                msg = f"Error reading artifact YAML file:{file_path}: {e}"
                                logger.error(msg, exc_info=True)
                                raise BgsException(msg, e)
                            except Exception as e:
                                msg = f"Error processing artifact file:{file_path}: {e}"
                                logger.error(msg, exc_info=True)
                                raise BgsException(msg, e)
        return artifacts


    def _param(self, kwargs, name: str):
        if name in kwargs:
            return kwargs[name]
        else:
            raise ValueError(f"Mandatory keyword:{name} parameters:{kwargs}")


# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created:  2024-04-15 by eric.broda@brodagroupsoftware.com

import logging
import uuid
from datetime import datetime

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(module)s:%(funcName)s %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
logger = logging.getLogger(__name__)

import models
from bgsexception import BgsException, BgsNotFoundException

STATUS_AUTHORIZED = "authorized"
STATUS_UNAUTHORIZED = "unauthorized"

import utilities
import models

class Registrar():

    def __init__(self, config: dict):
        """
        Connect to the registrar
        """
        logger.info(f"Using config:{config}")
        self.registrar_host = config["host"]
        self.registrar_port = config["port"]

    async def register_product(self, product: models.Product):
        logger.info(f"Registering product:{product}")

        product_dict = product.model_dump()
        service = "/api/registrar/products"
        method = "POST"
        response = await utilities.httprequest(self.registrar_host, self.registrar_port, service, method, obj=product_dict)
        logger.info(f"Registering product:{product}, response:{response}")

        return response

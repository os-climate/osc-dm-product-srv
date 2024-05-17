# Copyright 2024 Broda Group Software Inc.
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
#
# Created:  2024-04-15 by eric.broda@brodagroupsoftware.com

import logging
from datetime import datetime
from typing import List
import os
import json
# import csv
import yaml
import time

from fastapi import FastAPI, Request, WebSocket, HTTPException
from fastapi.websockets import WebSocketDisconnect
import uvicorn

# Make accessible other source directories (as needed)
# script_dir = os.path.dirname(__file__)  # Path to the directory of server.py
# parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
# sys.path.insert(0, parent_dir)

import utilities
import models
import state
from registrar import Registrar
from bgsexception import BgsException, BgsNotFoundException
from abstractmetadata import AbstractMetadata
from middleware import LoggingMiddleware

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(module)s:%(funcName)s %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
logger = logging.getLogger(__name__)

ENDPOINT_DATAPRODUCTS = "/dataproducts"
ENDPOINT_PREFIX = "/api" + ENDPOINT_DATAPRODUCTS
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT=8000
DEFAULT_CONFIG="./config/config.yaml"
STATE_CONFIGURATION = "configuration"
STATE_REGISTRAR="registrar"
STATE_METADATA="metadata"

DATAPRODUCT_DIR = "dataproducts"
METADATA_RETRY_SECONDS = 15
REGISTRATION_RETRY_SECONDS = 15
REGISTRATION_FILENAME = "registration.yaml"


# Set up server
app = FastAPI()
app.add_middleware(LoggingMiddleware)


@app.get(ENDPOINT_PREFIX + "/uuid/{uuid}/tmp/{path}")
async def dataproducts_tmp_file_get(uuid: str, path: str):
    """
    This is a TEMPORARY endpoint used by the Marketplace UX
    to get samples and metadata where it does not exist yet
    (in other words, for placehodler data). The path will be
    relative to the configuration directory (usually pointing
    to samples). THIS SHOULD BE REPLACED ONCE SAMPLES AND
    METADATA ARE SUPPORTED!
    """
    response = None

    fqpath = None
    try:
        logger.info(f"Using data product directory:{DATAPRODUCT_DIR}")
        logger.info(f"Contents of data product directory:{os.listdir(DATAPRODUCT_DIR)}")
        fqpath = os.path.join(DATAPRODUCT_DIR, path)
        logger.info(f"Reading fqpath:{fqpath}")
        data: str = None

        if fqpath.endswith('.json'):
            # Read a JSON file
            with open(fqpath, 'r') as file:
                data = json.load(file)
                logger.info(f"data:{data}")
                logger.info(f"JSON data:{json.dumps(data)}")
        # Using the CSV reader to convert to string
        # introduces a bunch extra escape characters,
        # so for now allow CSV files be treated as text files
        # elif fqpath.endswith('.csv'):
        #     # Using StringIO to accumulate output
        #     output = io.StringIO()

        #     # Open the CSV file for reading
        #     with open(fqpath, newline='') as file:
        #         reader = csv.reader(file)

        #         # Create a CSV writer that writes to a string buffer
        #         writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        #         # Read each row from the source CSV and write it to the string buffer
        #         for row in reader:
        #             writer.writerow(row)

        #     # Get the complete string from the buffer
        #     data = output.getvalue()
        #     output.close()
        else:
            # Default to reading as a plain text file
            with open(fqpath, 'r') as file:
                data = file.read()

    except FileNotFoundError:
        msg = f"File does not exist, path:{fqpath} exception:{e}"
        logger.error(msg)
        raise HTTPException(status_code=404, detail=msg)
    except json.JSONDecodeError:
        msg = f"Invalid JSON, path:{fqpath} exception:{e}"
        logger.error(msg)
        raise HTTPException(status_code=500, detail=msg)
    except PermissionError:
        msg = f"Permission denied to read file, path:{fqpath} exception:{e}"
        logger.error(msg)
        raise HTTPException(status_code=500, detail=msg)
    except Exception as e:
        msg = f"Could not read file, path:{fqpath} exception:{e}"
        logger.error(msg)
        raise HTTPException(status_code=500, detail=msg)

    response = data
    return response


@app.get(ENDPOINT_PREFIX + "/uuid/{uuid}")
async def dataproducts_uuid_get(uuid: str) -> models.FQProduct:
    """
    Discover product by uuid
    """
    response = None

    metadata = state.gstate(STATE_METADATA)
    fqproduct: models.FQProduct = metadata.info()
    logger.info(f"fqproduct:{fqproduct}")

    # Check to ensure the UUID matches
    if uuid != fqproduct.product.uuid:
        msg = f"Invalid uuid:{uuid} (does not match uuid for product)"
        logger.error(msg)
        raise HTTPException(status_code=404, detail=msg)

    response = fqproduct

    return response


@app.get(ENDPOINT_PREFIX + "/uuid/{uuid}/artifacts")
async def dataproducts_uuid_artifacts_get(uuid: str) -> List[models.Artifact]:
    """
    Discover all artifacts for a product
    """
    response = None

    # Should check to ensure the UUID matches?

    metadata = state.gstate(STATE_METADATA)
    fqproduct: models.FQProduct = metadata.info()

    # Check to ensure the UUID matches
    if uuid != fqproduct.product.uuid:
        msg = f"Invalid uuid:{uuid} (does not match uuid for product)"
        logger.error(msg)
        raise HTTPException(status_code=404, detail=msg)

    artifacts: List[models.Artifact] = fqproduct.artifacts
    response = artifacts

    return response


@app.get(ENDPOINT_PREFIX + "/uuid/{uuid}/artifacts/{artifact_uuid}")
async def dataproducts_uuid_artifacts_get(uuid: str, artifact_uuid: str) -> models.Artifact:
    """
    Discover product artifact by uuid
    """
    response = None

    metadata = state.gstate(STATE_METADATA)
    fqproduct: models.FQProduct = metadata.info()

    # Check to ensure the UUID matches
    if uuid != fqproduct.product.uuid:
        msg = f"Invalid uuid:{uuid} (does not match uuid for product)"
        logger.error(msg)
        raise HTTPException(status_code=404, detail=msg)

    artifacts: List[models.Artifact] = fqproduct.artifacts
    found_artifact: models.Artifact = None
    for artifact in artifacts:
        if artifact.uuid == artifact_uuid:
            found_artifact = artifact
            break

    response = found_artifact
    return response


@app.get(ENDPOINT_PREFIX + "/uuid/{uuid}/metrics")
async def dataproducts_observability_get(uuid: str):
    """
    Observability
    """
    response = None
    response = { "msg": "Not implemented" }
    return response


@app.get(ENDPOINT_PREFIX + "/uuid/{uuid}/admin")
async def administration_get(uuid: str):
    """
    Administration
    """
    response = None
    response = { "msg": "Not implemented" }
    return response


#####
# MONITOR
#####


@app.get(ENDPOINT_PREFIX + "/health")
async def dataproducts_health_get():
    """
    Get health information
    """
    response = {
        "health": "OK"
    }
    return response


@app.get(ENDPOINT_PREFIX + "/metrics")
async def dataproducts_metrics_get():
    """
    Get metrics information
    """
    response = {
        "metrics": "some-metrics"
    }
    return response


#####
# INTERNAL
#####


def _load_metadata():
    from metadatafactory import MetadataFactory
    factory = MetadataFactory()
    metadata_dir = "dataproducts"
    logger.info(f"Using metadata_dir:{metadata_dir}")

    while True:
        try:
            metadata = factory.new_instance("simple", directory=metadata_dir)
            metadata.load()
            state.gstate(STATE_METADATA, metadata)
            logger.info("Metadata load SUCCESS")
            break
        except Exception as e:
            msg = (
                f"Metadata load FAILED, "
                f"retry in (seconds):{METADATA_RETRY_SECONDS}, "
                f"exception:{e}"
            )
            logger.error(msg)
            time.sleep(METADATA_RETRY_SECONDS)


def _register():

    registrar: Registrar = state.gstate(STATE_REGISTRAR)
    metadata: AbstractMetadata = state.gstate(STATE_METADATA)
    import socket
    hostname = socket.gethostname()
    # http://osc-dm-product-srv-0:8000
    product_address = "http://" + hostname + ":" + "8000"
    logger.info(f"Product address:{product_address}")

    # product: models.Product = await self._load_product(directory)
    # product.uuid = uuids_dict["product_uuid"]
    # product.address = address

    fqproduct: models.FQProduct = metadata.info()
    product = fqproduct.product
    product.address = product_address
    product_dict = dict(product)

    # Registration MUST occur successfully, otherwise
    # the product can not interact with the system.
    # Try to send data on a periodic basis until
    # registration is successful.
    while True:
        response = None
        service = "/api/registrar/products"
        method = "POST"
        try:
            logger.info(
                f"Registering product with Registrar "
                f"host:{registrar.registrar_host} "
                f"port:{registrar.registrar_port} "
                f"service:{service} method:{method}"
            )
            response = utilities.shttprequest(
                registrar.registrar_host, registrar.registrar_port,
                service, method, obj=product_dict)
            logger.info(f"Registration SUCCESS, response:{response}")
            break
        except Exception as e:
            msg = (
                f"Registration FAILED, "
                f"retry in (seconds):{REGISTRATION_RETRY_SECONDS}, "
                f"exception:{e}"
            )
            logger.error(msg)
            time.sleep(REGISTRATION_RETRY_SECONDS)  # Sleep for one minute

    # Write the address to a YAML file (this a
    # record for product owner for what they submitted)
    filename = REGISTRATION_FILENAME
    fqfilename = os.path.join(DATAPRODUCT_DIR, filename)

    registration_date = datetime.now().strftime("%d-%b-%Y %H:%M:%S %Z")
    details = (
        "##### \n"
        "# \n"
        "# Data Product Address Registration \n"
        "# \n"
        f"# Namespace: {product.namespace} \n"
        f"# Name: {product.name} \n"
        "# \n"
        "# ----- \n"
        "# \n"
        f"# Registered on: {registration_date} \n"
        "# \n"
        "##### \n"
    )
    details = details + f"address: {product_address}  \n"
    logger.info(f"details:{details}")
    with open(fqfilename, 'w') as file:
        file.write(details)


#####
# MAINLINE
#####

@app.on_event("startup")
async def startup_event():
    path = DATAPRODUCT_DIR
    logger.info(f"Initializing file monitor path:{path}")
    logger.info(f"Contents of Dataproduct directory:{os.listdir(path)}")
    logger.info(f"STARTUP Using:{path}")
    # Running the directory watcher in the background
    asyncio.create_task(watch_directory(path))


import asyncio
from watchgod import awatch, Change
async def watch_directory(path: str):
    async for changes in awatch(path):
        logger.info(f"Changes detected: {changes}")
        for change in changes:
            event, path = change

            # Ignore registration file creation
            # as it will happen upon successful
            # registration and does not
            # need to be observed ... except if deleted,
            # which means we would lose registration
            # info (service will still run)
            if REGISTRATION_FILENAME in path:
                if event != Change.deleted:
                    continue

            if event == Change.added:
                logger.info(f"ADD:{path}")
            elif event == Change.modified:
                logger.info(f"CHANGE:{path}")
            elif event == Change.deleted:
                logger.info(f"DELETE:{path}")
            else:
                continue

            logger.info("Registration/metadata (reload) initiated")
            _load_metadata()
            _register()
            logger.info("Registration/metadata (reload) complete")


if __name__ == "__main__":

    # Set up argument parsing
    import argparse
    parser = argparse.ArgumentParser(description="Run the FastAPI server.")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help=f"Host for the server (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port for the server (default: {DEFAULT_PORT})")
    parser.add_argument("--configuration", default=DEFAULT_CONFIG, help=f"Configuration file (default: {DEFAULT_CONFIG})")
    args = parser.parse_args()

    # Show directory file contents (for debugging)
    cwd = os.getcwd()
    logger.info(f"Current working directory:{cwd}")
    logger.info(f"Files and directories:{os.listdir(cwd)}")
    logger.info(f"Dataproduct directory:{DATAPRODUCT_DIR}")
    logger.info(f"Contents of Dataproduct directory:{os.listdir(DATAPRODUCT_DIR)}")

    # Load configuration
    configuration = None
    with open(args.configuration, 'r') as file:
        configuration = yaml.safe_load(file)

    # Save the configuration for future use
    state.gstate(STATE_CONFIGURATION, configuration)
    logger.info(f"Using configuration:{configuration}")

    # Get host and port from configuration
    host = configuration["product"]["host"]
    port = configuration["product"]["port"]

    # Get host and port for registrar (via proxy)
    registrar_host = configuration["proxy"]["host"]
    registrar_port = configuration["proxy"]["port"]
    registrar = Registrar({
        "host": registrar_host,
        "port": registrar_port,
    })
    state.gstate(STATE_REGISTRAR, registrar)
    logger.info(f"Using registrar:{registrar}")

    # Load metadata
    _load_metadata()

    # Register the data product
    _register()

    # Start the service
    try:
        logger.info(f"START: service on host:{host} port:{port}")
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        logger.info(f"Stopping server, exception:{e}")
    finally:
        logger.info("Terminating server")

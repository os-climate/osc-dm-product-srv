
> [!IMPORTANT]
> On June 26 2024, Linux Foundation announced the merger of its financial services umbrella, the Fintech Open Source Foundation ([FINOS](https://finos.org)), with OS-Climate, an open source community dedicated to building data technologies, modeling, and analytic tools that will drive global capital flows into climate change mitigation and resilience; OS-Climate projects are in the process of transitioning to the [FINOS governance framework](https://community.finos.org/docs/governance); read more on [finos.org/press/finos-join-forces-os-open-source-climate-sustainability-esg](https://finos.org/press/finos-join-forces-os-open-source-climate-sustainability-esg)

# osc-dm-product-srv - Data Mesh Data Product

osc-dm-product-srv is a data product agent
service for Broda Group Software's Data Mesh platform,
allowing data product configurations to be registered
(published), and data products to be discoverable, observable,
and manageable.

Full documentation is available in in the
[osc-dm-mesh-doc](https://github.com/brodagroupsoftware/osc-dm-mesh-doc)
repo.

This application interacts with other applications. You can run
the full set of applications by following instructions in the
[osc-dm-mesh-doc](https://github.com/brodagroupsoftware/osc-dm-mesh-doc)
repo.

The remaining sections explain how to Dockerize the application
as well as providing a few developer notes.

## Prerequisites

Python must be available, preferably in a virtual environment (venv).

## Setting up your Environment

Some environment variables are used by various source code and scripts.
Setup your environment as follows (note that "source" is used)
~~~~
source ./bin/environment.sh
~~~~

It is recommended that a Python virtual environment be created.
We have provided several convenience scripts to create and activate
a virtual environment. To create a new virtual environment using
these convenience scripts, execute the following (this will
create a directory called "venv" in your current working directory):
~~~~
$PROJECT_DIR/bin/venv.sh
~~~~

Once your virtual enviornment has been created, it can be activated
as follows (note: you *must* activate the virtual environment
for it to be used, and the command requires "source" to ensure
environment variables to support venv are established correctly):
~~~~
source $PROJECT_DIR/bin/vactivate.sh
~~~~

Install the required libraries as follows:
~~~~
pip install -r requirements.txt
~~~~

Note that if you wish to run test cases then you will need
to also install "pytest" (it is not installed by default as
it is a development rather than product dependency).
~~~~
pip install pytest
~~~~

## Creating a Docker Image

A Dockefile is provided for this service.  A docker image for this
service can be creating using the following script:
~~~~
$PROJECT_DIR/bin/dockerize.sh
~~~~

## Starting the Service

This service is designed to work with other services and
can be started with the full set of Data Mesh components.
Information about starting the full set of components
can be found [here](https://github.com/brodagroupsoftware/osc-dm-mesh-srv)

A standalone server can be started for testing purposes
using the following command:
~~~~
$PROJECT_DIR/app/start.sh
~~~~

## Data Product Configuration

The data product configuration as well as artifact
configuration are contained in the following directory:
~~~~
config
~~~~

TODO: Configuration should be structured to allow
domains, then data product names:
~~~~
config/domain/name
~~~~

### Data Products (Configuration)

A sample data product is available in the data product
configuration directory, called "rmi".  The full
set of data product assets are located in:
~~~~
config/rmi
~~~~

The configuration for this data product is located in:
~~~~
config/rmi/product.yaml
~~~~

Each data product has several attributes:
- domain: the data product domain; domains are unique across all
data products
- name: The data product name; names must be unique in a domain
- description: 1-2 sentence description of the data product
- tags: Used for searching
- publisher: The data product publisher, or data product owner

The sample product configuration is as follows:
- domain: brodagroupsoftware.com
- name: rmi.dataproduct
- description: US Utility data provided by RMI
- tags: ["utilities", "emissions"]
- publisher: publisher.user@brodagroupsoftware.com

### Artifacts (Configuration) and Other Data Product Characteristics

Numerous artifacts are available for the sample data product:
~~~~
config/rmi/artifacts
~~~~

Each artifact has several attributes:
- name: Unique name within the set of artifacts
- description: 1-2 sentnece description
- tags: Used to augment searching
- license: Defines Defines how artifact can be used or shared
- securitypolicy: Access policy for the artifact
- data: URLs to the artifact

There are several other configuration files:
- bundles: groups of artifacts treated as a single entity
- metadata: API specifications to "discover" the data product
- provenance: Lineage information for the data product
- queries: vetted queries permitted by the data product

## Getting Started

In this tutorial, we will perform several steps:
- Start the data product
- Use the publisher CLI to register (publish) and observe a data product
- Use the subscriber CLI to discover and observe a data product
- Use the administrator CLI to manage the data product

## Start the Data Product

A script, "start.sh" is available to start the data
product locally. The script is currently setup
(but easy to change) to start the data product on
host:localhost and port:9000.

Start a data product locally:
~~~~
$PROJECT_DIR/app/start.sh
~~~~

A script, "startd.sh" is available to start the data
product in a docker container. The script has
parameters that govern its operation, but several
parameter are required:
- INSTANCE, which reflects the
instance id for the running image (multiple instances
with different configations can be running at the
same time.

To start it in a docker container with INSTANCE
is set to 0, and CONFIG_NAME to "rmi":
~~~~
INSTANCE=0 ;
CONFIG_NAME="rmi" ;
$PROJECT_DIR/app/startd.sh $INSTANCE $CONFIG_NAME
~~~~

## Using the Data Product CLI

The CLI communicates with the data product server
and hence requries a host and port, shown below.

Also, verbose logging can be enabled using the "--verbose" tag.
For your convenience, each of the examples in this tutorial
use an environment variable, VERBOSE, which if set to
"--verbose" will permit extended logging in the CLI.

~~~~
DATAPRODUCT_HOST=localhost ;
DATAPRODUCT_PORT=24000 ;
VERBOSE="--verbose"
~~~~

Note that in local mode (ie. not in docker) the Data Mesh
Registry may be running on a default port of 8000.
If you are running the Data Mesh Registry in Docker, then
the port is 'DATAPRODUCT_PORT'.  Make sure you setup the PORT
environment variable accordingly.

To disable verbose logging, unset VERBOSE:
~~~~
VERBOSE=""
~~~~

## Working with Data Products (using the CLI)

Each data product has a minimum set of endpoints:
- /registrar: registers a data product with the data mesh registry, and makes
it available in the marketplace/registry
- /discovery: returns information about all accessible endpoints for a data product
- /observability: returns run-time state/status and information about a data product
- /administration: controls and manages the data product agent

## Interacting with a Data Product

The CLI to interact with a data product is in the "bgscli-dmregistry" project.
You will need to open a new terminal window, clone the "bgscli-dmregistry"
repo and follow the instructions to setup the CLI environment.

The CLI allows you to:
- register a data product
- view all data products or a single one
- view data product artifacts
- disocver a data product
- observe a data product
- and many more capabilities
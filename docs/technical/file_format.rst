MSEE File Format
===============

Overview
-------

The MSEE file format is the native project file format for Modsee. It is a JSON-based format that stores all information required to represent and recreate a structural engineering model.

File Extension
------------

MSEE files use the `.msee` file extension.

Version
------

The current version of the file format is 1.0.0.

Format Structure
--------------

The MSEE file is structured as a JSON document with the following main sections:

1. `metadata`: Contains information about the file itself
2. `model`: Contains all model components (nodes, elements, etc.)
3. `app_settings`: Contains application-specific settings

Metadata
-------

The metadata section contains information about the file:

.. code-block:: json

    "metadata": {
        "file_format_version": "1.0.0",
        "created_by": "Modsee",
        "created_at": "2023-06-15T10:30:00",
        "file_path": "path/to/file.msee",
        "description": "Optional description"
    }

Fields:

- `file_format_version`: The version of the MSEE file format
- `created_by`: The application that created the file
- `created_at`: ISO 8601 timestamp of when the file was created
- `file_path`: The path where the file was originally saved
- `description`: Optional description of the model

Model
----

The model section contains all model components:

.. code-block:: json

    "model": {
        "nodes": [...],
        "elements": [...],
        "materials": [...],
        "sections": [...],
        "constraints": [...],
        "loads": [...],
        "stages": [...]
    }

Each model component is stored as an array of objects with at least the following fields:

- `id`: Unique identifier for the component
- `type`: The type of the component (e.g., "Node", "ElasticBeamColumn")

Nodes
~~~~

Each node contains:

.. code-block:: json

    {
        "id": 1,
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "dofs": [1, 1, 1, 1, 1, 1],
        "type": "Node"
    }

- `id`: Node identifier
- `x`, `y`, `z`: Coordinates
- `dofs`: Degrees of freedom (1 = free, 0 = fixed)
- `type`: Node type

Elements
~~~~~~~

Each element contains:

.. code-block:: json

    {
        "id": 1,
        "nodes": [1, 2],
        "material": 1,
        "section": 1,
        "type": "ElasticBeamColumn"
    }

- `id`: Element identifier
- `nodes`: Array of node identifiers that define the element
- `material`: Identifier of the material used
- `section`: Identifier of the section used
- `type`: Element type

Materials
~~~~~~~~

Each material contains:

.. code-block:: json

    {
        "id": 1,
        "type": "ElasticIsotropic",
        "name": "Steel",
        "properties": {
            "E": 29000.0,
            "v": 0.3,
            "rho": 7.85e-9
        }
    }

- `id`: Material identifier
- `type`: Material type
- `name`: Optional name
- `properties`: Type-specific properties

Sections
~~~~~~~

Each section contains:

.. code-block:: json

    {
        "id": 1,
        "type": "RectangularSection",
        "name": "Column Section",
        "properties": {
            "width": 0.3,
            "depth": 0.5,
            "area": 0.15,
            "Iz": 0.003125
        }
    }

- `id`: Section identifier
- `type`: Section type
- `name`: Optional name
- `properties`: Type-specific properties

Constraints
~~~~~~~~~~

Each constraint contains:

.. code-block:: json

    {
        "id": 1,
        "type": "FixedConstraint",
        "name": "Base Constraint",
        "properties": {
            "node_ids": [1, 2],
            "fixed_dofs": [1, 1, 1, 1, 1, 1]
        }
    }

- `id`: Constraint identifier
- `type`: Constraint type
- `name`: Optional name
- `properties`: Type-specific properties

Loads
~~~~

Each load contains:

.. code-block:: json

    {
        "id": 1,
        "type": "NodeLoad",
        "name": "Roof Point Load",
        "properties": {
            "node_id": 4,
            "fx": 0.0,
            "fy": -10.0,
            "fz": 0.0,
            "mx": 0.0,
            "my": 0.0,
            "mz": 0.0
        }
    }

- `id`: Load identifier
- `type`: Load type
- `name`: Optional name
- `properties`: Type-specific properties

Analysis Stages
~~~~~~~~~~~~~

Each analysis stage contains:

.. code-block:: json

    {
        "id": 1,
        "type": "AnalysisStage",
        "name": "Gravity Analysis",
        "properties": {
            "description": "Static analysis under gravity loads",
            "analysis_type": "Static",
            "load_ids": [1]
        }
    }

- `id`: Stage identifier
- `type`: Stage type
- `name`: Optional name
- `properties`: Type-specific properties

Application Settings
------------------

The application settings section contains settings specific to the Modsee application:

.. code-block:: json

    "app_settings": {
        "display": {
            "show_grid": true,
            "show_nodes": true,
            "show_node_labels": true,
            "show_elements": true,
            "show_element_labels": true
        },
        "units": {
            "length": "m",
            "force": "kN",
            "time": "s"
        }
    }

Example
------

For a complete example, see ``examples/simple_structure.msee``.

Implementation
------------

The Modsee application implements saving and loading of MSEE files in the following classes:

- ``FileService``: Handles the actual reading and writing of MSEE files
- ``ApplicationManager``: Coordinates the saving and loading of projects
- ``ModelManager``: Manages the model components that are saved and loaded

Future Enhancements
-----------------

Future versions of the MSEE file format may include:

1. Support for multiple model domains (structural, thermal, etc.)
2. Version migration tools for backward compatibility
3. Support for external references to shared model components
4. Embedded analysis results
5. Compression for large models 
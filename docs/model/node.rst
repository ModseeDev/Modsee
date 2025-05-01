Node Class
=========

The ``Node`` class represents points in space with degrees of freedom (DOFs) in the finite element model.

Overview
--------

Nodes are fundamental to finite element models as they define:

1. The geometry of the model through their coordinates
2. The degrees of freedom (DOFs) that can be restrained (fixed) or free
3. Connection points for elements
4. Locations where masses can be applied
5. Points at which loads and boundary conditions can be applied

Basic Usage
----------

Creating a simple 3D node::

    from model.nodes import Node
    from model.base.core import ModelMetadata
    
    # Create a node at coordinates (10, 20, 30)
    metadata = ModelMetadata(name="My Node")
    node = Node(id=1, metadata=metadata, coordinates=[10.0, 20.0, 30.0])
    
    # Access coordinates
    x = node.get_x()  # 10.0
    y = node.get_y()  # 20.0
    z = node.get_z()  # 30.0

Specifying Fixed DOFs
--------------------

For structural analysis, you can specify which degrees of freedom are fixed (restrained)::

    # Create a node with fixed X translation, free Y and Z translations,
    # free X and Y rotations, and fixed Z rotation
    fixed_dofs = [True, False, False, False, False, True]
    node = Node(id=1, metadata=metadata, coordinates=[10.0, 20.0, 30.0], 
               fixed_dofs=fixed_dofs)
               
    # Check if a DOF is fixed
    is_x_fixed = node.is_dof_fixed(0)  # True (X translation)
    is_y_fixed = node.is_dof_fixed(1)  # False (Y translation)
    is_rz_fixed = node.is_dof_fixed(5)  # True (Z rotation)

Adding Mass
----------

Mass can be added to nodes for dynamic analysis::

    # Add mass in X, Y, and Z directions
    node = Node(id=1, metadata=metadata, coordinates=[10.0, 20.0, 30.0], 
               mass=[1.0, 1.0, 1.0])

Generating OpenSees Code
-----------------------

The Node class can generate both TCL and Python code for OpenSees::

    # Generate TCL code
    tcl_code = node.to_opensees_tcl()
    # Result: "node 1 10.0 20.0 30.0\nmass 1 1.0 1.0 1.0"
    
    # Generate Python code
    py_code = node.to_opensees_py()
    # Result: "ops.node(1, 10.0, 20.0, 30.0)\nops.mass(1, 1.0, 1.0, 1.0)"

API Reference
------------

Constructors
~~~~~~~~~~~

.. code-block:: python

    Node(id: int, metadata: ModelMetadata, coordinates: List[float], 
         mass: Optional[List[float]] = None, fixed_dofs: Optional[List[bool]] = None)

Parameters:
    - **id**: Unique identifier for this node
    - **metadata**: Metadata for this node
    - **coordinates**: Spatial coordinates [x, y, z] (1D, 2D, or 3D)
    - **mass**: Nodal mass in each DOF direction (optional)
    - **fixed_dofs**: Boolean flags for fixed DOFs (optional)
        - For 2D nodes: list of 4 booleans [ux, uy, rz, extra]
        - For 3D nodes: list of 6 booleans [ux, uy, uz, rx, ry, rz]

Methods
~~~~~~

.. code-block:: python

    get_x() -> float  # Get X coordinate
    get_y() -> float  # Get Y coordinate  
    get_z() -> float  # Get Z coordinate
    
    set_x(value: float) -> None  # Set X coordinate
    set_y(value: float) -> None  # Set Y coordinate
    set_z(value: float) -> None  # Set Z coordinate
    
    get_num_dofs() -> int  # Get number of DOFs
    get_dimension() -> int  # Get dimension (1, 2, or 3)
    
    set_fixed_dofs(fixed_dofs: List[bool]) -> None  # Set fixed DOFs
    is_dof_fixed(dof_index: int) -> bool  # Check if a DOF is fixed
    
    validate() -> bool  # Validate node properties
    
    to_dict() -> Dict[str, Any]  # Convert to dictionary
    from_dict(data: Dict[str, Any]) -> Node  # Create from dictionary
    
    to_opensees_tcl() -> str  # Generate OpenSees TCL code
    to_opensees_py() -> str  # Generate OpenSeesPy code 
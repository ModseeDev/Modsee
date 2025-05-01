Testing Documentation
====================

Test Coverage
-----------

This document tracks the test coverage for Modsee components.

Core Infrastructure
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 40 10 10

   * - Component
     - Test Coverage
     - Test Files
     - Status
   * - Dependency Checker
     - Unit tests for dependency checking functionality
     - ``tests/unit/test_dependency_check.py``
     - Implemented
   * - Basic Window
     - Unit tests for window initialization
     - ``tests/unit/test_basic_window.py``
     - Implemented
   * - Application Launch
     - Integration test for application launch
     - ``tests/integration/test_app_launch.py``
     - Implemented
   * - Core Architecture
     - Unit tests for ApplicationManager, Component interfaces, ModelManager, ViewManager, FileService, and Integration
     - ``tests/unit/test_core_architecture.py``
     - Implemented

Running Tests
-----------

To run all tests, use the following command:

.. code-block:: bash

   python run_tests.py

To run specific test files:

.. code-block:: bash

   python -m unittest tests/unit/test_dependency_check.py
   python -m unittest tests/unit/test_basic_window.py
   python -m unittest tests/integration/test_app_launch.py
   python -m unittest tests/unit/test_core_architecture.py

Future Test Coverage
-----------------

The following components still need test coverage:

1. VTK integration
2. Model Explorer panel
3. Properties Editor panel
4. Project file operations
5. Splash screen UI

Test Strategy
-----------

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interaction between components
3. **System Tests**: Test the entire application as a black box
4. **GUI Tests**: Test user interface components and user interactions

Dependencies
----------

The testing framework uses the following dependencies:

- Python's built-in unittest module
- pytest for more advanced test features (as needed)

All dependencies are listed in the requirements.txt file. 
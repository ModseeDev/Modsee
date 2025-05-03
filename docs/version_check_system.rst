Version Check System
===================

Overview
--------

The version check system is designed to verify if the current Modsee application is up-to-date by comparing its version against the latest released version. This document outlines the implementation strategy for this feature.

Requirements
-----------

1. Display the current version number on the splash screen
2. Check for updates during application startup
3. Handle network issues gracefully without blocking application startup
4. Present update information to the user when a new version is available
5. Provide download links for updates
6. Support critical updates that require immediate attention

System Design
------------

Component Integration
~~~~~~~~~~~~~~~~~~~

The version check system will be integrated as follows:

1. A new ``VersionChecker`` service component that will be registered with the ``ApplicationManager``
2. Updates to the ``ModseeSplashScreen`` to display the current version and check status
3. A notification system to inform users about available updates

Data Flow
~~~~~~~~

1. During startup, ``ModseeSplashScreen`` displays the current application version
2. ``VersionChecker`` runs an asynchronous check against the version endpoint
3. If an update is available, a notification is shown to the user after the main window loads
4. For critical updates, a more prominent notification is displayed

Version Check Source
~~~~~~~~~~~~~~~~~~

The version information will be retrieved from:
``https://modsee.net/versions.json``

Example response:

.. code-block:: json

{
  "timestamp": "2025-05-01T15:10:00",
  "channels": {
    "stable": {
      "latest_version": "0.0.1",
      "download_url": "https://example.com/modsee/releases/0.0.1/modsee.zip",
      "release_notes": [
        "Initial stable release with version control check"
      ],
      "critical_update": false
    },
    "beta": {
      "latest_version": "0.1.0-beta",
      "download_url": "https://example.com/modsee/releases/0.1.0-beta/modsee.zip",
      "release_notes": [
        "Experimental UI changes",
        "Support for new elements"
      ],
      "critical_update": false
    },
    "dev": {
      "latest_version": "0.2.0-dev",
      "download_url": "https://example.com/modsee/releases/0.2.0-dev/modsee.zip",
      "release_notes": [
        "In-progress refactoring",
        "Plugin system draft implementation"
      ],
      "critical_update": false
    }
  }
}


Implementation Plan
------------------

1. Create VersionChecker Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new ``VersionChecker`` class in ``utils/version_checker.py`` that:

- Stores the current application version
- Provides methods to check for updates asynchronously
- Handles network errors and timeouts gracefully
- Parses and validates the version data from the server
- Compares versions using semantic versioning rules

2. Update Splash Screen
~~~~~~~~~~~~~~~~~~~~~

Modify ``ui/splash_screen.py`` to:

- Display the current application version (already implemented)
- Display the version check status during startup
- Maintain the existing dependency check flow

3. Create Update Notification
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new ``UpdateNotification`` dialog that:

- Displays information about available updates
- Shows release notes
- Provides links to download the new version
- Has different styling for critical vs. regular updates

4. Integration with Application Flow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Modify the application startup flow to:

- Register the ``VersionChecker`` with the ``ApplicationManager``
- Trigger the version check during splash screen display
- Show notifications after the main window is displayed
- Store the "last checked" timestamp to avoid excessive checks

Error Handling
-------------

The version check system will handle the following error conditions:

1. Network Unavailable
~~~~~~~~~~~~~~~~~~~

If the network is unavailable or the version endpoint cannot be reached:

- Log a warning message
- Continue application startup without blocking
- Allow manual version checking from the Help menu
- Retry on next application startup

2. Invalid Response
~~~~~~~~~~~~~~~~

If the response from the server is invalid or cannot be parsed:

- Log an error message
- Continue application startup
- Use cached version information if available

3. Version Comparison Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~

If version strings cannot be properly compared:

- Log an error message
- Assume current version is up-to-date
- Allow manual update checking

User Experience
--------------

1. Regular Updates
~~~~~~~~~~~~~~~~

For non-critical updates:

- A notification badge appears in the main window's status bar
- Clicking the badge shows update information
- The update notification is non-intrusive

2. Critical Updates
~~~~~~~~~~~~~~~~~

For updates marked as critical:

- A more prominent modal dialog appears after startup prompting the user to update to the latest version, program will not run if not updated
- The dialog explains the importance of updating
- This option reserved for rare cases and will be forced to update to the latest version

Configuration
------------

The version check system will support the following configuration options:

1. Include/exclude pre-release versions
2. Proxy settings for network connections

These settings will be integrated into the existing application settings dialog.

Testing Strategy
--------------

The version check system will be tested with:

1. Unit tests to verify version comparison logic
2. Mock server tests to verify handling of different response scenarios
3. Integration tests to verify proper display of update notifications
4. Error condition tests to verify graceful handling of network issues

Timeline and Priority
-------------------

This feature is identified as FUNC-019 in the task list with Low priority. The implementation should focus on the following key principles:

1. Non-blocking operation - The application must start even if version checking fails
2. Simplicity - Keep the implementation straightforward and maintainable
3. User control - Allow users to select update channels. Stable, Beta, and Dev. Stable will be the default and only checked by default.
4. Security - Ensure secure communication with the version endpoint
5. Version control is a must and cannot be disabled.

Implementation in multiple phases is recommended:

Phase 1: Basic version checking and notification
Phase 2: Critical update handling
Phase 3: User configuration and advanced options 
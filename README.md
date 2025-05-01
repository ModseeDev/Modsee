# Modsee

**Modsee** is an open-source graphical modeling platform designed to simplify the development of finite element models for OpenSees and OpenSeesPy users.  
It provides a modern, intuitive user interface for building, managing, visualizing, and exporting structural and geotechnical models, without the need for manual scripting.

---

## ✨ Features (planned)

- Graphical model builder (nodes, elements, materials, boundary conditions)
- Support for core OpenSees element types (2D, 3D, springs, soils)
- Material library management
- Project save/load system
- Export models to both OpenSees TCL scripts and OpenSeesPy scripts
- Integrated OpenSeesPy runner
- Model visualization with VTK or similar tools
- Cross-platform: Windows, macOS, Linux
- Intuitive graphical interface for model creation and visualization
- Support for staged analysis with progressive model changes
- Analysis results visualization
- Automatic association between model files (.msee) and results files (.h5)
- Model builder flexibility with different configurations for each stage

---

## 🛠️ Current Status

Modsee is in early development.  
Initial architecture focuses on building a modular, extensible, and scalable foundation to support long-term growth.

Stay tuned for early alpha releases and development milestones!

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/modsee/modsee.git
   cd modsee
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. For development, install the development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. To use OpenSeesPy integration, install the OpenSeesPy package:
   ```bash
   pip install -e ".[openseespy]"
   ```

### Running the Application

Run the application using the provided runner script:
```bash
python run.py
```

Alternatively, you can install the package and run the application using the console script:
```bash
pip install -e .
modsee
```

---

## 📦 Project Structure

```
Modsee/
├── src/                    # Source code
│   ├── main.py             # Application entry point
│   ├── app.py              # Main application class
│   ├── config.py           # Configuration management
│   ├── ui/                 # UI components
│   │   ├── main_window.py  # Main application window
│   │   ├── dialogs/        # Popup dialogs
│   │   ├── widgets/        # Custom widgets
│   │   └── style/          # UI themes and styling
│   ├── models/             # Data models
│   │   ├── project.py      # Project data structure
│   │   ├── geometry/       # Geometry definitions
│   │   ├── materials/      # Material definitions
│   │   ├── elements/       # Element definitions
│   │   ├── mesh/           # Meshing algorithms
│   │   └── analysis/       # Analysis settings
│   ├── io/                 # Input/Output operations
│   │   ├── project_io.py   # Project save/load
│   │   ├── opensees_exporter.py    # OpenSees TCL export
│   │   └── openseespy_exporter.py  # OpenSeesPy export
│   ├── visualization/      # Visualization components
│   │   ├── scene.py        # 3D scene management
│   │   └── renderer.py     # Rendering engine
│   └── utils/              # Utility functions
│       └── helpers.py      # Common helper functions
├── resources/              # Static resources
│   ├── icons/              # UI icons
│   ├── materials/          # Material databases
│   └── templates/          # Export templates
├── tests/                  # Automated tests
│   └── test_project.py     # Project model tests
├── docs/                   # Documentation
├── examples/               # Example projects
├── requirements.txt        # Python dependencies
├── setup.py                # Installation script
├── run.py                  # Development runner script
├── README.md
└── LICENSE
```

---

## 🧪 Running Tests

To run the tests:
```bash
pytest
```

For a specific test file:
```bash
pytest tests/test_project.py
```

---

## 📢 Contribution

Contributions, ideas, and discussions are welcome!  
Once the base structure is finalized, clear guidelines for contributing (issues, pull requests, coding standards) will be published.

If you are interested in early contributions or testing, feel free to open an issue or contact us.

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0**.

You are free to use, modify, and distribute Modsee under the terms of the GPLv3.  
See the full license text here: [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt).

---

## 📬 Stay Updated

- Star this repo!
- Bookmark [modsee.net](https://modsee.net) for project updates
- Join discussions and issue tracking once opened

---

> Built with passion for open-source engineering modeling.

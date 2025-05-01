# Modsee Examples

This directory contains example models and scripts for the Modsee structural analysis software.

### File Naming Convention

Modsee uses two primary file types:
- `.msee` files: Model definition files containing the structural model information
- `.h5` or `.hdf5` files: Results files containing analysis results

When working with Modsee:
1. Input models are stored in `.msee` files (JSON format)
2. Analysis results are stored in `.h5` files (HDF5 format)

#### Automatic Results Association

In Post-Processing mode, Modsee will automatically look for a results file with the same base name as the model file. For example:
- If you open `my_model.msee`, Modsee will automatically look for `my_model.h5` or `my_model.hdf5` in the same directory
- If the matching results file is not found, you'll be prompted to select it manually

This allows for a seamless workflow between model definition and results visualization without requiring manual file selection for each analysis.

### Example Files

- `cantilever_beam.msee` and `cantilever_beam_results.h5`: A multi-stage cantilever beam analysis with different loading conditions
- `multi_builder_bridge.msee` and `multi_builder_bridge.h5`: A bridge model demonstrating different model builders for different stages
- Other examples demonstrating various features of Modsee

### Model Builder Customization

Each stage in a model can have its own model builder configuration. The `custom_model_builder.py` example demonstrates how to define and use different model builders for different stages of analysis. See `model_builder_readme.md` for more details.

### Running Examples

To run an example script:

```
python examples/cantilever_beam_example.py
```

This will generate the corresponding `.msee` and `.h5` files in the examples directory.

## HDF5 File Format Example

The `hdf5_example.py` script demonstrates how to create, save and load a model using the HDF5 file format. 

### Running the Example

To run the example:

```bash
python -m examples.hdf5_example
```

This will:
1. Create a sample truss bridge model
2. Save it to HDF5 format in the `examples/output` directory
3. Add simulated analysis results
4. Re-load the model and display model information and results

### Viewing the HDF5 File in Modsee

To open the HDF5 example file in Modsee:

1. Run Modsee using: `python run.py`
2. Click on the "Open" button or select File > Open from the menu
3. Navigate to the `examples/output` folder
4. Select `sample_bridge.h5` and click Open

The model will load in Modsee and display in the Model Explorer. You can expand the nodes in the Model Explorer to see the model components and analysis results.

## HDF5 File Structure

The HDF5 file format used by Modsee has the following structure:

```
/Project
  /ModelDefinition
    /Nodes
      /1
        id, coordinates, mass
      /2
        ...
    /Elements
      /1
        id, type, material, nodes, ...
      /2
        ...
    /Materials
      /1
        id, type, properties
      /2
        ...
    /BoundaryConditions
      ...
    /Loads
      ...
    /AnalysisSettings
      ...
  /AnalysisResults
    /analysis_id_1
      time_steps
      /NodeResults
        /1
          ...
      /ElementResults
        /1
          ...
    /analysis_id_2
      ...
```

This hierarchical structure allows for efficient storage of both model definitions and large analysis results. 
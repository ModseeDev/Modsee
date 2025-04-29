# Modsee Examples

This directory contains example files for Modsee.

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
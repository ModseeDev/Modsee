# OpenSeesPy code for multi-stage analysis
import openseespy.opensees as ops

# Initialize model
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# --------------------------------------------------
# Stage: Initial Configuration
# Description: Base geometry and boundary conditions
# --------------------------------------------------

# Create nodes
ops.node(1, 0.0, 0.0, 0.0)
ops.node(2, 5.0, 0.0, 0.0)
ops.node(3, 5.0, 5.0, 0.0)
ops.node(4, 0.0, 5.0, 0.0)

# Define boundary conditions
ops.fix(1, 1, 1, 1, 1, 1, 1)  # Fix node 1 in all DOFs

# Set up analysis for this stage
# Stage 1: Initial Configuration
# Type: STATIC
# Description: Base geometry and boundary conditions
# Setting up analysis for stage 1
ops.wipeAnalysis()
ops.system('BandGeneral')
ops.constraints('Plain')
ops.numberer('RCM')
ops.test('NormDispIncr', 1.0e-6, 10)
ops.algorithm('Newton')
ops.integrator('LoadControl', 1.0)
ops.analysis('Static')

# Apply loads for this stage

# Run analysis for this stage
print('Running analysis for stage: Initial Configuration')
for i in range(10):
    ops.analyze(1)
    print(f'  Step {i+1}/{num_steps} completed')

# Commit state before moving to next stage
ops.reactions()

# --------------------------------------------------
# Stage: First Load Case
# Description: Apply first set of loads
# --------------------------------------------------

# Set up analysis for this stage
# Stage 2: First Load Case
# Type: STATIC
# Description: Apply first set of loads
# Setting up analysis for stage 2
ops.wipeAnalysis()
ops.system('BandGeneral')
ops.constraints('Plain')
ops.numberer('RCM')
ops.test('NormDispIncr', 1.0e-6, 10)
ops.algorithm('Newton')
ops.integrator('LoadControl', 1.0)
ops.analysis('Static')

# Apply loads for this stage
# Using load pattern: uniform
# Applying uniform loads to all nodes
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Run analysis for this stage
print('Running analysis for stage: First Load Case')
for i in range(20):
    ops.analyze(1)
    print(f'  Step {i+1}/{num_steps} completed')

# Commit state before moving to next stage
ops.reactions()

# --------------------------------------------------
# Stage: Second Load Case
# Description: Apply second set of loads
# --------------------------------------------------

# Set up analysis for this stage
# Stage 3: Second Load Case
# Type: STATIC
# Description: Apply second set of loads
# Setting up analysis for stage 3
ops.wipeAnalysis()
ops.system('BandGeneral')
ops.constraints('Plain')
ops.numberer('RCM')
ops.test('NormDispIncr', 1.0e-6, 10)
ops.algorithm('Newton')
ops.integrator('LoadControl', 1.0)
ops.analysis('Static')

# Apply loads for this stage
# Using load pattern: triangular
# Applying triangular distribution of loads
ops.timeSeries('Linear', 2)
ops.pattern('Plain', 2, 2)

# Run analysis for this stage
print('Running analysis for stage: Second Load Case')
for i in range(20):
    ops.analyze(1)
    print(f'  Step {i+1}/{num_steps} completed')

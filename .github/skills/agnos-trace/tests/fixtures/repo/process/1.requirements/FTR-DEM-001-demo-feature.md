# FTR-DEM-001: Demo Feature

## Overview
A synthetic feature for the agnos-trace tests.

## Functional Requirements

### RQ-DEM-001: Covered directly
- **Category**: Functional
- **Statement**: The system SHALL be cited by a source file.
- **Dependencies**: None

### RQ-DEM-002: Covered indirectly
- **Category**: Functional
- **Statement**: The system SHALL be cited only by a task that a source file cites.
- **Dependencies**: RQ-DEM-001

### RQ-DEM-003: Uncovered but tasked
- **Category**: Functional
- **Statement**: The system SHALL be cited by a task and by an excluded file only.
- **Dependencies**: None

### RQ-DEM-004: Uncovered and untasked
- **Category**: Functional
- **Statement**: The system SHALL be cited by a decision only.
- **Dependencies**: None

### RQ-DEM-005: Isolated
- **Category**: Functional
- **Statement**: Nothing cites this requirement.
- **Dependencies**: None

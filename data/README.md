# Data Dictionary

All datasets in this directory are model-generated outputs. They are not
independent experimental measurements.

## `awe_current_temperature_1bar.csv`

A current-temperature parameter sweep at approximately constant pressure.

| Property | Value |
|---|---:|
| Rows | 2,450 |
| Temperature points | 50 |
| Current points | 49 |
| Temperature range | 273 to 373 K |
| Current range | 3.061 to 150.000 A |
| Voltage range | 1.4643 to 2.1294 V |
| Bubble-coverage range | 0.0477 to 0.5441 |
| Hydrogen-flux range | 0.000529 to 0.025900 |

### Columns

| Column | Unit | Description |
|---|---|---|
| `Temperature` | K | Cell and electrolyte temperature |
| `Current` | A | Total current supplied to the cell |
| `Voltage` | V | Predicted single-cell voltage |
| `Theta` | Dimensionless | Predicted gas-bubble surface coverage |
| `Hflux` | Model unit | Predicted hydrogen-production flux from the model |

## `awe_pressure_temperature_90a.csv`

A pressure-temperature parameter sweep at a fixed total current of 90 A.

| Property | Value |
|---|---:|
| Rows | 2,900 |
| Temperature points | 50 |
| Pressure points | 58 |
| Temperature range | 273 to 373 K |
| Pressure range | 1.017 to 30.000 bar |
| Voltage range | 1.7379 to 1.9800 V |
| Bubble-coverage range | 0.0668 to 0.4668 |

### Columns

| Column | Unit | Description |
|---|---|---|
| `Temperature` | K | Cell and electrolyte temperature |
| `Pressure` | bar | Operating pressure |
| `Voltage` | V | Predicted single-cell voltage |
| `Theta` | Dimensionless | Predicted gas-bubble surface coverage |

## Interpretation

The project presentation reports comparison with HRI and PHOEBUS
polarisation data over a narrower temperature and pressure domain.
Values outside that reported comparison domain should be treated as
exploratory model extrapolations rather than validated predictions.

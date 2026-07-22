# Validation, Scope, and Limitations

## Model scope

The model represents a one-dimensional alkaline water electrolysis cell
with coupled electrochemical, transport, ohmic, and gas-bubble effects.

Principal inputs include current, temperature, anode pressure, cathode
pressure, and electrolyte properties. Principal outputs include cell
voltage, overpotentials, gas fluxes, and electrode bubble coverage.

## Reported comparison domain

The accompanying project presentation reports comparison with HRI and
PHOEBUS electrolyser polarisation curves across approximately:

- Temperature: 35 to 80 degrees Celsius
- Pressure: 1 to 9 bar

## Exploratory sweep domain

The public parameter-sweep datasets extend to:

- Temperature: 273 to 373 K
- Pressure: approximately 1 to 30 bar
- Current: approximately 3 to 150 A

Results outside the reported comparison domain should be interpreted as
model-based sensitivity studies and possible extrapolations.

## Scientific-use warning

- The CSV files are simulation outputs, not raw experimental measurements.
- The model should not be used for equipment sizing, safety decisions, or
  commercial guarantees without independent validation.
- Reproduce one known baseline case before changing model parameters.
- Document any equation, parameter, or correlation changed from the
  uploaded model.

# tomato-drycal
`tomato` driver for MesaLabs DryCal volumetric flow meters.

This driver is based on the serial interface for the DryCal devices. This driver is developed by the [ConCat lab at TU Berlin](https://tu.berlin/en/concat).

## Supported functions

### Capabilities
- `measure_flow` for measuring the volumetric flow on on the device.

### Attributes
- `piston` for determining piston state, `RO`, `int`

## Contributors

- Peter Kraus

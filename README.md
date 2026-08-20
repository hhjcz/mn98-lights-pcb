# MN98 Lights PCB

Passive body-light distribution boards for the MN98 RC car and DumboRC P6DC
receiver. The P6DC already controls the LEDs, so variants in this repository
must not add transistors, MOSFETs, resistors, regulators, capacitors, or GND.

## Shared P6DC Interface

The receiver manual is in `docs/`. The light channels follow the P6DC physical
output order: left cornering, right cornering, brake, flash, back-up, and
daytime running light. Any detachable body-to-chassis cable must preserve that
order without crossed conductors.

Before connecting a body harness, confirm LED polarity with a meter. Do not
infer it from wire colours or connector orientation.

## Archived JST-PH Variant

`v1.0-jst-ph/` contains the original JST-PH work-in-progress, including its
KiCad project, Gerbers, PDFs, connector-specific documentation and skill.
It is preserved as a reference and must not be overwritten by the next design.

## Next Variant

The repository root is reserved for a new design based on paired LED lights
with 2-pin Dupont female connectors. Keep it as an independent KiCad project
so both connector strategies remain maintainable side by side.

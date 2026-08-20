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

## Dupont Variant, First Revision

`pcb-svetla-mn98.kicad_sch` and `pcb-svetla-mn98.kicad_pcb` are the first
compact passive version. The board uses a right-angle JST-XH 1x8 P6DC harness
input and three right-angle 2.54 mm male headers for the paired Dupont LEDs:
the initial placement is 32 x 42 mm, dominated by the XH connector's body.

| Header | Physical pairs, top to bottom |
| --- | --- |
| J1, 1x4 | `COMMON+ / LEFT`, `COMMON+ / RIGHT` |
| J2, 1x6 | `COMMON+ / DRL`, `COMMON+ / BRAKE`, `COMMON+ / BACK-UP` |
| J3, 1x6 | `COMMON+ / MARKER`, `COMMON+ / RAMP`, `COMMON+ / SPARE` |

JP1, JP2 and JP3 select `DRL` or `FLASH` respectively for MARKER, RAMP and
SPARE. Fit the shunt across pins 1-2 for DRL, or 2-3 for FLASH. All right-angle
connectors face outward from the board. The headers are intentionally unkeyed:
silkscreen marks the common-positive side of every pair. Confirm the supplied
LED pair polarity before connecting power.

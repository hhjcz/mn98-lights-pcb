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

## Dupont Body Distributor

`pcb-svetla-mn98.kicad_sch` and `pcb-svetla-mn98.kicad_pcb` are the first
compact passive body-side distributor. The current placement candidate is
32 x 36 mm, within the verified 40 x 50 mm maximum envelope. It uses two
merged right-angle 2.54 mm male headers for paired Dupont LEDs. The left header
contains LEFT TURN and DRL. The right header contains RIGHT TURN, BRAKE,
BACK-UP, MARKER, RAMP and SPARE. Both JST-PH body-link connectors exit left so
their harnesses run toward the same chassis location.
All connector courtyards are inside the board outline. Routing is intentionally
deferred until the mechanical placement and JST-PH orientation are approved.
The JST-PH courtyards are inset 2.5 mm from the left edge to protect the
connectors and leave board material around their through-hole pads.

| Header | Physical pairs, top to bottom |
| --- | --- |
| J1, 1x4 | `COMMON+ / LEFT`, `COMMON+ / DRL` |
| J2, 1x12 | `COMMON+ / RIGHT`, `COMMON+ / BRAKE`, `COMMON+ / BACK-UP`, `COMMON+ / MARKER`, `COMMON+ / RAMP`, `COMMON+ / SPARE` |

JP1, JP2 and JP3 select `DRL` or `FLASH` respectively for MARKER, RAMP and
SPARE. Fit the shunt across pins 1-2 for DRL, or 2-3 for FLASH. All right-angle
connectors face outward from the board. The headers are intentionally unkeyed:
silkscreen marks the common-positive side of every pair. Confirm the supplied
LED pair polarity before connecting power.

### Body Link

The detachable body link uses two right-angle JST-PH 1x4 THT connectors. Pin 1
is `COMMON+` on both connectors, so swapping cables A and B cannot connect a
signal output to common positive; it only exchanges light functions.

| Connector | Pin 1 | Pin 2 | Pin 3 | Pin 4 |
| --- | --- | --- | --- | --- |
| J14, link A | `COMMON+` | `LEFT` | `RIGHT` | `BRAKE` |
| J15, link B | `COMMON+` | `FLASH` | `BACK-UP` | `DRL` |

Use pin-to-pin female-female harnesses. A practical custom-length harness can
be made from two pre-crimped JST-PH 4-pin pigtails joined wire-for-wire. Verify
continuity and pin order with a meter before connecting the receiver.

### Planned P6DC Adapter

A second passive PCB will plug into the six 2-pin P6DC light outputs through a
2x6 Dupont female socket and expose matching J14/J15 JST-PH connectors. It
will join the P6DC common-positive pins and preserve the pinout above. The
adapter is intentionally deferred until its fit against the receiver has been
measured. Both designs may later share one customer-panel PCB for fabrication.

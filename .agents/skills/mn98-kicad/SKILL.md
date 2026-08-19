---
name: mn98-kicad
description: Use when editing the MN98 DumboRC P6DC light-distribution KiCad PCB, its schematic, routing, connector assignment, jumper selection, DRC, or manufacturing outputs.
---

# MN98 Light Distribution PCB

## Scope

This board is a passive body-side lighting adapter for an MN98 RC car and a
DumboRC P6DC receiver. It contains connectors, copper routing, labels, and
configuration jumpers only. Do not add resistors, transistors, MOSFETs,
capacitors, regulators, or any GND connection.

The current files are `pcb-svetla-mn98.kicad_pcb`,
`pcb-svetla-mn98.kicad_sch`, and `generate_pcb.py`. Regenerate the board with
`/usr/bin/python3 generate_pcb.py` after changing the generator.

## P6DC Input

J14 is an eight-position right-angle JST-PH connector:

| Pin | Net |
| --- | --- |
| 1 | COMMON+ |
| 2 | COMMON+ |
| 3 | LEFT |
| 4 | RIGHT |
| 5 | BRAKE |
| 6 | FLASH |
| 7 | BACK-UP |
| 8 | DRL |

Pins 1 and 2 must be connected together on the PCB. They feed every LED
connector's pad 1 via a wide common-positive spine. There is no ground net:
each LED's pad 2 is its P6DC controlled return/channel.

Pins 3--8 must preserve the top-to-bottom P6DC light-output order [14]--[19]:
left cornering, right cornering, brake, flash, back-up, and DRL. The chassis
cable is a pin-to-pin harness; never reverse its conductor order between plugs.

## Output Assignment

J1 left front turn: LEFT.
J2 right front turn: RIGHT.
J3 left rear turn: LEFT.
J4 right rear turn: RIGHT.
J5 spare: FLASH.
J6/J10 main headlights: DRL.
J7/J11 front marker lights: MARKER through JP1.
J8/J12 rear red lights: REAR_RED through JP2.
J9 roof ramp: RAMP through JP3.
J13 spare: DRL.

Use right-angle JST-PH S2B-PH-K footprints for all LED outputs and the P6DC
input. Keep them around three PCB edges with cable exit facing outward.

## Jumper Requirements

JP1 is a 1x03, 2.54 mm header. Its centre is MARKER; shunt it to DRL or FLASH.

JP2 is a 2x03, 2.54 mm header. One vertical shunt must select exactly one
source, DRL, BRAKE, or BACK-UP, for both rear-red outputs. The three pads on
the output row must be copper-connected as REAR_RED.

JP3 is a 1x03, 2.54 mm header. Its centre is RAMP; shunt it to DRL or FLASH.

## Layout And Release Checks

- Board target size is 30 x 40 mm, two-layer 1.6 mm FR-4.
- Keep the COMMON+ spine at least 1.2 mm wide; use sensible signal widths.
- Do not create a copper zone or net named GND.
- Run KiCad DRC after every routing change and resolve all errors and
  unconnected ratsnest edges before declaring a fabrication release.
- Export Gerbers only after a clean DRC. Treat existing Gerbers as inspection
  artifacts until then.
- Confirm the real available MN98 body space before changing the outline.
- Confirm every existing LED lead's JST-PH pin 1 and electrical polarity with
  a meter. Never infer polarity from wire colour or connector orientation.

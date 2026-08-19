# MN98 light distribution PCB

Passive 30 x 40 mm, two-layer FR-4 adapter for the MN98 body lighting and
DumboRC P6DC. The board contains no active components and has no GND net.

## Input J14

J14 is an 8-position right-angle JST-PH connector. Pin 1 is marked on the
footprint. P6DC wiring is:

| Pin | Net |
| --- | --- |
| 1 | COMMON+ |
| 2 | COMMON+ |
| 3 | LEFT |
| 4 | RIGHT |
| 5 | BRAKE |
| 6 | BACK-UP |
| 7 | DRL |
| 8 | FLASH |

Pins 1 and 2 are connected to the same 1.2 mm common-positive spine. LED
connector pad 1 is COMMON+ and pad 2 is the controlled P6DC channel.

## LED outputs

| Connector | Function | Controlled net |
| --- | --- | --- |
| J1 | Left front turn | LEFT |
| J2 | Right front turn | RIGHT |
| J3 | Left rear turn | LEFT |
| J4 | Right rear turn | RIGHT |
| J5 | Spare | FLASH |
| J6 | Left 5 mm headlight | DRL |
| J7 | Left 3 mm marker | MARKER via JP1 |
| J8 | Left rear red | REAR_RED via JP2 |
| J9 | Roof ramp | RAMP via JP3 |
| J10 | Right 5 mm headlight | DRL |
| J11 | Right 3 mm marker | MARKER via JP1 |
| J12 | Right rear red | REAR_RED via JP2 |
| J13 | Spare | DRL |

All J1--J13 are right-angle JST-PH S2B-PH-K footprints.

## Jumper settings

JP1 and JP3 are 1x03 headers. Fit one 2.54 mm shunt between the centre pin
and the selected outside pin.

| Jumper | Left position | Right position |
| --- | --- | --- |
| JP1 | DRL -> MARKER | MARKER -> FLASH |
| JP3 | DRL -> RAMP | RAMP -> FLASH |

JP2 is a 2x03 header. Fit one vertical 2.54 mm shunt in the column labelled
DRL, BRAKE, or BACK-UP to connect that channel to both rear-red connectors.

## Before manufacturing

1. Check that 30 x 40 mm fits the exact available MN98 body cavity.
2. Check the mating housing and the actual pin-1/polarity of every MN98 LED
   lead. Do not infer it from lead colours or connector orientation.
3. Open `pcb-svetla-mn98.kicad_pcb` in KiCad PCB Editor, run DRC, and resolve
   the two JP2 ratsnest indicators before ordering. The generated Gerbers are
   an inspection aid, not a released fabrication package.

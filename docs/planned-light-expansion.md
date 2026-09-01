# Planned Light Expansion

> **DRAFT / UNVERIFIED**
>
> This document records ideas for a possible future revision. It is not the
> electrical specification of the current PCB. Do not update the schematic,
> PCB placement, routing, silkscreen, or manufacturing files from this document
> until the relevant measurements and decisions below are complete.

## Purpose

The current body distributor predates two purchased modules that may simplify
the chassis-to-body connection and add independently controlled auxiliary
lights. This draft preserves the proposed architecture and the assumptions that
must be tested when the modules arrive.

The intended future revision would:

- replace the planned custom P6DC adapter with a purchased six-wire adapter;
- omit the P6DC FLASH output, which is a true strobe function not currently
  needed on the MN98;
- use semantic body-light names instead of names copied from the P6DC manual;
- allow ROOF LIGHT to follow HEADLIGHTS or switch port 1;
- allow FRONT MARKER and SPARE to follow HEADLIGHTS or switch port 2;
- reserve one optional through-hole series-resistor position for each of those
  three outputs;
- remain a passive PCB containing only connectors, copper routing, labels,
  solder-select jumpers, and any explicitly approved series resistors.

The committed 32 x 36 mm placement-only design remains the active design until
this draft is verified and explicitly approved for a new placement revision.

## Purchased Modules

### Six-wire P6DC light adapter

Product page:

<https://www.aliexpress.com/item/1005008835970185.html>

Observed before delivery:

- the body-side connector appears to be a six-pin JST-PH connector;
- the adapter appears to use six conductors and omit FLASH;
- the likely functions are COMMON+, LEFT, RIGHT, TAIL/BRAKE, REVERSE, and
  HEADLIGHTS, but their physical order and polarity are not known.

The connector series, pin 1, conductor order, continuity, and polarity must all
be checked on the delivered part. The listing is not sufficient evidence for
an electrical pinout.

### DumboRC CH3 light controller

Product page:

<https://www.aliexpress.com/item/1005005666804975.html>

Installation video showing the same type of module:

<https://www.youtube.com/watch?v=yQgD09w_WAs>

Video demonstrating the two outputs and seven-state sequence:

<https://www.youtube.com/watch?v=6RompNNfQf8>

Local reference images copied from the product listing:

- [`ddf350-3ch-switch-overview.webp`](ddf350-3ch-switch-overview.webp)
- [`ddf350-3ch-switch-modes.webp`](ddf350-3ch-switch-modes.webp)
- [`ddf350-3ch-switch-jr-input.webp`](ddf350-3ch-switch-jr-input.webp)
- [`ddf350-3ch-switch-dimensions.webp`](ddf350-3ch-switch-dimensions.webp)
- [`ddf350-3ch-switch-output.webp`](ddf350-3ch-switch-output.webp)
- [`ddf350-3ch-switch-angle.webp`](ddf350-3ch-switch-angle.webp)

The listing calls this a `3CH LED Light Controller`, while the installation
video calls it a `Ch3 Light Control Module`. The latter interpretation is much
more consistent with the visible wiring: the controller is intended for the
receiver's CH3 output rather than providing three independently controlled LED
channels.

The listing and video show:

- one three-wire female JR receiver lead;
- one four-pin 2.54 mm male output, apparently arranged as two 2-pin LED ports;
- an approximately 24 x 10 mm controller body;
- approximately 120 mm overall length including the receiver lead;
- advertised on, off, breathing, and flashing effects.

The second video provides stronger evidence that the four pins are two
separately controlled 2-pin LED outputs:

```text
SWITCH PORT 1: + / -
SWITCH PORT 2: + / -
```

The ports are not fully independent because one receiver input cycles through a
fixed sequence, but the sequence can activate port 1 alone, port 2 alone, or
both ports. Treat them as `SW1+ / SW1-` and `SW2+ / SW2-`. Neither physical pin
order nor the electrical topology is verified on the delivered unit. The
photographs and videos must not be used as the final pinout. The controller may
use low-side switching, protection components, current regulation, or a supply
path that makes either positive output unsuitable for direct connection to
P6DC COMMON+.

The module has one PWM receiver input. The demonstrated controller advances
through seven output states when that input is clicked:

| State | Port 1 | Port 2 |
| --- | --- | --- |
| 1 | steady | off |
| 2 | slow pulse | off |
| 3 | off | steady |
| 4 | off | slow pulse |
| 5 | steady | steady |
| 6 | slow pulse | slow pulse |
| 7 | random flashing | random flashing |

The delivered unit must still be tested because firmware variants may use a
different order or behaviour.

## Proposed Light Names

Future PCB silkscreen should use the function on the vehicle:

| PCB label | Intended function | Probable source |
| --- | --- | --- |
| `LEFT TURN` | Left indicators | P6DC left output |
| `RIGHT TURN` | Right indicators | P6DC right output |
| `HEADLIGHTS` | Main front lights | P6DC DRL output |
| `TAIL / BRAKE` | Rear low-intensity tail and high-intensity brake | P6DC brake output |
| `REVERSE` | Reverse lights | P6DC back-up output |
| `FRONT MARKER` | Front marker lights | HEADLIGHTS or switch port 2 |
| `ROOF LIGHT` | Roof light bar | HEADLIGHTS or switch port 1 |
| `SPARE` | Future auxiliary light | HEADLIGHTS or switch port 2 |

The probable P6DC mapping is based on observed behaviour discussed during
planning. It must be checked across every P6DC light mode before becoming part
of the schematic specification.

## Preferred Electrical Architecture

The preferred architecture assumes that the P6DC light common positive,
receiver supply positive, switch port 1 positive, and switch port 2 positive
are the same electrical rail.

```text
Purchased P6DC adapter, 6 wires
  COMMON+ ----------------------+---------------- standard light positives
  LEFT -------------------------+---------------- LEFT TURN negative
  RIGHT ------------------------+---------------- RIGHT TURN negative
  TAIL/BRAKE -------------------+---------------- TAIL / BRAKE negative
  REVERSE ----------------------+---------------- REVERSE negative
  HEADLIGHTS -------------------+---------------- HEADLIGHTS negative
                                |
CH3 switch, two output ports    |
  SW1+ -------------------------+  only if verified as the same rail
  SW1- ---------------------------- roof selector
  SW2+ -------------------------+  only if verified as the same rail
  SW2- --------+------------------- marker selector
                +------------------- spare selector
```

With a verified shared positive rail, only the switched negative conductor of
each optional light needs selection:

```text
ROOF +   ------------------------------ COMMON+
ROOF -   -- R_ROOF -- [ HEADLIGHTS- | SW1- ]

MARKER + ------------------------------ COMMON+
MARKER - -- R_MARKER -- [ HEADLIGHTS- | SW2- ]

SPARE +  ------------------------------ COMMON+
SPARE -  -- R_SPARE -- [ HEADLIGHTS- | SW2- ]
```

This gives the following intended configurations:

| Output | Default or simple source | Alternate switch source |
| --- | --- | --- |
| `ROOF LIGHT` | `HEADLIGHTS` | `SWITCH PORT 1` |
| `FRONT MARKER` | `HEADLIGHTS` | `SWITCH PORT 2` |
| `SPARE` | `HEADLIGHTS` | `SWITCH PORT 2` |

FRONT MARKER and SPARE operate together when both select switch port 2. Their
combined current must remain within port 2's measured safe capacity. ROOF LIGHT
uses port 1 and can be activated separately in the demonstrated sequence.

TAIL/BRAKE is intentionally not a proposed FRONT MARKER source. Connecting the
front markers to that output would make them change intensity when braking,
which is not the intended vehicle behaviour.

Each three-pad selector must have unambiguous silkscreen showing the two valid
bridges. Simultaneously bridging both sides would connect two controlled
outputs and must be treated as an invalid configuration.

## Safe Fallback Architecture

If the two positive outputs are not proven to be the same rail, do not connect
them. ROOF LIGHT, FRONT MARKER, and SPARE must then use two-pole source
selection so both LED conductors move together between sources.

```text
HEADLIGHTS +  [ ]-[ ROOF + ]-[ ]  SW1+
HEADLIGHTS -  [ ]-[ ROOF - ]-[ ]  SW1-

HEADLIGHTS +  [ ]-[ MARKER + ]-[ ] SW2+
HEADLIGHTS -  [ ]-[ MARKER - ]-[ ] SW2-

HEADLIGHTS +  [ ]-[ SPARE + ]-[ ]  SW2+
HEADLIGHTS -  [ ]-[ SPARE - ]-[ ]  SW2-
```

This fallback needs six three-pad solder selectors instead of three. Both rows
for one light must always be set to the same side. Crossed or double-bridged
settings are invalid and could connect the P6DC and switch outputs together.
The corresponding `R_ROOF`, `R_MARKER`, or `R_SPARE` position remains in series
with each load after its two-pole selector.

The fallback remains the required design assumption until the common-positive
tests pass.

## Optional Series Resistors

The controller's 5-6 V open-circuit output does not prove whether it includes
LED current regulation. Do not add a resistor value based on that voltage
alone. Measure the output current-versus-load characteristic and inspect each
light assembly for an existing resistor.

The proposed PCB should nevertheless reserve three independent horizontal THT
positions:

```text
Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal
```

| Position | Load |
| --- | --- |
| `R_ROOF` | ROOF LIGHT |
| `R_MARKER` | FRONT MARKER |
| `R_SPARE` | SPARE |

Fit a calculated resistor only when the selected light and source require it.
Fit a 0-ohm THT link or insulated wire link when current limiting already exists
in the controller or light assembly. An unused output may remain open.

FRONT MARKER and SPARE need separate resistor positions even though they share
switch port 2. A single resistor before the split would make their brightness
and current depend on whether one or both loads are connected.

Adding these optional resistors would intentionally revise the current project
rule that prohibits resistors. Do not change the skill or active schematic
until measurements show that the positions are useful and this scope change is
explicitly approved.

## Connector Plan

The connector plan is provisional:

- one six-pin JST-PH input for the purchased P6DC light adapter, subject to
  physical connector and pinout verification;
- one 1x4 2.54 mm female Dupont socket for the CH3 switch's two separate
  2-pin output ports;
- existing unkeyed two-pin Dupont body-light outputs with a visible `+` mark.

The switch can potentially plug directly into the PCB socket. Placement must
reserve clearance for its approximately 24 x 10 mm body, heat-shrink sleeve,
and receiver cable. Direct mounting must not use the switch pins as the only
mechanical support where vibration can fatigue them.

An alternative is a short four-wire extension. In that case the PCB connector
gender depends on the selected cable, so the final footprint should not be
chosen before deciding whether the module is direct-mounted or cable-mounted.

## DDF-350 Control Plan

The CH3 switch should connect to one unused P6DC receiver channel. The DDF-350
must generate whatever single-channel PWM command sequence the module expects.

Possible behaviours include:

- a short transition to an endpoint acting as a button press;
- sequential state changes on repeated button transitions;
- the seven-state sequence documented above;
- a different sequence in another firmware revision.

The ports are separately addressable only through the controller's fixed state
sequence; they are not two freely assignable receiver channels. Transmitter
buttons, switches, endpoints, and mixes should be configured only after
recording the delivered controller's actual state machine.

## Verification Procedure

### Safety

- Perform resistance and continuity measurements only with all power removed.
- Start powered tests with a current-limited supply where practical.
- Do not connect the two candidate positive rails together merely to test
  whether they are compatible.
- Test with inexpensive LEDs or an appropriate dummy load before connecting
  the vehicle light sets.
- Verify every unkeyed connector orientation and LED polarity with a meter.

### Six-wire adapter pinout

Record the actual pin numbering from the connector's mating face, not from the
cable side.

| Pin | Wire colour | P6DC connection | Measured function | Verified |
| --- | --- | --- | --- | --- |
| 1 | TBD | TBD | TBD | no |
| 2 | TBD | TBD | TBD | no |
| 3 | TBD | TBD | TBD | no |
| 4 | TBD | TBD | TBD | no |
| 5 | TBD | TBD | TBD | no |
| 6 | TBD | TBD | TBD | no |

Confirm that FLASH is absent rather than silently combined with another
function.

### CH3 switch pinout

Record pin order from a clearly identified end of the four-pin header.

| Pin | PCB marking | Continuity | Observed output | Verified |
| --- | --- | --- | --- | --- |
| 1 | TBD | TBD | TBD | no |
| 2 | TBD | TBD | TBD | no |
| 3 | TBD | TBD | TBD | no |
| 4 | TBD | TBD | TBD | no |

Check the JR lead separately:

| JR conductor | Expected role | Verified role |
| --- | --- | --- |
| Black | GND | TBD |
| Red | Receiver supply positive | TBD |
| White | PWM signal | TBD |

### Common-positive decision gate

The preferred single-pole selectors are allowed only after all of these checks
pass:

1. Both switch output positives have near-zero resistance to JR red with the
   module unpowered.
2. The two switch output positives have near-zero resistance to each other.
3. P6DC light COMMON+ has near-zero resistance to receiver supply positive with
   the receiver unpowered.
4. All candidate positives measure the same voltage relative to receiver GND
   when powered.
5. The voltage difference remains negligible under representative LED load and
   in every relevant light mode.
6. No diode, regulator, current limiter, or protected output separates any
   positive from the receiver supply rail.
7. Supplying one connection cannot back-power a module through an output in an
   undocumented way.

If any check fails or remains ambiguous, use the two-pole fallback and keep the
positive rails separate.

### Switch behaviour matrix

First record the state after power-up and after signal loss. Then test stable
endpoint positions, short endpoint pulses, repeated pulses, and held commands.

| Input action or state | Port 1 | Port 2 | Persists after neutral | Notes |
| --- | --- | --- | --- | --- |
| Power on | TBD | TBD | TBD | |
| First click | expected steady | expected off | TBD | |
| Second click | expected slow pulse | expected off | TBD | |
| Third click | expected off | expected steady | TBD | |
| Fourth click | expected off | expected slow pulse | TBD | |
| Fifth click | expected steady | expected steady | TBD | |
| Sixth click | expected slow pulse | expected slow pulse | TBD | |
| Seventh click | expected random flash | expected random flash | TBD | |
| PWM signal removed | TBD | TBD | TBD | |
| Power cycled | TBD | TBD | TBD | |

Identify steady on, steady off, breathing, flashing, and any sequence
dependency. Confirm which states operate only one port and whether the previous
state is retained after a power cycle.

### Switch current-limiting test

Test each port separately in its steady-on state using known resistive loads.
Start with a high resistance and decrease it cautiously while recording voltage
and calculated current. Do not short the output.

| Load | Voltage | Calculated current | Port | Notes |
| --- | --- | --- | --- | --- |
| 1 kohm | TBD | TBD | TBD | |
| 470 ohm | TBD | TBD | TBD | |
| 330 ohm | TBD | TBD | TBD | |
| 220 ohm | TBD | TBD | TBD | only if earlier results are safe |

Open-circuit voltage is not evidence of current regulation. A useful LED
current source should show a safe, repeatable current plateau; a high-current
short-circuit protection threshold is not a substitute for LED current
regulation.

## Placement Deferred

A local 40 x 44 mm placement experiment confirmed that the planned connectors,
three vertical 1/4 W THT resistor footprints, and three low-profile solder
selectors can fit within the verified 40 x 50 mm envelope without routing. It
is not an approved placement and should not be committed as the next board
revision.

The current preferred connector directions for the next experiment are:

- J3, the six-pin JST-PH adapter input, should face and exit toward the left;
- J4, the right-angle 1x4 female switch socket, should sit at the bottom board
  edge and allow the switch module or its cable to extend downward;
- LEFT TURN and HEADLIGHTS Dupont pairs should remain accessible from the left;
- the other six Dupont pairs should remain accessible from the right.

Final placement is deferred until the available body volume is measured. The
MN98 shock mounts, structural braces, body posts, windows, interior parts, and
cable bend radii may all constrain the PCB outline and connector exits. The
active schematic should also remain unchanged because both purchased module
pinouts are unverified.

## Mechanical Checks

Before revising placement:

- measure the delivered six-pin adapter plug and its cable exit;
- measure the four-pin switch header pitch, pin length, and pin orientation;
- measure the switch body including heat shrink rather than relying on the
  advertised 24 x 10 mm PCB dimensions;
- decide whether the switch mounts directly to the body PCB or through an
  extension cable;
- map the positions and required clearance of the shock mounts, structural
  braces, body posts, windows, and interior parts;
- check insertion, removal, connector access, and cable bend clearance against
  that obstacle map;
- retain the verified maximum 40 x 50 mm PCB envelope;
- keep complete connector courtyards inside the outline where practical.

## Approval Gates

No active design files should change until the electrical measurements above
are recorded and the following decisions are explicit:

1. Final six-pin adapter pinout and orientation.
2. Final four-pin switch pinout and mounting method.
3. Shared-positive or isolated-positive architecture.
4. Usable CH3 switch sequence and behaviour of both output ports.
5. Confirmation of port 1 for ROOF LIGHT and port 2 for FRONT MARKER and SPARE.
6. Decision whether the three optional THT resistor positions are required.
7. Final selector defaults and silkscreen labels.

After approval, the project must return to the placement workflow:

1. Update the schematic and placement generator without tracks.
2. Generate a placement-only PCB and review outline, connectors, orientation,
   cable exits, switch clearance, and labels.
3. Route only after the new placement is explicitly approved.
4. Run ERC, DRC, netlist, visual, and fabrication-output checks before Gerbers.

## Current Open Questions

- What is the exact six-wire adapter pin order?
- Is its connector definitely JST-PH and which side presents pin 1?
- Is P6DC DRL the preferred HEADLIGHTS behaviour in every configured mode?
- Is P6DC BRAKE consistently low-intensity tail plus high-intensity brake?
- What is the exact four-pin switch output order?
- What is the `+ / -` order of each switch output pair?
- Are P6DC COMMON+, receiver positive, SW1+, and SW2+ one electrical rail?
- Does the delivered module follow the demonstrated seven-state sequence?
- Which button or mix configuration should the DDF-350 use to advance it?
- Should the switch plug directly into the PCB or use an extension harness?
- Does either switch port provide suitable LED current regulation?
- What current can each switch port safely drive?
- Do the actual roof, marker, and spare light assemblies contain resistors?
- What should happen to ROOF LIGHT, FRONT MARKER, and SPARE when the switch is
  absent?

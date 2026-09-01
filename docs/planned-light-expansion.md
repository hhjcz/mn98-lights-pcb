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
- allow ROOF LIGHT and FRONT MARKER to follow HEADLIGHTS or use separate
  outputs of a three-channel RC light switch;
- connect SPARE to the remaining output of that switch;
- remain a passive PCB containing only connectors, copper routing, labels, and
  solder-select jumpers.

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

### DumboRC three-channel light controller

Product page:

<https://www.aliexpress.com/item/1005005666804975.html>

Local reference images copied from the product listing:

- [`ddf350-3ch-switch-overview.webp`](ddf350-3ch-switch-overview.webp)
- [`ddf350-3ch-switch-modes.webp`](ddf350-3ch-switch-modes.webp)
- [`ddf350-3ch-switch-jr-input.webp`](ddf350-3ch-switch-jr-input.webp)
- [`ddf350-3ch-switch-dimensions.webp`](ddf350-3ch-switch-dimensions.webp)
- [`ddf350-3ch-switch-output.webp`](ddf350-3ch-switch-output.webp)
- [`ddf350-3ch-switch-angle.webp`](ddf350-3ch-switch-angle.webp)

The listing calls this a `3CH LED Light Controller` and shows:

- one three-wire female JR receiver lead;
- one four-pin 2.54 mm male output;
- an approximately 24 x 10 mm controller body;
- approximately 120 mm overall length including the receiver lead;
- advertised on, off, breathing, and flashing effects.

The photographs appear to mark the four-pin output as three switched negative
channels plus one common positive. The working hypothesis is therefore:

```text
SWITCH CH1- | SWITCH CH2- | SWITCH CH3- | SWITCH+
```

Neither the order nor the electrical topology is verified. The photographs
must not be used as the final pinout. The controller may use different output
ordering, low-side switching, protection components, or a supply path that
makes its positive output unsuitable for direct connection to P6DC COMMON+.

`3CH` describes three LED outputs, not three receiver inputs. The module has
one PWM receiver input. Its firmware likely decodes pulse positions or a
sequence of transitions to operate the three outputs.

## Proposed Light Names

Future PCB silkscreen should use the function on the vehicle:

| PCB label | Intended function | Probable source |
| --- | --- | --- |
| `LEFT TURN` | Left indicators | P6DC left output |
| `RIGHT TURN` | Right indicators | P6DC right output |
| `HEADLIGHTS` | Main front lights | P6DC DRL output |
| `TAIL / BRAKE` | Rear low-intensity tail and high-intensity brake | P6DC brake output |
| `REVERSE` | Reverse lights | P6DC back-up output |
| `FRONT MARKER` | Front marker lights | HEADLIGHTS or switch CH2 |
| `ROOF LIGHT` | Roof light bar | HEADLIGHTS or switch CH1 |
| `SPARE` | Future auxiliary light | Switch CH3 |

The probable P6DC mapping is based on observed behaviour discussed during
planning. It must be checked across every P6DC light mode before becoming part
of the schematic specification.

## Preferred Electrical Architecture

The preferred architecture assumes that the P6DC light common positive, the
receiver supply positive, and the three-channel switch output positive are the
same electrical rail.

```text
Purchased P6DC adapter, 6 wires
  COMMON+ ----------------------+---------------- standard light positives
  LEFT -------------------------+---------------- LEFT TURN negative
  RIGHT ------------------------+---------------- RIGHT TURN negative
  TAIL/BRAKE -------------------+---------------- TAIL / BRAKE negative
  REVERSE ----------------------+---------------- REVERSE negative
  HEADLIGHTS -------------------+---------------- HEADLIGHTS negative
                                |
Three-channel switch, 4 pins    |
  SWITCH+ ----------------------+  only if verified as the same rail
  CH1- -------- roof selector
  CH2- -------- marker selector
  CH3- -------------------------- SPARE negative
```

With a verified shared positive rail, only the switched negative conductor of
ROOF LIGHT and FRONT MARKER needs selection:

```text
ROOF +   ------------------------------ COMMON+
ROOF -   ---- [ HEADLIGHTS- | CH1- ] --- one 3-pad solder selector

MARKER + ------------------------------ COMMON+
MARKER - -- [ HEADLIGHTS- | CH2- ] ----- one 3-pad solder selector

SPARE +  ------------------------------ COMMON+
SPARE -  ------------------------------ CH3-
```

This gives the following intended configurations:

| Output | Default or simple source | Optional independent source |
| --- | --- | --- |
| `ROOF LIGHT` | `HEADLIGHTS` | `SWITCH CH1` |
| `FRONT MARKER` | `HEADLIGHTS` | `SWITCH CH2` |
| `SPARE` | none | `SWITCH CH3`, fixed |

TAIL/BRAKE is intentionally not a proposed FRONT MARKER source. Connecting the
front markers to that output would make them change intensity when braking,
which is not the intended vehicle behaviour.

Each three-pad selector must have unambiguous silkscreen showing the two valid
bridges. Simultaneously bridging both sides would connect two controlled
outputs and must be treated as an invalid configuration.

## Safe Fallback Architecture

If the two positive outputs are not proven to be the same rail, do not connect
them. ROOF LIGHT and FRONT MARKER must then use two-pole source selection so
both LED conductors move together between sources.

```text
HEADLIGHTS +  [ ]-[ ROOF + ]-[ ]  SWITCH+
HEADLIGHTS -  [ ]-[ ROOF - ]-[ ]  CH1-

HEADLIGHTS +  [ ]-[ MARKER + ]-[ ] SWITCH+
HEADLIGHTS -  [ ]-[ MARKER - ]-[ ] CH2-
```

This fallback needs four three-pad solder selectors instead of two. Both rows
for one light must always be set to the same side. Crossed or double-bridged
settings are invalid and could connect the P6DC and switch outputs together.

The fallback remains the required design assumption until the common-positive
tests pass.

## Connector Plan

The connector plan is provisional:

- one six-pin JST-PH input for the purchased P6DC light adapter, subject to
  physical connector and pinout verification;
- one 1x4 2.54 mm female Dupont socket for the three-channel switch output;
- existing unkeyed two-pin Dupont body-light outputs with a visible `+` mark.

The switch can potentially plug directly into the PCB socket. Placement must
reserve clearance for its approximately 24 x 10 mm body, heat-shrink sleeve,
and receiver cable. Direct mounting must not use the switch pins as the only
mechanical support where vibration can fatigue them.

An alternative is a short four-wire extension. In that case the PCB connector
gender depends on the selected cable, so the final footprint should not be
chosen before deciding whether the module is direct-mounted or cable-mounted.

## DDF-350 Control Plan

The three-channel switch should connect to one unused P6DC receiver channel.
The DDF-350 must generate whatever single-channel PWM command sequence the
module expects.

Possible behaviours include:

- fixed PWM ranges selecting different states;
- a short transition to an endpoint acting as a button press;
- sequential state changes on repeated transitions;
- one global sequence covering all three LED outputs;
- separate commands encoded by different pulse widths.

Do not assume that CH1, CH2, and CH3 can be independently toggled until this is
demonstrated. Transmitter buttons, switches, endpoints, and mixes should be
configured only after recording the controller's actual state machine.

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

### Three-channel switch pinout

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

1. The switch output positive has near-zero resistance to JR red with the
   module unpowered.
2. P6DC light COMMON+ has near-zero resistance to receiver supply positive with
   the receiver unpowered.
3. Both candidate positives measure the same voltage relative to receiver GND
   when powered.
4. The voltage difference remains negligible under representative LED load and
   in every relevant light mode.
5. No diode, regulator, current limiter, or protected output separates either
   positive from the receiver supply rail.
6. Supplying one connection cannot back-power a module through an output in an
   undocumented way.

If any check fails or remains ambiguous, use the two-pole fallback and keep the
positive rails separate.

### Switch behaviour matrix

First record the state after power-up and after signal loss. Then test slow PWM
sweeps, stable endpoint positions, short endpoint pulses, repeated pulses, and
held commands.

| Input action | CH1 | CH2 | CH3 | Persists after neutral | Notes |
| --- | --- | --- | --- | --- | --- |
| Power on | TBD | TBD | TBD | TBD | |
| Low endpoint held | TBD | TBD | TBD | TBD | |
| Low endpoint pulse | TBD | TBD | TBD | TBD | |
| High endpoint held | TBD | TBD | TBD | TBD | |
| High endpoint pulse | TBD | TBD | TBD | TBD | |
| Repeated pulse | TBD | TBD | TBD | TBD | |
| PWM signal removed | TBD | TBD | TBD | TBD | |
| Power cycled | TBD | TBD | TBD | TBD | |

For each channel, identify steady on, steady off, breathing, flashing, and any
sequence dependency. Also check whether the previous state is retained after a
power cycle.

## Mechanical Checks

Before revising placement:

- measure the delivered six-pin adapter plug and its cable exit;
- measure the four-pin switch header pitch, pin length, and pin orientation;
- measure the switch body including heat shrink rather than relying on the
  advertised 24 x 10 mm PCB dimensions;
- decide whether the switch mounts directly to the body PCB or through an
  extension cable;
- check removal clearance and ensure the roof module does not collide with the
  MN98 body, windows, interior, or mounting posts;
- retain the verified maximum 40 x 50 mm PCB envelope;
- keep complete connector courtyards inside the outline where practical.

## Approval Gates

No active design files should change until the electrical measurements above
are recorded and the following decisions are explicit:

1. Final six-pin adapter pinout and orientation.
2. Final four-pin switch pinout and mounting method.
3. Shared-positive or isolated-positive architecture.
4. Usable CH1, CH2, and CH3 controller behaviour.
5. Final assignment of controller channels to ROOF LIGHT, FRONT MARKER, and
   SPARE.
6. Final selector defaults and silkscreen labels.

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
- Does the switch use three low-side outputs and one common positive?
- Are P6DC COMMON+, receiver positive, and SWITCH+ one electrical rail?
- Can all three switch outputs be independently controlled from one PWM input?
- Which output modes and command sequence does the DDF-350 need?
- Should the switch plug directly into the PCB or use an extension harness?
- What current can each switch channel safely drive?
- What should happen to ROOF LIGHT and FRONT MARKER when the switch is absent?

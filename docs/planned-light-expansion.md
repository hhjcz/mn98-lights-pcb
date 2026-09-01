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
- allow ROOF LIGHT, FRONT MARKER, and SPARE to follow HEADLIGHTS or use the
  common output of a CH3 RC light switch;
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

### DumboRC CH3 light controller

Product page:

<https://www.aliexpress.com/item/1005005666804975.html>

Installation video showing the same type of module:

<https://www.youtube.com/watch?v=yQgD09w_WAs>

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

The working hypothesis is that the four pins are two electrically parallel
copies of the same switched LED output:

```text
SWITCH PORT 1: + / -
SWITCH PORT 2: + / -
```

Both ports appear to switch together and provide the same effect. They should
be treated as one electrical source named `SWITCH+ / SWITCH-`, not as separate
channels. Neither pin order, the parallel connection, nor the electrical
topology is verified on the delivered unit. The photographs and video must not
be used as the final pinout. The controller may use different output ordering,
low-side switching, protection components, or a supply path that makes its
positive output unsuitable for direct connection to P6DC COMMON+.

The module has one PWM receiver input. Its firmware likely decodes pulse
positions or a sequence of transitions to switch the shared output and select
on, off, breathing, or flashing modes.

## Proposed Light Names

Future PCB silkscreen should use the function on the vehicle:

| PCB label | Intended function | Probable source |
| --- | --- | --- |
| `LEFT TURN` | Left indicators | P6DC left output |
| `RIGHT TURN` | Right indicators | P6DC right output |
| `HEADLIGHTS` | Main front lights | P6DC DRL output |
| `TAIL / BRAKE` | Rear low-intensity tail and high-intensity brake | P6DC brake output |
| `REVERSE` | Reverse lights | P6DC back-up output |
| `FRONT MARKER` | Front marker lights | HEADLIGHTS or SWITCH |
| `ROOF LIGHT` | Roof light bar | HEADLIGHTS or SWITCH |
| `SPARE` | Future auxiliary light | HEADLIGHTS or SWITCH |

The probable P6DC mapping is based on observed behaviour discussed during
planning. It must be checked across every P6DC light mode before becoming part
of the schematic specification.

## Preferred Electrical Architecture

The preferred architecture assumes that the P6DC light common positive, the
receiver supply positive, and the CH3 switch output positive are the same
electrical rail.

```text
Purchased P6DC adapter, 6 wires
  COMMON+ ----------------------+---------------- standard light positives
  LEFT -------------------------+---------------- LEFT TURN negative
  RIGHT ------------------------+---------------- RIGHT TURN negative
  TAIL/BRAKE -------------------+---------------- TAIL / BRAKE negative
  REVERSE ----------------------+---------------- REVERSE negative
  HEADLIGHTS -------------------+---------------- HEADLIGHTS negative
                                |
CH3 switch, two parallel ports  |
  SWITCH+ ----------------------+  only if verified as the same rail
  SWITCH- ------+--------------- roof selector
                +--------------- marker selector
                +--------------- spare selector
```

With a verified shared positive rail, only the switched negative conductor of
each optional light needs selection:

```text
ROOF +   ------------------------------ COMMON+
ROOF -   ---- [ HEADLIGHTS- | SWITCH- ] --- one 3-pad solder selector

MARKER + ------------------------------ COMMON+
MARKER - -- [ HEADLIGHTS- | SWITCH- ] ----- one 3-pad solder selector

SPARE +  ------------------------------ COMMON+
SPARE -  --- [ HEADLIGHTS- | SWITCH- ] --- one 3-pad solder selector
```

This gives the following intended configurations:

| Output | Default or simple source | Alternate shared source |
| --- | --- | --- |
| `ROOF LIGHT` | `HEADLIGHTS` | `SWITCH` |
| `FRONT MARKER` | `HEADLIGHTS` | `SWITCH` |
| `SPARE` | `HEADLIGHTS` | `SWITCH` |

All outputs selected to `SWITCH` operate together. The PCB may fan the shared
switch output out to more loads than the module's two physical ports, but their
combined current must remain within the controller's measured safe capacity.

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
HEADLIGHTS +  [ ]-[ ROOF + ]-[ ]  SWITCH+
HEADLIGHTS -  [ ]-[ ROOF - ]-[ ]  SWITCH-

HEADLIGHTS +  [ ]-[ MARKER + ]-[ ] SWITCH+
HEADLIGHTS -  [ ]-[ MARKER - ]-[ ] SWITCH-

HEADLIGHTS +  [ ]-[ SPARE + ]-[ ]  SWITCH+
HEADLIGHTS -  [ ]-[ SPARE - ]-[ ]  SWITCH-
```

This fallback needs six three-pad solder selectors instead of three. Both rows
for one light must always be set to the same side. Crossed or double-bridged
settings are invalid and could connect the P6DC and switch outputs together.

The fallback remains the required design assumption until the common-positive
tests pass.

## Connector Plan

The connector plan is provisional:

- one six-pin JST-PH input for the purchased P6DC light adapter, subject to
  physical connector and pinout verification;
- one 1x4 2.54 mm female Dupont socket for the CH3 switch's two parallel
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

- fixed PWM ranges selecting different states;
- a short transition to an endpoint acting as a button press;
- sequential state changes on repeated transitions;
- one sequence controlling both parallel LED ports together;
- separate commands encoded by different pulse widths.

Do not assume that the two physical LED ports can be controlled independently.
Current evidence indicates that they always operate together. Transmitter
buttons, switches, endpoints, and mixes should be configured only after
recording the controller's actual state machine.

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

| Input action | Port 1 | Port 2 | Outputs match | Persists after neutral | Notes |
| --- | --- | --- | --- | --- | --- |
| Power on | TBD | TBD | TBD | TBD | |
| Low endpoint held | TBD | TBD | TBD | TBD | |
| Low endpoint pulse | TBD | TBD | TBD | TBD | |
| High endpoint held | TBD | TBD | TBD | TBD | |
| High endpoint pulse | TBD | TBD | TBD | TBD | |
| Repeated pulse | TBD | TBD | TBD | TBD | |
| PWM signal removed | TBD | TBD | TBD | TBD | |
| Power cycled | TBD | TBD | TBD | TBD | |

Identify steady on, steady off, breathing, flashing, and any sequence
dependency. Confirm that both ports remain synchronized in every mode and check
whether the previous state is retained after a power cycle.

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
4. Usable CH3 switch behaviour and confirmation that both output ports match.
5. Final assignment of the shared SWITCH source to ROOF LIGHT, FRONT MARKER,
   and SPARE selectors.
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
- Are the four switch pins two parallel `+ / -` output pairs?
- Are P6DC COMMON+, receiver positive, and SWITCH+ one electrical rail?
- Do both physical switch ports remain synchronized in every mode?
- Which shared output modes and command sequence does the DDF-350 need?
- Should the switch plug directly into the PCB or use an extension harness?
- What total current can the shared switch output safely drive?
- What should happen to ROOF LIGHT, FRONT MARKER, and SPARE when the switch is
  absent?

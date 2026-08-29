---
name: mn98-p6dc
description: Use when designing or reviewing any MN98 body-light PCB that connects to a DumboRC P6DC receiver, including connector selection, P6DC pin order, cable harnesses, LED polarity, or passive routing.
---

# MN98 DumboRC P6DC Light Interface

## Scope

The P6DC controls all light channels. The PCB is a passive body-side harness
adapter only: connectors, routing, labels, and optional selection jumpers are
allowed. Do not add GND, resistors, MOSFETs, transistors, capacitors,
regulators, or other active electronics.

## P6DC Light Order

The P6DC manual is in `docs/`. Its physical light-output order is:

1. Left cornering light
2. Right cornering light
3. Brake
4. Flash
5. Back-up
6. Daytime running light (DRL)

When using an eight-wire body-to-chassis harness with duplicated common
positive, use this order: `COMMON+`, `COMMON+`, `LEFT`, `RIGHT`, `BRAKE`,
`FLASH`, `BACK-UP`, `DRL`. Wire mating connectors pin-to-pin without reversing
the conductor order.

## Required Checks

- Verify the physical connector, pin 1 orientation, and cable order at both
  ends before applying power.
- Verify LED polarity with a meter; lead colours and unkeyed Dupont housings
  are not reliable polarity indicators.
- If a prewired LED pair shares one two-pin connector, both LEDs must use the
  same P6DC channel. Left and right turn signals need separate pairs.
- Use a wide common-positive route and adequate track width for each channel.
- Run ERC, DRC and a visual review before producing Gerbers.

## Required Design Workflow

For every new PCB or substantial connector-layout revision, work in these
separate approval stages:

1. Place footprints and define the board outline without routing tracks.
2. Review and approve dimensions, connector orientation, cable exits,
   clearances, and mechanical fit.
3. Route the PCB only after the placement and outline have been explicitly
   approved.

Do not combine initial placement and routing in one revision. If placement
changes after routing, return to the placement-review stage before rerouting.

## Variants

`v1.0-jst-ph/` is an archived JST-PH design. Do not alter it while creating a
new connector variant. Connector-specific design rules belong in that new
variant's own skill or README.

## Current Dupont Body Distributor

The active root-project design is the passive body-side distributor. Treat the
following as current requirements until explicitly revised:

- Maximum verified PCB envelope: 40 x 50 mm.
- Keep the board as small as practical and keep complete connector courtyards
  inside the outline where possible.
- Current placement candidate: 32 x 36 mm, with no routing until approved.
- Use two merged right-angle 2.54 mm Dupont output headers:
  - Left J1, 1x4: `COMMON+ / LEFT`, `COMMON+ / DRL`.
  - Right J2, 1x12: `COMMON+ / RIGHT`, `COMMON+ / BRAKE`,
    `COMMON+ / BACK-UP`, `COMMON+ / MARKER`, `COMMON+ / RAMP`,
    `COMMON+ / SPARE`.
- Left and right turn-light cables must exit the corresponding body side.
- Use two right-angle JST-PH 1x4 THT body-link connectors on the same side of
  the board so both harnesses run toward the same chassis location:
  - Link A / J14: pin 1 `COMMON+`, pin 2 `LEFT`, pin 3 `RIGHT`, pin 4 `BRAKE`.
  - Link B / J15: pin 1 `COMMON+`, pin 2 `FLASH`, pin 3 `BACK-UP`, pin 4 `DRL`.
- Keeping `COMMON+` on pin 1 of both links makes an A/B cable swap non-critical:
  it exchanges light functions but does not put a signal on the common pin.
- Custom-length body-link cables may be made by joining two pre-crimped 4-pin
  JST-PH pigtails pin-to-pin. Verify continuity before use.
- Keep JP1-JP3 as 2.54 mm 1x3 THT selector headers for now. Low-profile headers
  and shunts may be fitted without changing the footprint.
- Do not add jumper descriptions during placement review; add them after the
  connector layout is approved.
- Top silkscreen must prioritize explicit light-port names and a visible `+`
  for each unkeyed Dupont pair. Omit group titles such as MAIN, AUX, and TURN.
  The body-link connectors only need clear matching labels `A` and `B`.

## Planned P6DC Adapter

A second passive PCB is planned but not yet designed. It will plug into the six
2-pin P6DC light outputs with a 2x6 Dupont female socket and expose matching
JST-PH links A and B. It must preserve the body-link pinout above, join only
the P6DC common-positive pins, and contain no active components or GND. The two
PCB designs may later be placed on one customer panel for fabrication, but the
adapter must first go through the placement-review-routing workflow.

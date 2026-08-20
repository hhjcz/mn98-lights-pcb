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

## Variants

`v1.0-jst-ph/` is an archived JST-PH design. Do not alter it while creating a
new connector variant. Connector-specific design rules belong in that new
variant's own skill or README.

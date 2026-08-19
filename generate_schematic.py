#!/usr/bin/env python3
"""Generate the MN98 passive light-distribution schematic from scratch."""

from pathlib import Path
from uuid import NAMESPACE_URL, uuid4, uuid5


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "pcb-svetla-mn98.kicad_sch"


def uid():
    return str(uuid4())


def component_uuid(reference):
    return str(uuid5(NAMESPACE_URL, f"mn98-lights-pcb/schematic/{reference}"))


def prop(name, value, x=0, y=0, hidden=False):
    hide = " hide" if hidden else ""
    return f'''    (property "{name}" "{value}" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)){hide})
    )'''


def connector_lib(name, pins, two_column=False):
    pin_defs = []
    for number, x, y, angle in pins:
        pin_defs.append(f'''        (pin passive line (at {x} {y} {angle}) (length 3.81)
          (name "Pin_{number}" (effects (font (size 1.27 1.27))))
          (number "{number}" (effects (font (size 1.27 1.27))))
        )''')
    width = 2.54 if two_column else 0.86
    return f'''    (symbol "MN98:{name}" (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
{prop("Reference", "J", 0, 2.54)}
{prop("Value", name, 0, -5.08)}
{prop("Footprint", "", 0, 0, True)}
{prop("Datasheet", "~", 0, 0, True)}
      (symbol "{name}_1_1"
        (rectangle (start {-width} 1.27) (end {width} {-max(p[2] for p in pins) - 1.27})
          (stroke (width 0.1524) (type default))
          (fill (type background))
        )
{chr(10).join(pin_defs)}
      )
    )'''


LIB_1X2 = connector_lib("Conn_01x02", [("1", 5.08, 0, 180), ("2", 5.08, -2.54, 180)])
LIB_1X3 = connector_lib("Conn_01x03", [("1", 5.08, 0, 180), ("2", 5.08, -2.54, 180), ("3", 5.08, -5.08, 180)])
LIB_1X8 = connector_lib("Conn_01x08", [(str(i), -5.08, 10.16 - i * 2.54, 0) for i in range(1, 9)])
LIB_2X3 = connector_lib(
    "Conn_02x03",
    [("1", -5.08, 0, 0), ("2", 5.08, 0, 180), ("3", -5.08, -2.54, 0),
     ("4", 5.08, -2.54, 180), ("5", -5.08, -5.08, 0), ("6", 5.08, -5.08, 180)],
    two_column=True,
)


def instance(lib_id, reference, value, footprint, x, y, pins, reference_at=None, value_at=None):
    reference_at = reference_at or (x, y + 3)
    value_at = value_at or (x, y - 8)
    lines = [
        f'  (symbol (lib_id "MN98:{lib_id}") (at {x} {y} 0) (unit 1)',
        '    (in_bom yes) (on_board yes) (dnp no)',
        f'    (uuid {component_uuid(reference)})',
        prop("Reference", reference, *reference_at),
        prop("Value", value, *value_at),
        prop("Footprint", footprint, x, y, True),
        prop("Datasheet", "~", x, y, True),
    ]
    lines.extend(f'    (pin "{pin}" (uuid {uid()}))' for pin in pins)
    lines.extend([
        '    (instances',
        '      (project "pcb-svetla-mn98"',
        f'        (path "/{ROOT_UUID}" (reference "{reference}") (unit 1))',
        '      )',
        '    )',
        '  )',
    ])
    return "\n".join(lines)


def label(name, x, y, rotation=0, justify="left"):
    return f'''  (label "{name}" (at {x} {y} {rotation})
    (effects (font (size 1.27 1.27)) (justify {justify} bottom))
    (uuid {uid()})
  )'''


def wire(x1, y1, x2, y2):
    return f'''  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type solid))
    (uuid {uid()})
  )'''


ROOT_UUID = str(uuid5(NAMESPACE_URL, "mn98-lights-pcb/schematic/root"))


def add_1x2(items, labels, reference, value, x, y, signal):
    items.append(instance("Conn_01x02", reference, value,
                          "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", x, y, ("1", "2")))
    # Symbol-local Y is inverted when mapped to the schematic page.
    labels.extend((label("COMMON+", x + 5.08, y), label(signal, x + 5.08, y + 2.54)))


def main():
    items, labels, wires = [], [], []
    outputs = [
        ("J1", "L TURN FRONT", 30, 45, "LEFT"),
        ("J2", "R TURN FRONT", 30, 60, "RIGHT"),
        ("J3", "L TURN REAR", 30, 75, "LEFT"),
        ("J4", "R TURN REAR", 30, 90, "RIGHT"),
        ("J5", "SPARE FLASH", 30, 105, "FLASH"),
        ("J6", "HEADLIGHT L", 90, 45, "DRL"),
        ("J7", "MARKER L", 90, 60, "MARKER"),
        ("J8", "REAR RED L", 90, 75, "REAR_RED"),
        ("J9", "ROOF RAMP", 90, 90, "RAMP"),
        ("J10", "HEADLIGHT R", 150, 45, "DRL"),
        ("J11", "MARKER R", 150, 60, "MARKER"),
        ("J12", "REAR RED R", 150, 75, "REAR_RED"),
        ("J13", "SPARE DRL", 150, 90, "DRL"),
    ]
    for output in outputs:
        add_1x2(items, labels, *output)

    # J14 follows the physical top-to-bottom P6DC output order [14]--[19].
    items.append(instance("Conn_01x08", "J14", "P6DC INPUT",
                          "Connector_JST:JST_PH_S8B-PH-K_1x08_P2.00mm_Horizontal", 225, 80,
                          tuple(str(i) for i in range(1, 9)), reference_at=(230, 96), value_at=(230, 100)))
    for pin, net in enumerate(("COMMON+", "COMMON+", "LEFT", "RIGHT", "BRAKE", "FLASH", "BACK-UP", "DRL"), 1):
        y = 72.38 + (pin - 1) * 2.54
        wires.append(wire(219.92, y, 205, y))
        labels.append(label(net, 205, y, 180, "right"))

    items.append(instance("Conn_01x03", "JP1", "MARKER: DRL / FLASH",
                          "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Horizontal", 150, 120,
                          ("1", "2", "3")))
    for pin, net in enumerate(("DRL", "MARKER", "FLASH")):
        labels.append(label(net, 155.08, 120 + pin * 2.54))

    items.append(instance("Conn_02x03", "JP2", "REAR: DRL / BRAKE / BACK-UP",
                          "Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical", 95, 125,
                          ("1", "2", "3", "4", "5", "6")))
    for pin, net, x, y, side in (("1", "REAR_RED", 89.92, 125, "left"), ("2", "DRL", 100.08, 125, "right"),
                                  ("3", "REAR_RED", 89.92, 127.54, "left"), ("4", "BRAKE", 100.08, 127.54, "right"),
                                  ("5", "REAR_RED", 89.92, 130.08, "left"), ("6", "BACK-UP", 100.08, 130.08, "right")):
        end_x = 80 if side == "left" else 110
        wires.append(wire(x, y, end_x, y))
        labels.append(label(net, end_x, y, 180 if side == "left" else 0, "right" if side == "left" else "left"))

    items.append(instance("Conn_01x03", "JP3", "RAMP: DRL / FLASH",
                          "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Horizontal", 35, 120,
                          ("1", "2", "3")))
    for pin, net in enumerate(("DRL", "RAMP", "FLASH")):
        labels.append(label(net, 40.08, 120 + pin * 2.54))

    content = f'''(kicad_sch (version 20230121) (generator eeschema)
  (uuid {ROOT_UUID})
  (paper "A4")
  (lib_symbols
{LIB_1X2}
{LIB_1X3}
{LIB_1X8}
{LIB_2X3}
  )
{chr(10).join(items)}
{chr(10).join(wires)}
{chr(10).join(labels)}
  (text "MN98 / DumboRC P6DC - PASSIVE LIGHT DISTRIBUTION" (at 105 25 0)
    (effects (font (size 2 2) (thickness 0.35)))
    (uuid {uid()})
  )
  (text "No GND. All LED pad 1 pins are COMMON+. Verify LED connector polarity before use." (at 105 32 0)
    (effects (font (size 1.27 1.27)))
    (uuid {uid()})
  )
  (text "J14: 1/2 COMMON+, 3 LEFT, 4 RIGHT, 5 BRAKE, 6 FLASH, 7 BACK-UP, 8 DRL" (at 105 140 0)
    (effects (font (size 1.27 1.27)))
    (uuid {uid()})
  )
  (sheet_instances
    (path "/" (page "1"))
  )
)\n'''
    OUT.write_text(content)


if __name__ == "__main__":
    main()

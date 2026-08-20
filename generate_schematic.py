#!/usr/bin/env python3
"""Generate the first Dupont-header MN98 light-distribution schematic."""

from pathlib import Path
from uuid import NAMESPACE_URL, uuid4, uuid5


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "pcb-svetla-mn98.kicad_sch"
ROOT_UUID = str(uuid5(NAMESPACE_URL, "mn98-dupont/schematic/root"))


def uid():
    return str(uuid4())


def component_uuid(reference):
    return str(uuid5(NAMESPACE_URL, f"mn98-dupont/schematic/{reference}"))


def prop(name, value, x=0, y=0, hidden=False):
    hide = " hide" if hidden else ""
    return f'''    (property "{name}" "{value}" (at {x} {y} 0)
      (effects (font (size 1.27 1.27)){hide})
    )'''


def connector_lib(name, count, input_side="right"):
    if input_side == "right":
        pins = [(str(i), 5.08, -(i - 1) * 2.54, 180) for i in range(1, count + 1)]
        start, end = -0.86, 0.86
    else:
        pins = [(str(i), -5.08, (count - i) * 2.54, 0) for i in range(1, count + 1)]
        start, end = -0.86, 0.86
    pin_defs = "\n".join(
        f'''        (pin passive line (at {x} {y} {angle}) (length 3.81)
          (name "Pin_{number}" (effects (font (size 1.27 1.27))))
          (number "{number}" (effects (font (size 1.27 1.27))))
        )'''
        for number, x, y, angle in pins
    )
    ys = [pin[2] for pin in pins]
    return f'''    (symbol "MN98:{name}" (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
{prop("Reference", "J", 0, max(ys) + 2.54)}
{prop("Value", name, 0, min(ys) - 5.08)}
{prop("Footprint", "", 0, 0, True)}
{prop("Datasheet", "~", 0, 0, True)}
      (symbol "{name}_1_1"
        (rectangle (start {start} {max(ys) + 1.27}) (end {end} {min(ys) - 1.27})
          (stroke (width 0.1524) (type default))
          (fill (type background))
        )
{pin_defs}
      )
    )'''


LIB_1X3 = connector_lib("Conn_01x03", 3)
LIB_1X4 = connector_lib("Conn_01x04", 4)
LIB_1X6 = connector_lib("Conn_01x06", 6)
LIB_1X8_INPUT = connector_lib("Conn_01x08_Input", 8, "left")


def instance(lib_id, reference, value, footprint, x, y, pins):
    lines = [
        f'  (symbol (lib_id "MN98:{lib_id}") (at {x} {y} 0) (unit 1)',
        '    (in_bom yes) (on_board yes) (dnp no)',
        f'    (uuid {component_uuid(reference)})',
        prop("Reference", reference, x, y + 3),
        prop("Value", value, x, y - 4),
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


def output_connector(items, labels, reference, value, x, y, nets):
    count = len(nets)
    footprint = f"Connector_PinHeader_2.54mm:PinHeader_1x{count:02d}_P2.54mm_Horizontal"
    items.append(instance(f"Conn_01x{count:02d}", reference, value, footprint, x, y,
                          tuple(str(i) for i in range(1, count + 1))))
    for index, net in enumerate(nets):
        labels.append(label(net, x + 5.08, y + index * 2.54))


def main():
    items, labels, wires = [], [], []

    # The board silkscreen identifies each physical COMMON+ / channel pair.
    # J1 and J2 are rotated towards the left board edge, so their electrical
    # pin order is reversed relative to the visible top-to-bottom pair order.
    output_connector(items, labels, "J1", "TURN PAIRS", 35, 55,
                     ("RIGHT", "COMMON+", "LEFT", "COMMON+"))
    output_connector(items, labels, "J2", "MAIN LIGHTS", 35, 80,
                     ("BACK-UP", "COMMON+", "BRAKE", "COMMON+", "DRL", "COMMON+"))
    output_connector(items, labels, "J3", "AUX LIGHTS", 120, 55,
                     ("COMMON+", "MARKER", "COMMON+", "RAMP", "COMMON+", "SPARE"))

    items.append(instance("Conn_01x08_Input", "J14", "P6DC INPUT",
                          "Connector_JST:JST_XH_S8B-XH-A_1x08_P2.50mm_Horizontal",
                          210, 82, tuple(str(i) for i in range(1, 9))))
    input_nets = ("COMMON+", "COMMON+", "LEFT", "RIGHT", "BRAKE", "FLASH", "BACK-UP", "DRL")
    for pin, net in enumerate(input_nets, 1):
        y = 82 - (8 - pin) * 2.54
        wires.append(wire(204.92, y, 192, y))
        labels.append(label(net, 192, y, 180, "right"))

    for reference, value, y, output_net in (
        ("JP1", "MARKER: DRL / FLASH", 120, "MARKER"),
        ("JP2", "RAMP: DRL / FLASH", 135, "RAMP"),
        ("JP3", "SPARE: DRL / FLASH", 150, "SPARE"),
    ):
        items.append(instance("Conn_01x03", reference, value,
                              "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
                              100, y, ("1", "2", "3")))
        for index, net in enumerate(("DRL", output_net, "FLASH")):
            labels.append(label(net, 105.08, y + index * 2.54))

    content = f'''(kicad_sch (version 20230121) (generator eeschema)
  (uuid {ROOT_UUID})
  (paper "A4")
  (lib_symbols
{LIB_1X3}
{LIB_1X4}
{LIB_1X6}
{LIB_1X8_INPUT}
  )
{chr(10).join(items)}
{chr(10).join(wires)}
{chr(10).join(labels)}
  (text "MN98 / DumboRC P6DC - PASSIVE DUPONT LIGHT DISTRIBUTION" (at 110 25 0)
    (effects (font (size 2 2) (thickness 0.35)))
    (uuid {uid()})
  )
  (text "No GND and no active parts. The J1-J3 silkscreen marks every physical COMMON+ / channel pair." (at 110 32 0)
    (effects (font (size 1.27 1.27)))
    (uuid {uid()})
  )
  (text "JP1-JP3: fit one shunt between pins 1-2 for DRL or pins 2-3 for FLASH. Verify each LED pair polarity before use." (at 110 165 0)
    (effects (font (size 1.27 1.27)))
    (uuid {uid()})
  )
  (text "J14: 1/2 COMMON+, 3 LEFT, 4 RIGHT, 5 BRAKE, 6 FLASH, 7 BACK-UP, 8 DRL. Body harness is wired pin-to-pin." (at 110 172 0)
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

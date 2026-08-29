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
LIB_1X12 = connector_lib("Conn_01x12", 12)
LIB_1X4_INPUT = connector_lib("Conn_01x04_Input", 4, "left")


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

    # Each body side uses one merged Dupont header. The tuples account for J1
    # facing left and J2 facing right while keeping every physical pair +/signal.
    output_connector(items, labels, "J1", "LEFT LIGHT PORTS", 35, 60,
                     ("DRL", "COMMON+", "LEFT", "COMMON+"))
    output_connector(items, labels, "J2", "RIGHT LIGHT PORTS", 120, 55,
                     ("COMMON+", "RIGHT", "COMMON+", "BRAKE", "COMMON+",
                      "BACK-UP", "COMMON+", "MARKER", "COMMON+", "RAMP",
                      "COMMON+", "SPARE"))

    for reference, value, y, input_nets in (
        ("J14", "BODY LINK A", 75, ("COMMON+", "LEFT", "RIGHT", "BRAKE")),
        ("J15", "BODY LINK B", 110, ("COMMON+", "FLASH", "BACK-UP", "DRL")),
    ):
        items.append(instance("Conn_01x04_Input", reference, value,
                              "Connector_JST:JST_PH_S4B-PH-K_1x04_P2.00mm_Horizontal",
                              210, y, tuple(str(i) for i in range(1, 5))))
        for pin, net in enumerate(input_nets, 1):
            pin_y = y - (4 - pin) * 2.54
            wires.append(wire(204.92, pin_y, 192, pin_y))
            labels.append(label(net, 192, pin_y, 180, "right"))

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
{LIB_1X12}
{LIB_1X4_INPUT}
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
  (text "J14/A: 1 COMMON+, 2 LEFT, 3 RIGHT, 4 BRAKE. J15/B: 1 COMMON+, 2 FLASH, 3 BACK-UP, 4 DRL." (at 110 172 0)
    (effects (font (size 1.27 1.27)))
    (uuid {uid()})
  )
  (text "Both JST-PH harnesses are wired pin-to-pin. Swapping A and B keeps COMMON+ on pin 1 but exchanges light functions." (at 110 179 0)
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

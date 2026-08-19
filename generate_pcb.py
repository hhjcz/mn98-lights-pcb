#!/usr/bin/env python3
"""Generate the compact passive MN98 light-distribution PCB."""

from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "pcb-svetla-mn98.kicad_pcb"
JST_LIB = "/usr/share/kicad/footprints/Connector_JST.pretty"
HDR_LIB = "/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty"


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def add_net(board, name):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    return net


def add_footprint(board, library, name, ref, value, x, y, rotation=0):
    footprint = pcbnew.FootprintLoad(library, name)
    if footprint is None:
        raise RuntimeError(f"Missing footprint: {library}/{name}")
    footprint.SetReference(ref)
    footprint.SetValue(value)
    footprint.SetPosition(mm(x, y))
    footprint.SetOrientationDegrees(rotation)
    board.Add(footprint)
    return footprint


def connect_pad(footprint, number, net):
    footprint.FindPadByNumber(str(number)).SetNet(net)


def add_track(board, net, points, width, layer=pcbnew.B_Cu):
    for start, end in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(mm(*start))
        track.SetEnd(mm(*end))
        track.SetWidth(pcbnew.FromMM(width))
        track.SetLayer(layer)
        track.SetNet(net)
        board.Add(track)


def add_text(board, text, x, y, size=1.0, layer=pcbnew.F_SilkS, rotation=0):
    label = pcbnew.PCB_TEXT(board)
    label.SetText(text)
    label.SetPosition(mm(x, y))
    label.SetTextSize(mm(size, size))
    label.SetTextThickness(pcbnew.FromMM(0.15))
    label.SetLayer(layer)
    label.SetTextAngleDegrees(rotation)
    board.Add(label)


def edge(board, x1, y1, x2, y2):
    line = pcbnew.PCB_SHAPE(board)
    line.SetShape(pcbnew.SHAPE_T_SEGMENT)
    line.SetStart(mm(x1, y1))
    line.SetEnd(mm(x2, y2))
    line.SetLayer(pcbnew.Edge_Cuts)
    line.SetWidth(pcbnew.FromMM(0.1))
    board.Add(line)


def pad_pos(footprint, pad):
    position = footprint.FindPadByNumber(str(pad)).GetPosition()
    return (pcbnew.ToMM(position.x), pcbnew.ToMM(position.y))


def main():
    board = pcbnew.BOARD()
    board.GetDesignSettings().SetCopperLayerCount(2)

    nets = {name: add_net(board, name) for name in (
        "COMMON+", "LEFT", "RIGHT", "BRAKE", "BACK-UP", "DRL", "FLASH",
        "MARKER", "REAR_RED", "RAMP",
    )}

    # All LED connectors use pad 1 for COMMON+. Confirm actual MN98 harness
    # polarity before plugging the board into the car.
    outputs = [
        ("J1", "L TURN FRONT", 3, 1.5, 1.5, 0, "LEFT"),
        ("J2", "R TURN FRONT", 3, 7.5, 1.5, 0, "RIGHT"),
        ("J3", "L TURN REAR", 3, 13.5, 1.5, 0, "LEFT"),
        ("J4", "R TURN REAR", 3, 19.5, 1.5, 0, "RIGHT"),
        ("J5", "SPARE FLASH", 3, 25.5, 1.5, 0, "FLASH"),
        ("J6", "HEADLIGHT L", 2, 1.5, 8.0, 270, "DRL"),
        ("J7", "MARKER L", 2, 1.5, 16.0, 270, "MARKER"),
        ("J8", "REAR RED L", 2, 1.5, 24.0, 270, "REAR_RED"),
        ("J9", "ROOF RAMP", 2, 1.5, 32.0, 270, "RAMP"),
        ("J10", "HEADLIGHT R", 2, 28.5, 8.0, 90, "DRL"),
        ("J11", "MARKER R", 2, 28.5, 16.0, 90, "MARKER"),
        ("J12", "REAR RED R", 2, 28.5, 24.0, 90, "REAR_RED"),
        ("J13", "SPARE DRL", 2, 28.5, 32.0, 90, "DRL"),
    ]
    led = {}
    for ref, value, _pins, x, y, rotation, signal in outputs:
        fp = add_footprint(
            board, JST_LIB, "JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal",
            ref, value, x, y, rotation,
        )
        connect_pad(fp, 1, nets["COMMON+"])
        connect_pad(fp, 2, nets[signal])
        led[ref] = fp

    input_fp = add_footprint(
        board, JST_LIB, "JST_PH_S8B-PH-K_1x08_P2.00mm_Horizontal",
        "J14", "P6DC INPUT", 27.0, 36.3, 180,
    )
    input_nets = ("COMMON+", "COMMON+", "LEFT", "RIGHT", "BRAKE", "FLASH", "BACK-UP", "DRL")
    for pin, net_name in enumerate(input_nets, 1):
        connect_pad(input_fp, pin, nets[net_name])

    # JP1 and JP3 use standard three-pin shunts: centre is the load output.
    jp1 = add_footprint(board, HDR_LIB, "PinHeader_1x03_P2.54mm_Horizontal",
                         "JP1", "MARKER: DRL / FLASH", 10.5, 18.0, 0)
    connect_pad(jp1, 1, nets["DRL"])
    connect_pad(jp1, 2, nets["MARKER"])
    connect_pad(jp1, 3, nets["FLASH"])
    jp3 = add_footprint(board, HDR_LIB, "PinHeader_1x03_P2.54mm_Horizontal",
                         "JP3", "RAMP: DRL / FLASH", 10.5, 25.0, 0)
    connect_pad(jp3, 1, nets["DRL"])
    connect_pad(jp3, 2, nets["RAMP"])
    connect_pad(jp3, 3, nets["FLASH"])

    # A single 2.54 mm shunt placed vertically selects one of three columns.
    jp2 = add_footprint(board, HDR_LIB, "PinHeader_2x03_P2.54mm_Vertical",
                         "JP2", "REAR: DRL / BRAKE / BACK-UP", 17.0, 21.0, 0)
    for pin in (1, 3, 5):
        connect_pad(jp2, pin, nets["REAR_RED"])
    connect_pad(jp2, 2, nets["DRL"])
    connect_pad(jp2, 4, nets["BRAKE"])
    connect_pad(jp2, 6, nets["BACK-UP"])

    # Common positive is deliberately routed on F.Cu with a 1.2 mm spine.
    common_pin_1 = pad_pos(input_fp, 1)
    common_pin_2 = pad_pos(input_fp, 2)
    common_points = [common_pin_1, (common_pin_1[0], 35.0), (15.0, 35.0), (15.0, 5.0)]
    add_track(board, nets["COMMON+"], common_points, 1.2, pcbnew.F_Cu)
    for fp in led.values():
        pos = pad_pos(fp, 1)
        add_track(board, nets["COMMON+"], [(15.0, pos[1]), pos], 0.8, pcbnew.F_Cu)
    add_track(board, nets["COMMON+"], [common_pin_2, (common_pin_2[0], 35.0), (15.0, 35.0)], 1.2, pcbnew.F_Cu)

    # Routed B.Cu signal trunks. Jumper-selected loads terminate at the centre pad.
    sources = {
        "LEFT": pad_pos(input_fp, 3), "RIGHT": pad_pos(input_fp, 4),
        "BRAKE": pad_pos(input_fp, 5), "FLASH": pad_pos(input_fp, 6),
        "BACK-UP": pad_pos(input_fp, 7), "DRL": pad_pos(input_fp, 8),
        "MARKER": pad_pos(jp1, 2), "REAR_RED": pad_pos(jp2, 1), "RAMP": pad_pos(jp3, 2),
    }
    lanes = {"LEFT": 7.0, "RIGHT": 9.0, "BRAKE": 17.0, "BACK-UP": 19.0,
             "DRL": 21.0, "FLASH": 23.0, "MARKER": 11.0, "REAR_RED": 13.0, "RAMP": 15.0}
    targets = {
        "LEFT": ("J1", "J3"), "RIGHT": ("J2", "J4"), "DRL": ("J6", "J10", "J13"),
        "FLASH": ("J5",), "MARKER": ("J7", "J11"), "REAR_RED": ("J8", "J12"),
        "RAMP": ("J9",),
    }
    for name, refs in targets.items():
        lane = lanes[name]
        source = sources[name]
        add_track(board, nets[name], [source, (lane, 33.0), (lane, 1.5)], 0.35)
        for ref in refs:
            target = pad_pos(led[ref], 2)
            add_track(board, nets[name], [(lane, target[1]), target], 0.35)

    # Bring selectable source nets to each jumper.
    for net_name, fp, pin in (("DRL", jp1, 1), ("FLASH", jp1, 3), ("DRL", jp3, 1),
                               ("FLASH", jp3, 3), ("DRL", jp2, 2), ("BRAKE", jp2, 4),
                               ("BACK-UP", jp2, 6)):
        target = pad_pos(fp, pin)
        lane = lanes[net_name]
        add_track(board, nets[net_name], [(lane, target[1]), target], 0.35)

    # BRAKE and BACK-UP are only jumper sources, so they need their own trunks.
    for name in ("BRAKE", "BACK-UP"):
        add_track(board, nets[name], [sources[name], (lanes[name], 33.0), (lanes[name], 21.0)], 0.35)

    # All three upper JP2 pins are the same REAR_RED jumper output.
    add_track(board, nets["REAR_RED"], [pad_pos(jp2, 1), pad_pos(jp2, 3), pad_pos(jp2, 5)], 0.35)

    for x1, y1, x2, y2 in ((0, 0, 30, 0), (30, 0, 30, 40), (30, 40, 0, 40), (0, 40, 0, 0)):
        edge(board, x1, y1, x2, y2)
    add_text(board, "MN98 LIGHT DISTRIBUTION", 15, 12.0, 1.1)
    add_text(board, "PIN 1 = COMMON+  VERIFY LED POLARITY", 15, 14.0, 0.75)
    add_text(board, "JP1: DRL-MARKER-FLASH", 15, 16.0, 0.75)
    add_text(board, "JP2: REAR RED SELECT", 15, 27.8, 0.75)
    add_text(board, "JP3: DRL-RAMP-FLASH", 15, 29.0, 0.75)
    add_text(board, "P6DC: 1/2 +, 3 L, 4 R, 5 B, 6 FLASH, 7 REV, 8 DRL", 15, 36.7, 0.65)

    pcbnew.SaveBoard(str(OUT), board)


if __name__ == "__main__":
    main()

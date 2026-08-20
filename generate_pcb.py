#!/usr/bin/env python3
"""Generate the first compact Dupont-header MN98 light-distribution PCB."""

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pcbnew


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "pcb-svetla-mn98.kicad_pcb"
JST_LIB = "/usr/share/kicad/footprints/Connector_JST.pretty"
HDR_LIB = "/usr/share/kicad/footprints/Connector_PinHeader_2.54mm.pretty"


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def schematic_path(reference):
    return f"/{uuid5(NAMESPACE_URL, f'mn98-dupont/schematic/{reference}')}"


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
    footprint.SetPath(pcbnew.KIID_PATH(schematic_path(ref)))
    footprint.SetPosition(mm(x, y))
    footprint.SetOrientationDegrees(rotation)
    board.Add(footprint)
    return footprint


def connect_pad(footprint, number, net):
    footprint.FindPadByNumber(str(number)).SetNet(net)


def pad_pos(footprint, number):
    position = footprint.FindPadByNumber(str(number)).GetPosition()
    return pcbnew.ToMM(position.x), pcbnew.ToMM(position.y)


def add_track(board, net, points, width, layer=pcbnew.B_Cu):
    for start, end in zip(points, points[1:]):
        if start == end:
            continue
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(mm(*start))
        track.SetEnd(mm(*end))
        track.SetWidth(pcbnew.FromMM(width))
        track.SetLayer(layer)
        track.SetNet(net)
        board.Add(track)


def add_text(board, text, x, y, size=0.9, layer=pcbnew.F_SilkS, rotation=0):
    label = pcbnew.PCB_TEXT(board)
    label.SetText(text)
    label.SetPosition(mm(x, y))
    label.SetTextSize(mm(size, size))
    label.SetTextThickness(pcbnew.FromMM(0.15))
    label.SetLayer(layer)
    label.SetTextAngleDegrees(rotation)
    board.Add(label)


def add_silk_box(board, x1, y1, x2, y2):
    for start, end in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)),
                       ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
        line = pcbnew.PCB_SHAPE(board)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetStart(mm(*start))
        line.SetEnd(mm(*end))
        line.SetLayer(pcbnew.F_SilkS)
        line.SetWidth(pcbnew.FromMM(0.15))
        board.Add(line)


def edge(board, x1, y1, x2, y2):
    line = pcbnew.PCB_SHAPE(board)
    line.SetShape(pcbnew.SHAPE_T_SEGMENT)
    line.SetStart(mm(x1, y1))
    line.SetEnd(mm(x2, y2))
    line.SetLayer(pcbnew.Edge_Cuts)
    line.SetWidth(pcbnew.FromMM(0.1))
    board.Add(line)


def main():
    board = pcbnew.BOARD()
    board.GetDesignSettings().SetCopperLayerCount(2)
    nets = {name: add_net(board, name) for name in (
        "COMMON+", "LEFT", "RIGHT", "BRAKE", "FLASH", "BACK-UP", "DRL",
        "MARKER", "RAMP", "SPARE",
    )}

    # J1 and J2 face left, J3 faces right, and J14 faces toward the board.
    # Pins are assigned to preserve the visible COMMON+ / channel pairs.
    j1 = add_footprint(board, HDR_LIB, "PinHeader_1x04_P2.54mm_Horizontal",
                       "J1", "TURN PAIRS", 3.0, 11.62, 180)
    j2 = add_footprint(board, HDR_LIB, "PinHeader_1x06_P2.54mm_Horizontal",
                       "J2", "MAIN LIGHTS", 3.0, 25.70, 180)
    j3 = add_footprint(board, HDR_LIB, "PinHeader_1x06_P2.54mm_Horizontal",
                       "J3", "AUX LIGHTS", 28.0, 5.30)
    for fp, net_names in (
        (j1, ("RIGHT", "COMMON+", "LEFT", "COMMON+")),
        (j2, ("BACK-UP", "COMMON+", "BRAKE", "COMMON+", "DRL", "COMMON+")),
        (j3, ("COMMON+", "MARKER", "COMMON+", "RAMP", "COMMON+", "SPARE")),
    ):
        for pin, net_name in enumerate(net_names, 1):
            connect_pad(fp, pin, nets[net_name])

    j14 = add_footprint(board, JST_LIB, "JST_XH_S8B-XH-A_1x08_P2.50mm_Horizontal",
                        "J14", "P6DC INPUT", 8.0, 30.0, 0)
    for pin, net_name in enumerate(("COMMON+", "COMMON+", "LEFT", "RIGHT", "BRAKE", "FLASH", "BACK-UP", "DRL"), 1):
        connect_pad(j14, pin, nets[net_name])

    jumpers = {}
    for ref, value, x, output in (
        ("JP1", "MARKER DRL/FLASH", 13.0, "MARKER"),
        ("JP2", "RAMP DRL/FLASH", 17.0, "RAMP"),
        ("JP3", "SPARE DRL/FLASH", 21.0, "SPARE"),
    ):
        fp = add_footprint(board, HDR_LIB, "PinHeader_1x03_P2.54mm_Vertical", ref, value, x, 16.0)
        for pin, net_name in enumerate(("DRL", output, "FLASH"), 1):
            connect_pad(fp, pin, nets[net_name])
        jumpers[ref] = fp

    # Front common-positive spine keeps the duplicated P6DC positive pins low impedance.
    p_common_1, p_common_2 = pad_pos(j14, 1), pad_pos(j14, 2)
    common_x = 17.0
    add_track(board, nets["COMMON+"], [p_common_1, (p_common_1[0], 27.0), (common_x, 27.0), (common_x, 3.0)], 1.0, pcbnew.F_Cu)
    add_track(board, nets["COMMON+"], [p_common_2, (p_common_2[0], 27.0), (common_x, 27.0)], 1.0, pcbnew.F_Cu)
    for fp, common_pins in ((j1, (2, 4)), (j2, (2, 4, 6)), (j3, (1, 3, 5))):
        for pin in common_pins:
            target = pad_pos(fp, pin)
            add_track(board, nets["COMMON+"], [(common_x, target[1]), target], 0.7, pcbnew.F_Cu)

    # The remaining channels are isolated back-copper lanes. Jumper centre pads
    # are their selected loads; a shunt provides the DRL or FLASH source.
    sources = {name: pad_pos(j14, pin) for name, pin in (
        ("LEFT", 3), ("RIGHT", 4), ("BRAKE", 5), ("FLASH", 6),
        ("BACK-UP", 7), ("DRL", 8),
    )}
    lanes = {
        "LEFT": 7.5, "RIGHT": 9.0, "DRL": 10.5, "BRAKE": 12.0,
        "FLASH": 22.0, "BACK-UP": 23.5, "MARKER": 25.0,
        "RAMP": 26.5, "SPARE": 28.0,
    }
    targets = {
        "LEFT": [(j1, 3)], "RIGHT": [(j1, 1)], "DRL": [(j2, 5)],
        "BRAKE": [(j2, 3)], "BACK-UP": [(j2, 1)],
        "MARKER": [(j3, 2), (jumpers["JP1"], 2)],
        "RAMP": [(j3, 4), (jumpers["JP2"], 2)],
        "SPARE": [(j3, 6), (jumpers["JP3"], 2)],
    }
    for net_name, source in sources.items():
        lane = lanes[net_name]
        add_track(board, nets[net_name], [source, (lane, 27.0), (lane, 3.0)], 0.4)
        for fp, pin in targets.get(net_name, []):
            target = pad_pos(fp, pin)
            add_track(board, nets[net_name], [(lane, target[1]), target], 0.4)
    for net_name, ref, header_pin in (
        ("MARKER", "JP1", 2), ("RAMP", "JP2", 4), ("SPARE", "JP3", 6),
    ):
        header_pad = pad_pos(j3, header_pin)
        jumper_pad = pad_pos(jumpers[ref], 2)
        lane = lanes[net_name]
        add_track(board, nets[net_name], [header_pad, (lane, header_pad[1]),
                                           (lane, jumper_pad[1]), jumper_pad], 0.4)
    for net_name, ref, pin in (
        ("DRL", "JP1", 1), ("FLASH", "JP1", 3),
        ("DRL", "JP2", 1), ("FLASH", "JP2", 3),
        ("DRL", "JP3", 1), ("FLASH", "JP3", 3),
    ):
        target = pad_pos(jumpers[ref], pin)
        add_track(board, nets[net_name], [(lanes[net_name], target[1]), target], 0.4)

    for segment in ((0, 0, 32, 0), (32, 0, 32, 42), (32, 42, 0, 42), (0, 42, 0, 0)):
        edge(board, *segment)

    # Boxes make each unkeyed Dupont pair and its COMMON+ pin obvious during assembly.
    add_silk_box(board, 0.4, 2.5, 6.3, 13.6)
    add_silk_box(board, 0.4, 11.5, 6.3, 26.8)
    add_silk_box(board, 24.7, 3.5, 31.3, 20.0)
    add_text(board, "TURN", 3.0, 1.5, 0.9)
    add_text(board, "+ LEFT   + RIGHT", 3.0, 14.0, 0.65)
    add_text(board, "MAIN", 3.0, 10.2, 0.9)
    add_text(board, "+ DRL   + BRAKE   + BACK-UP", 7.7, 19.5, 0.55, rotation=90)
    add_text(board, "AUX", 28.0, 1.5, 0.9)
    add_text(board, "+ MARK   + RAMP   + SPARE", 23.3, 11.5, 0.55, rotation=90)
    add_text(board, "MARK  RAMP  SPARE", 17.0, 12.4, 0.65)
    add_text(board, "JP: DRL / OUT / FLASH", 17.0, 19.7, 0.65)
    add_text(board, "J14 PIN 1", 8.0, 24.5, 0.65)
    add_text(board, "P6DC: 1/2 +, 3 L, 4 R, 5 B, 6 F, 7 REV, 8 DRL", 16.0, 40.5, 0.55)
    add_text(board, "VERIFY LED POLARITY", 17.0, 22.0, 0.75)

    pcbnew.SaveBoard(str(OUT), board)


if __name__ == "__main__":
    main()

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
    footprint.Reference().SetVisible(False)
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

    # Placement-only revision for mechanical review. All connector courtyards
    # are inside the outline; routing is intentionally deferred until approval.
    j1 = add_footprint(board, HDR_LIB, "PinHeader_1x04_P2.54mm_Horizontal",
                       "J1", "LEFT LIGHT PORTS", 11.05, 9.9, 180)
    j2 = add_footprint(board, HDR_LIB, "PinHeader_1x12_P2.54mm_Horizontal",
                       "J2", "RIGHT LIGHT PORTS", 20.95, 2.3)
    for fp, net_names in (
        (j1, ("DRL", "COMMON+", "LEFT", "COMMON+")),
        (j2, ("COMMON+", "RIGHT", "COMMON+", "BRAKE", "COMMON+",
              "BACK-UP", "COMMON+", "MARKER", "COMMON+", "RAMP",
              "COMMON+", "SPARE")),
    ):
        for pin, net_name in enumerate(net_names, 1):
            connect_pad(fp, pin, nets[net_name])

    j14a = add_footprint(board, JST_LIB, "JST_PH_S4B-PH-K_1x04_P2.00mm_Horizontal",
                         "J14", "BODY LINK A", 9.25, 15.0, 270)
    j14b = add_footprint(board, JST_LIB, "JST_PH_S4B-PH-K_1x04_P2.00mm_Horizontal",
                         "J15", "BODY LINK B", 9.25, 27.0, 270)
    for fp, net_names in (
        (j14a, ("COMMON+", "LEFT", "RIGHT", "BRAKE")),
        (j14b, ("COMMON+", "FLASH", "BACK-UP", "DRL")),
    ):
        for pin, net_name in enumerate(net_names, 1):
            connect_pad(fp, pin, nets[net_name])

    jumpers = {}
    for ref, value, x, output in (
        ("JP1", "MARKER DRL/FLASH", 2.3, "MARKER"),
        ("JP2", "RAMP DRL/FLASH", 13.2, "RAMP"),
        ("JP3", "SPARE DRL/FLASH", 24.1, "SPARE"),
    ):
        fp = add_footprint(board, HDR_LIB, "PinHeader_1x03_P2.54mm_Vertical", ref, value, 16.0, x)
        for pin, net_name in enumerate(("DRL", output, "FLASH"), 1):
            connect_pad(fp, pin, nets[net_name])
        jumpers[ref] = fp

    for segment in ((0, 0, 32, 0), (32, 0, 32, 36), (32, 36, 0, 36), (0, 36, 0, 0)):
        edge(board, *segment)

    # Light-port names and COMMON+ polarity are the primary assembly labels.
    add_text(board, "+LEFT", 13.35, 3.55, 0.6, rotation=90)
    add_text(board, "+DRL", 13.35, 8.63, 0.6, rotation=90)

    add_text(board, "+RIGHT", 18.65, 3.57, 0.6, rotation=90)
    add_text(board, "+BRAKE", 18.65, 8.65, 0.55, rotation=90)
    add_text(board, "+BACK-UP", 18.65, 13.73, 0.55, rotation=90)
    add_text(board, "+MARKER", 18.65, 18.81, 0.55, rotation=90)
    add_text(board, "+RAMP", 18.65, 23.89, 0.6, rotation=90)
    add_text(board, "+SPARE", 18.65, 28.97, 0.6, rotation=90)

    add_text(board, "A", 12.7, 15.0, 1.0)
    add_text(board, "B", 12.7, 27.0, 1.0)

    pcbnew.SaveBoard(str(OUT), board)


if __name__ == "__main__":
    main()

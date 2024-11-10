from migen import *

from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

# Core Board
_io = [
    # Clk / Rst.
    ("clk27",  0, Pins("H11"), IOStandard("LVCMOS33")),

    # Serial.
    ("serial", 0,
        Subsignal("rx", Pins("T13")), # CARD1:1
        Subsignal("tx", Pins("M11")), # CARD1:11
        IOStandard("LVCMOS33")
    ),

    # SPIFlash.
    ("spiflash", 0,
        Subsignal("cs_n", Pins("M9"),  IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("L10"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("P10"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("R10"), IOStandard("LVCMOS33")),
    ),

    # SDCard.
    ("spisdcard", 0,
        Subsignal("clk",  Pins("N10")),
        Subsignal("mosi", Pins("R14")),
        Subsignal("cs_n", Pins("N11")),
        Subsignal("miso", Pins("M8")),
        IOStandard("LVCMOS33"),
    ),
    ("sdcard", 0,
        Subsignal("data", Pins("M8 M7 M10 N11")),
        Subsignal("cmd",  Pins("R14")),
        Subsignal("clk",  Pins("N10")),
        Subsignal("cd",   Pins("D15")),
        IOStandard("LVCMOS33"),
    ),

    # DDR3 
    ("ddram", 0,
        Subsignal("a", Pins("F7 A4 D6 F8 C4 E6 B1 D8 A5 F9 K3 B7 A3 C8"),
            IOStandard("SSTL15")),
        Subsignal("ba", Pins("H4 D3 H5"), IOStandard("SSTL15")),
        Subsignal("ras_n", Pins("R4"), IOStandard("SSTL15")),
        Subsignal("cas_n", Pins("R6"), IOStandard("SSTL15")),
        Subsignal("we_n",  Pins("L2"), IOStandard("SSTL15")),
        Subsignal("cs_n",  Pins("P5"), IOStandard("SSTL15")),
        Subsignal("dm", Pins("G1 K5"), IOStandard("SSTL15")),
        Subsignal("dq", Pins(
            "G5 F5 F4 F3 E2 C1 E1 B3",
            "M3 K4 N2 L1 P4 H3 R1 M2"),
            IOStandard("SSTL15"),
            Misc("VREF=INTERNAL")),
        Subsignal("dqs_p", Pins("G2 J5"), IOStandard("SSTL15D")),
        Subsignal("dqs_n", Pins("G3 K6"), IOStandard("SSTL15D")),
        Subsignal("clk_p", Pins("J1"), IOStandard("SSTL15D")),
        Subsignal("clk_n", Pins("J3"), IOStandard("SSTL15D")),
        Subsignal("cke",   Pins("J2"), IOStandard("SSTL15")),
        Subsignal("odt",   Pins("R3"), IOStandard("SSTL15")),
        Subsignal("reset_n", Pins("B9"), IOStandard("SSTL15")),
    ),
]

_connectors = [
    ["CARD1",
        # A.
        # -------------------------------------------------
        "---", # 0
        #     GND GND  5V  5V  5V  5V GND GND  NC   ( 1-10).
        " T13 --- --- --- --- --- --- --- --- ---",
        #      NC GND GND      NC  NC  NC GND GND   (11-20).
        " M11 --- --- --- T10 --- --- --- --- ---",
        #  NC 3V3  NC 3V3 GND GND                   (21-30).
        " --- --- --- --- --- ---  T6 R16  P6 P15",
        # GND GND                 GND GND           (31-40).
        " --- ---  T7 P16  R8 N15 --- ---  T8  N16",
        #         GND                 GND GND       (41-50).
        "  M6 N14 --- L16  T9 L14  P9 --- --- K15",
        #             GND GND                 GND   (51-60).
        " P11 K14 T11 --- --- K16 R11 J15 T12 ---",
        # GND                 GND                   (61-70).
        " --- H16 R12 H14 P13 --- R13 G16 T14 H15",
        # GND GND                                   (71-72).
        " --- ---",
        # B.
        # -------------------------------------------------
        #                                      NC   (73-82).
        " M15 L13 M14 K11 F13 K12 G12 K13 T15 ---",
        #                  NC  NC                   (83-92).
        " J16 H13 J14 J12 --- --- G14 H12 G15 G11",
        #  NC  NC                  NC  NC      NC  (93-102).
        " --- --- F14 B10 F16 A13 --- --- E15 ---",
        #      NC  NC  NC      NC      NC  NC  NC  (103-112).
        " D15 --- --- --- A15 --- B14 --- --- ---",
        #      NC      NC  NC  NC      NC      NC  (113-122).
        " A14 --- B13 --- --- --- C12 --- B12 ---",
        #      NC      NC GND GND                  (123-132).
        " A12 --- C11 --- --- --- B11 E16 A11 F15",
        # GND GND          NC GND GND      NC      (133-142).
        " --- --- C10 C13 --- --- --- D16 --- E14",
        #     GND GND                 GND GND      (143-152).
        "  B8 --- ---  C9  C6  A9  A7 --- --- L12",
        #         GND GBD                 GND GND  (153-162).
        "  A6 J11 --- ---  C7  E9  D7  E8 --- ---",
        #     VCC     VCC GND GND     VCC     GND  (163-172).
        "  T2 ---  T3 --- --- ---  T4 ---  T5 ---",
        # GND VCC             GND GND              (173-182).
        " --- ---  N6 F10  N7 --- --- D11  N9 D10",
        #     GND GND      NC  NC GND GND          (183-192).
        "  R9 --- --- E10 --- --- --- ---  N8 R7",
        #         GND GND  NC      NC      NC  NC  (193-202).
        "  L9  P7 --- --- ---  M6 ---  L8 --- ---",
        #  NC  NC                                  (203-204).
        " --- ---",
    ],
]

_dock_lite_io = [
    # Buttons.
    ("btn_rst_n",   0, Pins("CARD1:15"),  IOStandard("LVCMOS15")),
    ("btn_n",   0, Pins("T3"), IOStandard("LVCMOS15")),

    # oled
    ("i2c0", 0,
        Subsignal("sda", Pins("A15")),
        Subsignal("scl", Pins("B14")),
        IOStandard("LVCMOS33"),
    ),

    ("ad9226_data",0, Pins("R9"),IOStandard("LVCMOS33")),
    ("ad9226_data",1, Pins("N9"),IOStandard("LVCMOS33")),
    ("ad9226_data",2, Pins("N7"),IOStandard("LVCMOS33")),
    ("ad9226_data",3, Pins("N6"),IOStandard("LVCMOS33")),
    ("ad9226_data",4, Pins("C10"),IOStandard("LVCMOS33")),
    ("ad9226_data",5, Pins("A11"),IOStandard("LVCMOS33")),
    ("ad9226_data",6, Pins("B11"),IOStandard("LVCMOS33")),
    ("ad9226_data",7, Pins("C11"),IOStandard("LVCMOS33")),
    ("ad9226_data",8, Pins("A12"),IOStandard("LVCMOS33")),
    ("ad9226_data",9, Pins("B12"),IOStandard("LVCMOS33")),
    ("ad9226_data",10, Pins("C12"),IOStandard("LVCMOS33")),
    ("ad9226_data",11, Pins("B13"),IOStandard("LVCMOS33")),
    ("ad9226_clk",0,Pins("A14"),IOStandard("LVCMOS33")),
]

class Platform(GowinPlatform):
    default_clk_name   = "clk27"
    default_clk_period = 1e9/27e6

    def __init__(self, toolchain="gowin"):

        GowinPlatform.__init__(self, "GW2A-LV18PG256C8/I7", _io, _connectors, toolchain=toolchain, devicename="GW2A-18C")
        self.add_extension(_dock_lite_io)

        self.toolchain.options["use_mspi_as_gpio"]  = 1
        self.toolchain.options["use_sspi_as_gpio"]  = 1
        self.toolchain.options["use_ready_as_gpio"] = 1
        self.toolchain.options["use_done_as_gpio"]  = 1
        self.toolchain.options["rw_check_on_ram"]   = 1

    def create_programmer(self, kit="openfpgaloader"):
        return OpenFPGALoader(cable="ft2232")

    def do_finalize(self, fragment):
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk27", loose=True), 1e9/27e6)


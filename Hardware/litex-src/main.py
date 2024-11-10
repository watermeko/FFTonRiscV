#!/usr/bin/env python3

from migen import *
from litex.soc.cores.timer import *
from migen.genlib.resetsync import AsyncResetSynchronizer
from litex.gen import *
from litex.soc.cores.clock.gowin_gw2a import GW2APLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.gpio import *
from litedram.modules import MT41K64M16
from litex.soc.cores.bitbang import I2CMaster
from litedram.phy import GW2DDRPHY
from myplatform import  Platform

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_dram=False):
        self.rst        = Signal()
        self.cd_sys     = ClockDomain()
        self.cd_por     = ClockDomain()
        if with_dram:
            self.cd_init    = ClockDomain()
            self.cd_sys2x   = ClockDomain()
            self.cd_sys2x_i = ClockDomain()

        self.stop  = Signal()
        self.reset = Signal()

        # clk
        clk27 = platform.request("clk27")
        rst_n  = platform.request("btn_rst_n")

        # reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk27)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # pll
        self.pll = pll = GW2APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done)
        self.comb += pll.reset.eq(~rst_n)
        pll.register_clkin(clk27, 27e6)

        if with_dram:
            # ddr clk
            pll.create_clkout(self.cd_sys2x_i, 2*sys_clk_freq)
            self.specials += [
                Instance("DHCEN",
                    i_CLKIN  = self.cd_sys2x_i.clk,
                    i_CE     = self.stop,
                    o_CLKOUT = self.cd_sys2x.clk),
                Instance("CLKDIV",
                    p_DIV_MODE = "2",
                    i_CALIB    = 0,
                    i_HCLKIN   = self.cd_sys2x.clk,
                    i_RESETN   = ~self.reset,
                    o_CLKOUT   = self.cd_sys.clk),
            ]
            
            # Init clock domain
            self.comb += self.cd_init.clk.eq(clk27)
            self.comb += self.cd_init.rst.eq(pll.reset)

        else:
            pll.create_clkout(self.cd_sys, sys_clk_freq)
        
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked | self.rst | self.reset)


class SOC(SoCCore):
        def __init__(self, sys_clk_freq=48e6,**kwargs):
            myplatform = Platform(toolchain="gowin")

            # crg
            with_dram = (kwargs.get("integrated_main_ram_size", 0) == 0)
            self.crg  = _CRG(myplatform, sys_clk_freq, with_dram=with_dram)

            # core
            SoCCore.__init__(self, myplatform, sys_clk_freq, ident="LiteX SoC on Tang Primer 20K", **kwargs)
            # ddr3
            if with_dram:
                self.ddrphy = GW2DDRPHY(
                    pads         =  myplatform.request("ddram"),
                    sys_clk_freq = sys_clk_freq
                )
                self.ddrphy.settings.rtt_nom = "disabled"
                self.comb += self.crg.stop.eq(self.ddrphy.init.stop)
                self.comb += self.crg.reset.eq(self.ddrphy.init.reset)
                self.add_sdram("sdram",
                    phy           = self.ddrphy,
                    module        = MT41K64M16(sys_clk_freq, "1:2"),
                    l2_cache_size = kwargs.get("l2_size", 8192) 
                )

            # flash
            from litespi.modules import W25Q32JV as SpiFlashModule
            from litespi.opcodes import SpiNorFlashOpCodes as Codes
            self.add_spi_flash(mode="1x", module=SpiFlashModule(Codes.READ_1_1_1))
            # buttons
            self.button = GPIOIn(pads=~myplatform.request("btn_n"),with_irq=True)
            # oled
            self.i2c0 = I2CMaster(pads = myplatform.request("i2c0"))
            # adc
            self.adc_data = GPIOIn(pads=myplatform.request_all("ad9226_data"))
            self.adc_clk = GPIOOut(pads=myplatform.request("ad9226_clk"))
            # timer
            self.timer1 = Timer()
            self.timer2 = Timer()

            self.irq.add("button",use_loc_if_exists=True)
            self.irq.add("timer1",  use_loc_if_exists=True)

def main():
        from litex.build.parser import LiteXArgumentParser
        parser = LiteXArgumentParser(platform=Platform, description="LiteX SoC on Tang Primer 20K.")
        parser.add_target_argument("--flash",  action="store_true")
        args = parser.parse_args()
        soc = SOC(with_pmod_led = True,with_buttons = True,**parser.soc_argdict)
        soc.add_spi_sdcard()

        builder = Builder(soc, **parser.builder_argdict)
        if args.build:
            builder.build(**parser.toolchain_argdict)

        if args.load:
            prog = soc.platform.create_programmer()
            prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

        if args.flash:
            prog = soc.platform.create_programmer()
            prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"), external=True)

if __name__ == "__main__":
    main()

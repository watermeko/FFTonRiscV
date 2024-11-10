package vexriscv

import spinal.core._
import spinal.core.internals.{ExpressionContainer, PhaseAllocateNames, PhaseContext}
import vexriscv.{VexRiscv, VexRiscvConfig, plugin}
import spinal.lib._
import vexriscv.ip.fpu.FpuParameter
import vexriscv.ip.{DataCacheConfig, InstructionCacheConfig}
import vexriscv.plugin._

import scala.collection.mutable.ArrayBuffer

object SpinalConfig extends spinal.core.SpinalConfig(
  defaultConfigForClockDomains = ClockDomainConfig(
    resetKind = spinal.core.SYNC
  )
){
  phasesInserters += {(array) => array.insert(array.indexWhere(_.isInstanceOf[PhaseAllocateNames]) + 1, new ForceRamBlockPhase)}
  phasesInserters += {(array) => array.insert(array.indexWhere(_.isInstanceOf[PhaseAllocateNames]) + 1, new NoRwCheckPhase)}
}

object FFTonRiscV{
  def main(args: Array[String]) {

    var fpuEnable = false
    var outputFile = "VexRiscv_FPU"

    args.sliding(2, 2).toList.collect {
      case Array("--fpuEnable", value) => fpuEnable = value.toBoolean
      case Array("--outputFile", value) => outputFile = value
    }

    SpinalConfig.copy(netlistFileName = outputFile + ".v").generateVerilog {
      val plugins = ArrayBuffer[Plugin[VexRiscv]]()

      plugins ++= List(
        new IBusCachedPlugin(
          resetVector = null, 
          relaxedPcCalculation = false,
          prediction = STATIC,
          compressedGen = false,
          config = InstructionCacheConfig(
            cacheSize = 4096,
            bytePerLine = 32,
            wayCount = 1,
            addressWidth = 32,
            cpuDataWidth = 32,
            memDataWidth = 32,
            catchIllegalAccess = true,
            catchAccessFault = true,
            asyncTagMemory = false,
            twoCycleRam = false,
            twoCycleCache = true
          )
        ),
        new DBusCachedPlugin(
          dBusCmdMasterPipe = true,
          dBusCmdSlavePipe = true,
          dBusRspSlavePipe = false,
          config = new DataCacheConfig(
            cacheSize = 4096,
            bytePerLine = 32,
            wayCount = 1,
            addressWidth = 32,
            cpuDataWidth = 32,
            memDataWidth = 32,
            catchAccessError = true,
            catchIllegal = true,
            catchUnaligned = true,
            withLrSc = false,
            withAmo = false,
            earlyWaysHits = true
          ),
          csrInfo = true
        ),
        new StaticMemoryTranslatorPlugin(
          ioRange = _.msb
        ),
        new DecoderSimplePlugin(
          catchIllegalInstruction = true
        ),
        new RegFilePlugin(
          regFileReadyKind = plugin.SYNC,
          zeroBoot = false
        ),
        new IntAluPlugin,
        new SrcPlugin(
          separatedAddSub = false,
          executeInsertion = true
        ),
        new FullBarrelShifterPlugin,
        new HazardSimplePlugin(
          bypassExecute = true,
          bypassMemory = true,
          bypassWriteBack = true,
          bypassWriteBackBuffer = true,
          pessimisticUseSrc = false,
          pessimisticWriteRegFile = false,
          pessimisticAddressMatch = false
        ),
        new BranchPlugin(
          earlyBranch = false,
          catchAddressMisaligned = true
        ),
        new CsrPlugin(
          CsrPluginConfig.small(mtvecInit = null).copy(mtvecAccess = CsrAccess.WRITE_ONLY, ecallGen = true, wfiGenAsNop = true)
        ),
        new YamlPlugin(outputFile.concat(".yaml"))
      )

      if(fpuEnable) {
        plugins += new FpuPlugin(
          externalFpu = false,
          simHalt = false,
          p = FpuParameter(withDouble = false)
        )
      }

      val cpuConfig = VexRiscvConfig(plugins.toList)
      val cpu = new VexRiscv(cpuConfig)

      cpu.rework {
        for (plugin <- cpuConfig.plugins) plugin match {
          case plugin: IBusCachedPlugin => {
            plugin.iBus.setAsDirectionLess()
            master(plugin.iBus.toWishbone()).setName("iBusWishbone")
          }
          case plugin: DBusCachedPlugin => {
            plugin.dBus.setAsDirectionLess()
            master(plugin.dBus.toWishbone()).setName("dBusWishbone")
          }
          case _ =>
        }
      }

      cpu
    }
  }
}

class ForceRamBlockPhase() extends spinal.core.internals.Phase{
  override def impl(pc: PhaseContext): Unit = {
    pc.walkBaseNodes{
      case mem: Mem[_] => {
        var asyncRead = false
        mem.dlcForeach[MemPortStatement]{
          case _ : MemReadAsync => asyncRead = true
          case _ =>
        }
        if(!asyncRead) mem.addAttribute("ram_style", "block")
      }
      case _ =>
    }
  }
  override def hasNetlistImpact: Boolean = false
}

class NoRwCheckPhase() extends spinal.core.internals.Phase{
  override def impl(pc: PhaseContext): Unit = {
    pc.walkBaseNodes{
      case mem: Mem[_] => {
        var doit = false
        mem.dlcForeach[MemPortStatement]{
          case _ : MemReadSync => doit = true
          case _ =>
        }
        mem.dlcForeach[MemPortStatement]{
          case p : MemReadSync if p.readUnderWrite != dontCare  => doit = false
          case _ =>
        }
        if(doit) mem.addAttribute("no_rw_check")
      }
      case _ =>
    }
  }
  override def hasNetlistImpact: Boolean = false
}


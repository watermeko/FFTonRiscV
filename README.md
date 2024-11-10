# 说明
本项目基于SpianlHDL和LiteX，基于VexRiscv构建具有浮点运算单元的CPU,通过LiteX构建外设并组成SOC。板子上电后从SD卡读取并运行程序，按键中断触发后，采集电压并进行快速傅里叶变换，再通过OLED显示出来。
## 项目结构
```
watermeko-litex
│
├── 📁Software // 存放算法的源文件
├── 📁Hardware
│   └── 📁fs    // 存放构建好的.fs文件
│   └── 📁litex-src // 用以构建soc的源文件
│   └── 📁spinal-src // 用以构建cpu的源文件
├── 📁Tools // 可能会使用到的工具
├── 📁Doc
├── 📄README
├── 📄requirements.txt
│
```

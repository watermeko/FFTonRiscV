# 说明
本项目基于SpianlHDL和LiteX，基于VexRiscv构建具有浮点运算单元的CPU,通过LiteX构建外设并组成SOC。板子上电后从SD卡读取并运行程序，按键触发后，采集电压并进行快速傅里叶变换，再通过OLED显示出来。
采用Sipeed Tang Premier 20K(Gowin GW2A FPGA)+自制扩展板。
移植了U8g2。

# 板子构成
![Board](https://github.com/watermeko/picx-images-hosting/raw/master/all/others/无标题-2024-11-11-0524.2a53vqbd52.svg)

# 文件结构
```
FFTonRiscV
│
├── 📁Software // 存放程序的源文件
├── 📁Hardware
│   └── 📁fs    // 存放构建好的.fs文件和程序.bin文件
│   └── 📁litex-src // 用以构建soc的源文件
│   └── 📁spinal-src // 用以构建cpu的源文件
├── 📁Doc // 存放原理图、文档等
├── 📄README
├── 📄requirements.txt
│
```

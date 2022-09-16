## Some usefull tool
1. Print directory
   + Run print_directory/print_directory.py we get following output
   ```
   print_directory/
   ├── .print_directory.py.swp
   ├── a/
   │   └── text.txt
   ├── b/
   └── print_directory.py
   ```
2. Setup bluetooh
   + cd /usr/lib/firmware/rtl_bt
   + sudo ln -s rtl8761b_fw.bin rtl8761bu_fw.bin
   + sudo dmesg (run this command first if error then run the command above)
   + auto connect: https://github.com/jrouleau/bluetooth-autoconnect

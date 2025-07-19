ssh pi@raspberrypi

.\ai_planing_code_docu.bat
.\git\SCIoT_G02_2025\ai_planing_code_docu.bat
.\room_unit_gateway_code_docu.bat
.\git\SCIoT_G02_2025\room_unit_gateway_code_docu.bat

C:\Anaconda\envs\SCIoT\python.exe
.\test_and_present_single_components.py True .\backend\aiplaning\config\ai_planer_test_example.ini False

./room_unit_gateway/main.py .\room_unit_gateway\configs_dir\manual_configs\config_virtual_manual.ini "test"
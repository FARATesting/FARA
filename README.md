# FARA
This repository contains the FARA testing framework, and our dataset (all apps used in our empirical study and evaluation). They are available in two separate folders: FARA tool and source code and dataset.

## Prerequisites
Before running FARA, ensure your system meets these requirements:

- Operating System: Ubuntu 18.04 or Windows 11

- Java Development Kit: JDK 1.8 (with JAVA_HOME environment variable configured)

- Android SDK: Android 9.0 (API 28) with ANDROID_HOME environment variable set

- Python: Version 3.7 or higher

- Android Device: Physical device or emulator (API 28) connected to your PC

- ADB Tools: Android Debug Bridge installed and configured

## Running FARA
Execute the testing framework in the following sequence:

### Step 1: Initialize State Transition Model

**cd "FARA tool and source code/StateTransitionModel"**
**java -cp . Main**

### Step 2: Execute Dynamic Analysis
cd "../DynamicAnalysis"
java -cp . DynamicTest dynamicAnalysis

### Step 3: Launch GUI Testing
cd ../..
python gui-testing.py

## Troubleshooting
If you encounter issues:

- Ensure all environment variables are properly configured

- Verify ADB connection to your Android device (adb devices)

- Check that required ports (5037 for ADB) are not blocked

- Confirm API level compatibility (API 28)

- Ensure Python 3.7+ is set as default Python interpreter
# dicom-rawdata-app
DICOM rawdata medical image app

<br />

## How to install

### For Linux and Mac user

Install [Docker for Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
or [Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/)

Run
```
docker pull chikinl/dicom-rawdata-app
```

### For Windows user

You can run this with WSL (Windows Subsystem for Linux).

[Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install)

Install Ubuntu 24.04 from the Microsoft Store

In the Ubuntu 24.04 WSL, install the [Docker for Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

Run
```
docker pull chikinl/dicom-rawdata-app
```

\

## How to run

Download the 4 shell scripts

### View LISTMODE header
```
./dicom_rawdata_listmode_readonly.sh [FILE_PATH]
```

### Export LISTMODE header to files
```
./dicom_rawdata_listmode.sh [FILE_PATH]
```

### View folder summary 
```
./dicom_rawdata_directory_readonly.sh [DIRECTORY_PATH]
```

### Export folder summary to file
```
./dicom_rawdata_directory.sh [DIRECTORY_PATH]
```


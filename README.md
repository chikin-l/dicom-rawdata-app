# dicom-rawdata
DICOM Raw data medical image utility


## How to install
This app is for Linux and Mac only.

Install Docker.

Run
```
docker pull chikinl/dicom-rawdata-app
```


## How to run

Download the 4 shell scripts

### View LISTMODE header
```
dicom_rawdata_listmode_readonly.sh [FILE_PATH]
```

### Export LISTMODE header to files
```
dicom_rawdata_listmode.sh [FILE_PATH]
```

### View folder summary 
```
dicom_rawdata_directory_readonly.sh [DIRECTORY_PATH]
```

### Export folder summary to file
```
dicom_rawdata_directory.sh [DIRECTORY_PATH]
```

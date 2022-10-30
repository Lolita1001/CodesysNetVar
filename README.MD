# CodesysNetVar
[![ru](https://img.shields.io/badge/lang-ru-green.svg)](https://github.com/Lolita1001/CodesysNetVar/blob/master/README.ru.MD)
## What is it ?

This is a small project that allows communication between a Codesys-based PLC and a PC.

The project is based on transferring data from the PLC to the PC via 
[Network Variables](https://help.codesys.com/api-content/2/codesys/3.5.13.0/en/_cds_f_networkvariables/) 
(Network Variable Lists / NVL).
This is a basic Codesys functionality that allows you to transfer data to another PLC (or with this project to a PC) 
with minimal effort using the UDP protocol.

The project allows you to generate variable objects based on Codesys configuration files and receive data from the PLC. 
In addition, it is possible to automatically generate a table in a PostgreSQL or Sqlite3 database and populate it 
as you receive data.

![structure](../assets/media/Nvl_S.jpg?raw=true)

## How to use it?

1. In the Codeys PLC programming environment, add NVL sender;

![Setup_1](../assets/media/Nvl_1.jpg?raw=true)

2. Set the IP address and port of the receiver. It is important to make sure that the handshake and 
delivery acknowledge bits are disabled. The PLC I had at hand did not change the sends because of these settings, 
but I admit that other vendors may change the sends or the behavior of the data transfer depending on these settings;

![Setup_2](../assets/media/Nvl_2.jpg?raw=true)

3. Declare variables in the NVL for transmission;

![Setup_3](../assets/media/Nvl_3.jpg?raw=true)

4. In the NVL settings choose to link to the file, this way the configuration file will be generated after confirmation.
The file contains declaration of variables, communication settings.

![Setup_4](../assets/media/Nvl_4.jpg?raw=true)

```configuration file```

    <GVL>
      <Declarations><![CDATA[VAR_GLOBAL
        sinus, cosine: REAL;
        some_word : WORD;
        integer : INT;
        my_time : TIME;
        my_date : DATE;
        my_string20 : STRING(20);
        my_array : ARRAY[0..4] OF INT;
    END_VAR]]></Declarations>
      <NetvarSettings Protocol="UDP">
        <ListIdentifier>1</ListIdentifier>
        <Pack>True</Pack>
        <Checksum>False</Checksum>
        <Acknowledge>False</Acknowledge>
        <CyclicTransmission>True</CyclicTransmission>
        <TransmissionOnChange>False</TransmissionOnChange>
        <TransmissionOnEvent>False</TransmissionOnEvent>
        <Interval>T#500ms</Interval>
        <MinGap>T#20ms</MinGap>
        <EventVariable>
        </EventVariable>
        <ProtocolSettings>
          <ProtocolSetting Name="Broadcast Adr." Value="192.168.56.35" />
          <ProtocolSetting Name="Port" Value="1202" />
        </ProtocolSettings>
      </NetvarSettings>
    </GVL>

5. Copy this file to ```CodesysNetVar/external```

6. The project is configured through environment variables or an ```.env``` file. 
The .env file must be located in ```CodesysNetVar/settings```. The database password must be in the form of 
file with no extension ```CNV_STORAGE___PASSWORD```, inside there should be only the password, no spaces, indents, etc. file 
must be in the folder ```CodesysNetVar/settings/secrets```.

```.env```
```
### Settings

## network
CNV_NETWORK___LOCAL_IP="192.168.56.35"
CNV_NETWORK___LOCAL_PORT="1202"

## storage
CNV_STORAGE___DB_TYPE="postgresql"  #or 'sqlite3'
CNV_STORAGE___IP_OR_PATH="127.0.0.1"  #or '/db.sqlite'
CNV_STORAGE___PORT="5432"
CNV_STORAGE___LOGIN="postgres"
CNV_STORAGE___DB_NAME="mydb"
CNV_STORAGE___TABLE_NAME_PREFIX="nvl"  #prefix for table in DB

##nvl_files
CNV_NVL___PATHS='["external/exp.gvl"]'

##logger
CNV_LOGGER___LEVEL_IN_STDOUT="INFO"  #or DEBUG, INFO, WARNING, ERROR or Comment this string for disable stdout
CNV_LOGGER___LEVEL_IN_FILE="INFO"  #or DEBUG, INFO, WARNING, ERROR or Comment this string for disable filelog
CNV_LOGGER___FILE_ROTATE="1 MB"  # see format in loguru
```

7. Install and Run 

install dependencies
```commandline
poetry install
```
Run
```commandline
poetry run python main.py
```

![Result in DB](../assets/media/Nvl_5.jpg?raw=true)

## Information

1. Codesys data type supported:
    
- Bool, Byte, Word, DWord, LWord;
- Int, DInt, LInt, UInt, UDInt, ULInt;
- Real, LReal;
- Time, TIME_OF_DAY, Date;
- String or Dimensional String(..);
- Array of supported data types;

2. Exchange with several PLCs at the same time is supported. This requires that the NVL IDs of the PLCs are 
unique. The generated NVL configuration files must be copied into ```CodesysNetVar/external``` and in
```.env``` the parameter ```CNV_NVL___PATHS='["external/exp1.gvl", "external/exp2.gvl"]'``` must list these files


## Roadmap

- [x] Support Arrays data type in **Unpack** mode
- Support more codesys data type
  - [x] TIME_OF_DAY 
  - [ ] DATE_AND_TIME
  - [ ] LTime
  - [x] String without dimensional
  - [ ] Structure
- [ ] Bulk write to DB
- [ ] other

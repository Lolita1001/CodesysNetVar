#CodesysNetVar
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

``configuration file``

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

``.env``
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

---
## Что это ?

Это небольшой проект позволяющий выполнять коммуникацию между ПЛК базирующем на Codesys и ПК.

Проект основан на передаче данных от ПЛК в ПК через Network Variables (Network Variable Lists / NVL).
Это базовый функционал Codesys позволяющий с минимальными усилиями передать данные в другой ПЛК 
(или с помощью этого проекта в ПК) используя UDP протокол.

Проект позволяет на основе конфигурационных файлов Codesys файлов сформировать объекты переменных и принимать данные 
от ПЛК. Дополнительно, имеется возможность автоматически генерировать таблицу в базе данных PostgreSQL или Sqlite3 и 
заполнять ее по ходу получения данных.

![structure](../assets/media/Nvl_S.jpg?raw=true)

## Как этим пользоваться?

1. В среде программирования ПЛК Codeys, добавить NVL sender.

![Setup_1](../assets/media/Nvl_1.jpg?raw=true)

2. Задать IP адрес и порт получателя. Важно, убедится, что биты квитирования и подтверждения доставки должны 
быть отключены. Тут ПЛК который был у меня под рукой, не меняли посылки из за этих настроек, но я допускаю, 
что другие вендоры могут изменять посылки или поведения передачи данных в зависимости от этих настроек;

![Setup_2](../assets/media/Nvl_2.jpg?raw=true)

3. Объявить переменные в NVL для передачи;

![Setup_3](../assets/media/Nvl_3.jpg?raw=true)

4. В настройках NVL выбрать связь с файлом, таким образом после подтверждения будет сгенерирован файл с конфигурацией. 
Файл содержит объявление переменных, настройки коммуникаций.

![Setup_4](../assets/media/Nvl_4.jpg?raw=true)

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

5. Этот файл нужно скопировать в ``CodesysNetVar/external``

6. Настройка проекта выполняется через переменные окружения или файл .env. 
Файл .env должен находится в ``CodesysNetVar/settings``. Пароль от базы данных должен быть в виде 
файла без расширения ``CNV_STORAGE___PASSWORD``, внутри должен быть только пароль, без пробелов, отступов и т.д. файл 
должен быть в папке ``CodesysNetVar/settings/secrets``


``.env``
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

7. Установка и запуск

Установка зависимостей
```commandline
poetry install
```
Запуск
```commandline
poetry run python main.py
```

![Result in DB](../assets/media/Nvl_5.jpg?raw=true)

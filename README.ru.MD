# CodesysNetVar
[![eng](https://img.shields.io/badge/lang-eng-green.svg)](https://github.com/Lolita1001/CodesysNetVar/blob/master/README.MD)

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

5. Этот файл нужно скопировать в ```CodesysNetVar/external```

6. Настройка проекта выполняется через переменные окружения или файл .env. 
Файл .env должен находится в ```CodesysNetVar/settings```. Пароль от базы данных должен быть в виде 
файла без расширения ```CNV_STORAGE___PASSWORD```, внутри должен быть только пароль, без пробелов, отступов и т.д. файл 
должен быть в папке ```CodesysNetVar/settings/secrets```


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

## Инфо

1. Поддерживаемые типы данных Codesys:
    
- Bool, Byte, Word, DWord, LWord;
- Int, DInt, LInt, UInt, UDInt, ULInt;
- Real, LReal;
- Time, Time of day, Date, Date and time;
- String или String(..) с указанным размером;
- Array of supported data types;

2. Поддерживается обмен с несколькими ПЛК одновременно. Для этого необходимо, что бы ID NVL у ПЛК были уникальны. 
Сгенерированные конфигурационные файлы NVL нужно скопировать в ```CodesysNetVar/external``` и в ```.env``` параметр 
```CNV_NVL___PATHS='["external/exp.gvl"]'``` должен содержать список из этих файлов


## Планы

- [x] Поддержка типа данных массив в **Unpack** режиме
- Поддержка больше типо данных Codesys
  - [x] TIME_OF_DAY
  - [x] DATE_AND_TIME
  - [ ] LTime
  - [x] String без указания размера
  - [ ] ~~Structure~~
- [ ] Запись в БД по несколько
- [ ] остальное...

#include "FedmIscCore.h"
#include <iostream>
using namespace std;

extern "C"
{
    __declspec(dllexport) FEDM_ISCReaderModule * new_reader()
    {
        return new FEDM_ISCReaderModule();
    }


    __declspec(dllexport) int connect_reader(FEDM_ISCReaderModule * reader, unsigned char bus_addr, int port_number)
    {
        // установка шины адреса
        reader->SetBusAddress(bus_addr);
        // установка размера таблицы (до 100 меток во время инвентаризации в Host-Mode)
        reader->SetTableSize(FEDM_ISC_ISO_TABLE, 100);
        // поддержка TagHandler
        reader->EnableTagHandler(true);
        // получить информацию о типе ридера
        reader->ReadReaderInfo();
        // подключиться к COM-порту
        int rCode = reader->ConnectCOMM(port_number);

        if (rCode == 0)
        {
            // определение скорости передачи данных
            rCode = reader->FindBaudRate();

            if (rCode == 0)
            {
                reader->SetPortPara("Timeout", "5000");  // 5s timeout
                return 0;
            }
            else {return rCode;}
        }
        else {return rCode;}
    }
        

    __declspec(dllexport) void disconnect_reader(FEDM_ISCReaderModule * reader)
    {
        reader->DisConnect();
    }


    /*
    Функция ищет транспондеры в зоне действия антенны и получает информацию о них
    Принимает:
        snr_array - ссылка на массив, в который запишутся идентификаторы транспондеров
    */
     __declspec(dllexport) int inventory(FEDM_ISCReaderModule * reader, unsigned char ** snr_array)
    {
        unsigned char transType = 0;
        CString sNR;

        // установка параметров для следующего протокола 
        // команда инвентаризации
        reader->SetData(FEDM_ISC_TMP_B0_CMD, (unsigned char)0x01);
        // очистка флагов
        reader->SetData(FEDM_ISC_TMP_B0_MODE, (unsigned char)0x00);
        // освобождение места для следующего инвентаря
        reader->ResetTable(FEDM_ISC_ISO_TABLE);
        // отправка протокола инвентаризации
        int rCode = reader->SendProtocol(0xB0);

        if(rCode == 0)
        {
            // заполнение таблицы данными о транспондерах
            for (int idx=0; idx < reader->GetTableLength(FEDM_ISC_ISO_TABLE); idx++)
            {
                std::cout << "position: " << idx << endl;
                // получение типа транспондера
                reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_TRTYPE, &transType);
                // получение строки с идентификатором транспондера
                reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR, sNR);
                // запись идентификатора транспондера в массив
                for (int i = 0; sNR[i] != '\0'; i++)
                {
                    snr_array[idx][i] = (unsigned char)sNR[i];
                }                    
            }
        }

        return rCode;
    }


    /*
    Функция выполняет считывание данных с одного транспондера
    Принимает:
        serialNumber - идентификатор транспондера            
        readData - массив, в который будут записаны считанные данные
        first_block - блок, с которого начинается считывание
        amount - количество блоков, которые нужно считать
    */
     __declspec(dllexport) int read_tag(FEDM_ISCReaderModule * reader, char const * serialNumber, unsigned char * readData)
    {
        int rCode = FEDM_OK; // код ошибок ридера
        int deviceID = 0; // серийный номер ридера; можно подать 0, тогда компонент подключится к первому обнаруженному ридеру
        int address = 0; // номер блока, с которого начинаем запись
        int blockCnt = 56; // число блоков для записи
        unsigned int blockSize = 4; // размер блока, отдается при чтении
        FedmIscTagHandler* tagHandler = NULL;   // объект метки

        reader->ConnectUSB(deviceID);

        if (reader->IsConnected())
        {
            reader->ReadReaderInfo();

            // зачитываем полную конфигурацию
            rCode = reader->ReadCompleteConfiguration(true);
            std::cout << "back1: " << rCode << endl;

            // переключаем ридер в HostMode (0)
            rCode = reader->SetConfigPara(ReaderConfig::OperatingMode::Mode, 0, true);
            std::cout << "back2: " << rCode << endl;

            rCode = reader->ApplyConfiguration(true);
            std::cout << "back3: " << rCode << endl;

            // перед работой с тегами необходимо задать размер таблицы
            rCode = reader->SetTableSize(FEDM_ISC_ISO_TABLE, 100);
            std::cout << "back4: " << rCode << endl;
                        
            tagHandler = reader->GetTagHandler(serialNumber);
            std::cout << "tagHandler: " << tagHandler << endl;

            if (tagHandler != NULL)
            {
                if(dynamic_cast<FedmIscTagHandler_ISO15693*>(tagHandler) != NULL)
                {
                    // задаем временную переменную для работы с меткой
                    FedmIscTagHandler_ISO15693* hfTag = (FedmIscTagHandler_ISO15693*)tagHandler;
                    std::cout << "hfTag: " << hfTag << endl;

                    //чтение
                    rCode = hfTag->ReadMultipleBlocks(address, blockCnt, blockSize, readData);
                }
            }
            else 
            {
                rCode = FEDM_ERROR_TAG_HANDLER_NOT_IDENTIFIED;
            }
        }
        else 
        {
            rCode = FEDM_ERROR_NOT_CONNECTED;
        }

        return rCode;
    }


    /*
    Функция выполняет запись данных на один транспондер
    Принимает:
        serialNumber - идентификатор транспондера          
        writeData - массив данных, которые будут записаны
        first_block - блок, с которого начинается считывание
    */
     __declspec(dllexport) int write_tag(FEDM_ISCReaderModule * reader, char const * serialNumber,  unsigned char * writeData)    
    {
        int rCode = FEDM_OK; // код ошибок ридера
        int deviceID = 0; // серийный номер ридера; можно подать 0, тогда компонент подключится к первому обнаруженному ридеру
        int address = 0; // номер блока, с которого начинаем запись
        int blockCnt = 56; // число блоков для записи
        unsigned int blockSize = 4; // размер блока, отдается при чтении
        FedmIscTagHandler* tagHandler = NULL;   // объект метки

        reader->ConnectUSB(deviceID);

        if (reader->IsConnected())
        {
            reader->ReadReaderInfo();

            //зачитываем полную конфигурацию
            rCode = reader->ReadCompleteConfiguration(true);
            std::cout << "back1: " << rCode << endl;

            // переключаем ридер в HostMode (0)
            rCode = reader->SetConfigPara(ReaderConfig::OperatingMode::Mode, 0, true);
            std::cout << "back2: " << rCode << endl;

            rCode = reader->ApplyConfiguration(true);
            std::cout << "back3: " << rCode << endl;

            //перед работой с тегами необходимо задать размер таблицы
            rCode = reader->SetTableSize(FEDM_ISC_ISO_TABLE, 100);
            std::cout << "back4: " << rCode << endl;
                        
            tagHandler = reader->GetTagHandler(serialNumber);
            std::cout << "tagHandler: " << tagHandler << endl;

            if (tagHandler != NULL)
            {
                if(dynamic_cast<FedmIscTagHandler_ISO15693*>(tagHandler) != NULL)
                {
                    // задаем временную переменную для работы с меткой
                    FedmIscTagHandler_ISO15693* hfTag = (FedmIscTagHandler_ISO15693*)tagHandler;
                    std::cout << "hfTag: " << hfTag << endl;
                        
                    //запись
                    rCode = hfTag->WriteMultipleBlocks(address, blockCnt, blockSize, writeData);
                }
            }
            else 
            {
                rCode = FEDM_ERROR_TAG_HANDLER_NOT_IDENTIFIED;
            }
        }
        else 
        {
            rCode = FEDM_ERROR_NOT_CONNECTED;
        }

        return rCode;
    }

    
    __declspec(dllexport) char * get_error_text(FEDM_ISCReaderModule * reader, int rCode)
    {
        return reader->GetErrorText(rCode);
    }
}
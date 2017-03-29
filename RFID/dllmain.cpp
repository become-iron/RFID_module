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
        int r_code = reader->ConnectCOMM(port_number);

        if (r_code == 0)
        {
            // определение скорости передачи данных
            r_code = reader->FindBaudRate();

            if (r_code == 0)
            {
                reader->SetPortPara("Timeout", "5000");  // 5s timeout
                return 0;
            }
            else {return r_code;}
        }
        else {return r_code;}
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
        unsigned char trans_type = 0;
        CString sNR;

        // установка параметров для следующего протокола 
        // команда инвентаризации
        reader->SetData(FEDM_ISC_TMP_B0_CMD, (unsigned char)0x01);
        // очистка флагов
        reader->SetData(FEDM_ISC_TMP_B0_MODE, (unsigned char)0x00);
        // освобождение места для следующего инвентаря
        reader->ResetTable(FEDM_ISC_ISO_TABLE);
        // отправка протокола инвентаризации
        int r_code = reader->SendProtocol(0xB0);

        if(r_code == 0)
        {
            // заполнение таблицы данными о транспондерах
            for (int idx=0; idx < reader->GetTableLength(FEDM_ISC_ISO_TABLE); idx++)
            {
                cout << "position: " << idx << endl;
                // получение типа транспондера
                reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_TRTYPE, &trans_type);
                // получение строки с идентификатором транспондера
                reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR, sNR); // TODO: Выяснить, какой тип должен быть у serial_number: char или unsigned char
                // запись идентификатора транспондера в массив
                cout << "CString sNR: " << sNR << endl;
                for (int i = 0; sNR[i] != '\0'; i++)
                {
                    snr_array[idx][i] = (unsigned char)sNR[i];
                }
                cout << "char sNR: " << endl;
//                for (int i = 0; i < 255; i++)
//                {
//                    cout << snr_array[idx][i];
//                }
//                cout << endl;

                    
            }
        }

        return r_code;
    }


    /*
    Функция выполняет считывание данных с одного транспондера
    Принимает:
        serial_number - идентификатор транспондера            
        read_data - массив, в который будут записаны считанные данные
        first_block - блок, с которого начинается считывание
        amount - количество блоков, которые нужно считать
    */
      // TODO (nb): для serial_number, наверное, просто char const *
     __declspec(dllexport) int read_tag(FEDM_ISCReaderModule * reader, char * serial_number, unsigned char * read_data)
    {
        /*
        // ПОПРОБОВАТЬ ПАРУ ДРУГИХ ВАРИАНТОВ
        UINT first_block = 5;
        unsigned char amount = 4;
        int r_code = 0; // код ошибок ридера
        int idx = 0;    // идентификатор блока        
        int item = 1;    // идентификатор блока  ПОПРОБОВАТЬ РАЗНЫЕ ЗНАЧЕНИЯ
        unsigned int block_size = 0;   // размер одного блока данных в байтах
        int data_len = 4;        
	    unsigned int ucDataSets;
        UCHAR ucSecStatus = 0;
        UINT ucSnrLen = 0;
        string data_string;
        int block_len = 4;
        unsigned int ucTagType = 0;

        UCHAR ucReadBlock[256]; // тестовый массив под данные
        
        // определения типа метки; для ISO15693 должен быть 3
        idx = reader->GetTableData(item, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_TRTYPE, &ucTagType);
        cout << "CPP. ucTagType: " << ucTagType << endl;
        cout << "CPP. idx: " << idx << endl;

        // поиск данных о транспондере в таблице по идентификатору

        // попробовать два варианта поиска данных о транспондере
        // 1
        //idx = reader->FindTableIndex(item, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR, serial_number); 
        
        // 2
        idx = reader->GetTableData(item, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR, serial_number, 32);        
        cout << "CPP. serial_number: " << serial_number << endl;
        cout << "CPP. idx: " << idx << endl;

        idx = reader->GetTableData(item, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR_LEN, &ucSnrLen);
        cout << "CPP. ucSnrLen: " << ucSnrLen << endl;
        cout << "CPP. idx: " << idx << endl;


        // установка параметров для следующего протокола
        // команда считывания данных
        reader->SetData(FEDM_ISC_TMP_B0_CMD, (UCHAR)0x23);
        // режим адресации
        reader->SetData(FEDM_ISC_TMP_B0_MODE, (UCHAR)0x00);
        reader->SetData(FEDM_ISC_TMP_B0_MODE_ADR, (UCHAR)0x01);   // FEDM_ISC_ISO_MODE_ADR = 0x01


        // ПРОТЕСТИРОВАТЬ НУЖНО ЛИ ЭТО
		reader->SetData(FEDM_ISC_TMP_B0_MODE_SEC, (UCHAR)0x01);

        // выбор транспондера по идентификатору
        reader->SetData(FEDM_ISC_TMP_B0_REQ_UID, serial_number, 8);
        // определение места считывания
        // ВЫБРАТЬ ПРАВИЛЬНЫЙ ВАРИАНТ
        // 1
        //reader->SetData(FEDM_ISC_TMP_B0_REQ_DB_ADR, first_block);
        // 2
        reader->SetData(FEDM_ISC_TMP_B0_REQ_DB_ADR, (UCHAR)first_block);

        // определение количества данных для считывания
        reader->SetData(FEDM_ISC_TMP_B0_REQ_DBN, amount);
        

        if(idx >= 0)
        {
        

        // отправка протокола считывания блоков
        r_code = reader->SendProtocol(0xB0);
        
            cout << "r_code: " << r_code << endl;
            // получение размера блока

            int ireturn2 = reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_BLOCK_SIZE, &block_size);
	        int ireturn3 = reader->GetData(FEDM_ISC_TMP_B0_RSP_DBN, &ucDataSets);
            cout << "block size: " << block_size << endl;
            cout << "ireturn2: " << ireturn2 << endl;
            cout << "ucDataSets: " << ucDataSets << endl;
            cout << "ireturn3: " << ireturn3 << endl;

            // получение самих данных
            //reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_RxDB, first_block, read_data, 256);

            // ПОПРОБОВАТЬ БЕЗ ЦИКЛА
            for(int i=0; i<ucDataSets; i++ )
	        {
                //ВЫБРАТЬ ПРАВИЛЬНЫЙ ВАРИАНТ
                // 1                
                reader->GetTableData(item, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_RxDB, i + first_block, ucReadBlock, block_size);
                cout << "ucReadBlock: " << ucReadBlock << endl;
                for (int j = 0; ucReadBlock[j] != '\0'; j++)                
                    cout << ucReadBlock[j];                
                cout << endl;
		        
                // 2
                reader->GetTableData(item, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_RxDB, i + (UCHAR)first_block, ucReadBlock, block_size);	
                cout << "ucReadBlock: " << ucReadBlock << endl;
                for (int j = 0; ucReadBlock[j] != '\0'; j++)              
                    cout << ucReadBlock[j];                
                cout << endl;

                // 3
                reader->GetTableData(item, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_RxDB, i+(UCHAR)first_block, read_data, block_size);	
                cout << "read_data: " << read_data << endl;
                for (int j = 0; read_data[j] != '\0'; j++)             
                    cout << read_data[j];                
                cout << endl;
		        
                // 4
                reader->GetTableData(item, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_RxDB, i+first_block, data_string);	
                cout << "data_string: " << data_string << endl;


		        reader->GetTableData(item, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SEC_STATUS, i, &ucSecStatus, 1);	
		
	        }	

        }
        */

        int r_code = 0; // код ошибок ридера
        int back = 0;
        int deviceID = 0; // серийный номер ридера; можно подать 0, тогда компонент подключится к первому обнаруженному ридеру
        int address = 0; // номер блока, с которого начинаем запись
        int BlockCnt = 55; // число блоков для записи
        unsigned int bsize = 4; // размер блока, отдается при чтении
        unsigned char newData[16]; // данные для записи

        FedmIscTagHandler* tagHandler = NULL;   // метка
        FEDM_ISC_TAG_LIST* tagList = NULL;      // список меток
        FEDM_ISC_TAG_LIST_ITOR itor;            // итератор меток

        reader->ConnectUSB(deviceID);

        if (reader->IsConnected())
        {
            //первым действием обязательно следует вызов ReadReaderInfo
            reader->ReadReaderInfo();

            //зачитываем полную конфигурацию
            back = reader->ReadCompleteConfiguration(true);
            cout << "back1: " << back << endl;

            // переключаем ридер в HostMode (0)
            // поскольку компонент подразумевает работу только в HostMode
            back = reader->SetConfigPara(ReaderConfig::OperatingMode::Mode, 0, true);
            cout << "back2: " << back << endl;

            back = reader->ApplyConfiguration(true);
            cout << "back3: " << back << endl;

            //перед работой с тегами необходимо задать размер таблицы
            back = reader->SetTableSize(FEDM_ISC_ISO_TABLE, 100);
            cout << "back4: " << back << endl;

            tagList = reader->TagInventory();
            cout << "tagList: " << tagList << endl;

            for(itor = tagList->begin(); itor != tagList->end(); itor++)
            {
                // проверяем валидность тега
                tagHandler = itor->second;
                cout << "tagHandler: " << tagHandler << endl;
                if (tagHandler != NULL)
                {
                    if(dynamic_cast<FedmIscTagHandler_ISO15693*>(tagHandler) != NULL)
                    {
                        // задаем временную переменную для работы с меткой
                        FedmIscTagHandler_ISO15693* hf_tag = (FedmIscTagHandler_ISO15693*)tagHandler;
                        cout << "hf_tag: " << hf_tag << endl;

                        string uid = hf_tag->GetUID();
                        cout << "uid: " << uid << endl;

                        byte data[256];

                        //чтение
                        r_code = hf_tag->ReadMultipleBlocks(address, BlockCnt, bsize, data);
                        cout << "r_code: " << r_code << endl;

                        //запись
                        //r_code = hf_tag->WriteMultipleBlocks(address, BlockCnt, bsize, newData);

                        cout << "data: " << data << endl;
                        for (int j = 0; j < 256; j++)             
                            cout << data[j];                
                        cout << endl;
                    }
                }
            }
        }

        return r_code;
    }


    /*
    Функция выполняет запись данных на один транспондер
    Принимает:
        serial_number - идентификатор транспондера          
        write_data - массив данных, которые будут записаны
        first_block - блок, с которого начинается считывание
    */
     __declspec(dllexport) int write_tag(FEDM_ISCReaderModule * reader, char * serial_number,  unsigned char * write_data)    
    {
        /*
        unsigned char first_block = 0;
        int ireturn = 0;
        int r_code = 0; // код ошибок ридера
        int idx = 0;    // идентификатор блока
        int item = 1;    // идентификатор блока  ПОПРОБОВАТЬ РАЗНЫЕ ЗНАЧЕНИЯ
        unsigned char block_size = 0;   // размер одного блока данных в байтах
        unsigned char data[256]; // буфер для 4 блоков данных по 4 байта
        int data_len = 4;
        int block_len = 4;

        // поиск данных о транспондере в таблице по идентификатору
        //idx = reader->FindTableIndex(0, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR, serial_number);
        idx = reader->GetTableData(item, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR, serial_number, 32);
        cout << "idx: " << idx << endl;
        //if(idx >= 0)
        //{
            // получение размера блока
            reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_BLOCK_SIZE, &block_size);
            
            // проверить, какой вариант получения данных рабочий
            // 1
            // получение данных из таблицы
            cout << "ireturn: " << endl;
            for(int i=0; i<data_len; i++)
            {
                ireturn = reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_RxDB, first_block, &data[i*block_size], block_len);
                cout << ireturn << endl;
            }

            // 2
            //reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_RxDB, first_block, data, block_len);
            
            cout << "data: " << endl;
            for (int i = 0; i <= 255; i++)                
                cout << data[i];                
            cout << endl;


            // печать передаваемых данных
            cout << "write_data: " << endl;
            for (int i = 0; write_data[i] != '\0'; i++)                
                cout << write_data[i];                
            cout << endl;
                

            // проверить, какой вариант записи рабочий
            // 1
            // сборка данных для протокола отправки
            cout << "ireturn: " << endl;
            for(int i=0; i<data_len; i++)
            {
                ireturn = reader->SetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_TxDB, first_block, &write_data[i*block_size], block_size);
                cout << ireturn << endl;
            }

            // 2
            //reader->SetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_TxDB, first_block, write_data, block_size);
                
            // отправка протокола записи блоков
            reader->SetData(FEDM_ISC_TMP_B0_CMD, (unsigned char)0x24);
            r_code = reader->SendProtocol(0xB0);

            cout << r_code << endl;
        //}

        return r_code;
        */

        int r_code = 0; // код ошибок ридера
        int back = 0;
        int deviceID = 0; // серийный номер ридера; можно подать 0, тогда компонент подключится к первому обнаруженному ридеру
        int address = 0; // номер блока, с которого начинаем запись
        int BlockCnt = 55; // число блоков для записи
        unsigned int bsize = 4; // размер блока, отдается при чтении

        FedmIscTagHandler* tagHandler = NULL;   // метка
        FEDM_ISC_TAG_LIST* tagList = NULL;      // список меток
        FEDM_ISC_TAG_LIST_ITOR itor;            // итератор меток

        reader->ConnectUSB(deviceID);

        if (reader->IsConnected())
        {
            //первым действием обязательно следует вызов ReadReaderInfo
            reader->ReadReaderInfo();

            //зачитываем полную конфигурацию
            back = reader->ReadCompleteConfiguration(true);
            cout << "back1: " << back << endl;

            // переключаем ридер в HostMode (0)
            // поскольку компонент подразумевает работу только в HostMode
            back = reader->SetConfigPara(ReaderConfig::OperatingMode::Mode, 0, true);
            cout << "back2: " << back << endl;

            back = reader->ApplyConfiguration(true);
            cout << "back3: " << back << endl;

            //перед работой с тегами необходимо задать размер таблицы
            back = reader->SetTableSize(FEDM_ISC_ISO_TABLE, 100);
            cout << "back4: " << back << endl;

            tagList = reader->TagInventory();
            cout << "tagList: " << tagList << endl;

            for(itor = tagList->begin(); itor != tagList->end(); itor++)
            {
                // проверяем валидность тега
                tagHandler = itor->second;
                cout << "tagHandler: " << tagHandler << endl;
                if (tagHandler != NULL)
                {
                    if(dynamic_cast<FedmIscTagHandler_ISO15693*>(tagHandler) != NULL)
                    {
                        // задаем временную переменную для работы с меткой
                        FedmIscTagHandler_ISO15693* hf_tag = (FedmIscTagHandler_ISO15693*)tagHandler;
                        cout << "hf_tag: " << hf_tag << endl;

                        string uid = hf_tag->GetUID();
                        cout << "uid: " << uid << endl;

                        //чтение
                        //r_code = hf_tag->ReadMultipleBlocks(address, BlockCnt, bsize, data);
                        
                        //запись
                        r_code = hf_tag->WriteMultipleBlocks(address, BlockCnt, bsize, write_data);
                        cout << "r_code: " << r_code << endl;
                    }
                }
            }
        }

        return r_code;
    }

    
    __declspec(dllexport) char * get_error_text(FEDM_ISCReaderModule * reader, int r_code)
    {
        return reader->GetErrorText(r_code);
    }
}
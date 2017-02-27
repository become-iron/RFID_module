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
     __declspec(dllexport) int inventory(FEDM_ISCReaderModule * reader, char ** snr_array)
    {
        unsigned char trans_type = 0;
        char * serial_number = new char [255];
        int block_len = 4;

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
                cout << idx << endl;
                // получение типа транспондера
                reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_TRTYPE, &trans_type);
                // получение строки с идентификатором транспондера
                reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR, serial_number, block_len); // TODO: Выяснить, какой тип должен быть у serial_number: char или unsigned char
                // запись идентификатора транспондера в массив                
                snr_array[idx] = serial_number;
            }
        }

        delete [] serial_number;

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
     __declspec(dllexport) int read_tag(FEDM_ISCReaderModule * reader, char * const & serial_number, char ** read_data)
    {
        unsigned char first_block = 0;
        unsigned char amount = 255;
        int r_code = 0; // код ошибок ридера

        // установка параметров для следующего протокола
        // команда считывания данных
        reader->SetData(FEDM_ISC_TMP_B0_CMD, (unsigned char)0x23);
        // режим адресации
        reader->SetData(FEDM_ISC_TMP_B0_MODE, (unsigned char)0x01);
        // выбор транспондера по идентификатору
        reader->SetData(FEDM_ISC_TMP_B0_REQ_UID, serial_number);
        // определение места считывания
        reader->SetData(FEDM_ISC_TMP_B0_REQ_DB_ADR, first_block);
        // определение количества данных для считывания
        reader->SetData(FEDM_ISC_TMP_B0_REQ_DBN, amount);
        
        // отправка протокола считывания блоков
        r_code = reader->SendProtocol(0xB0);

        return r_code;
    }


    /*
    Функция выполняет запись данных на один транспондер
    Принимает:
        serial_number - идентификатор транспондера          
        write_data - массив данных, которые будут записаны
        first_block - блок, с которого начинается считывание
    */
     __declspec(dllexport) int write_tag(FEDM_ISCReaderModule * reader, char * serial_number,  char ** write_data)    
    {
        unsigned char first_block = 0;
        int r_code = 0; // код ошибок ридера
        int idx = 0;    // идентификатор блока
        unsigned char block_size = 0;   // размер одного блока данных в байтах
        unsigned char data[16]; // буфер для 4 блоков данных по 4 байта
        int data_len = 4;
        int block_len = 4;

        // поиск данных о транспондере в таблице по идентификатору
        idx = reader->FindTableIndex(0, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR, serial_number);  // TODO (nb): тут что-то не то в сигнатуре

        if(idx >= 0)
        {
            // получение размера блока
            reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_BLOCK_SIZE, &block_size);
                
            // получение данных из таблицы
            for(int i=0; i<data_len; i++)
                reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_RxDB, first_block, &data[i*block_size], block_len);
                
            // сборка данных для протокола отправки
            for(int i=0; i<data_len; i++)
                reader->SetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_TxDB, first_block, &data[i*block_size], block_size);
                
            // отправка протокола записи блоков
            reader->SetData(FEDM_ISC_TMP_B0_CMD, (unsigned char)0x24);
            r_code = reader->SendProtocol(0xB0);
        }
        return r_code;
    }

    
    __declspec(dllexport) char * get_error_text(FEDM_ISCReaderModule * reader, int r_code)
    {
        return reader->GetErrorText(r_code);
    }
}

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
        // ��������� ���� ������
        reader->SetBusAddress(bus_addr);
        // ��������� ������� ������� (�� 100 ����� �� ����� �������������� � Host-Mode)
        reader->SetTableSize(FEDM_ISC_ISO_TABLE, 100);
        // ��������� TagHandler
        reader->EnableTagHandler(true);
        // �������� ���������� � ���� ������
        reader->ReadReaderInfo();
        // ������������ � COM-�����
        int r_code = reader->ConnectCOMM(port_number);

        if (r_code == 0)
        {
            // ����������� �������� �������� ������
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
    ������� ���� ������������ � ���� �������� ������� � �������� ���������� � ���
    ���������:
        snr_array - ������ �� ������, � ������� ��������� �������������� �������������
    */
     __declspec(dllexport) int inventory(FEDM_ISCReaderModule * reader, char ** snr_array)
    {
        unsigned char trans_type = 0;
        char * serial_number = new char [255];
        int block_len = 4;

        // ��������� ���������� ��� ���������� ��������� 
        // ������� ��������������
        reader->SetData(FEDM_ISC_TMP_B0_CMD, (unsigned char)0x01);
        // ������� ������
        reader->SetData(FEDM_ISC_TMP_B0_MODE, (unsigned char)0x00);
        // ������������ ����� ��� ���������� ���������
        reader->ResetTable(FEDM_ISC_ISO_TABLE);
        // �������� ��������� ��������������
        int r_code = reader->SendProtocol(0xB0);

        if(r_code == 0)
        {
            // ���������� ������� ������� � �������������
            for (int idx=0; idx < reader->GetTableLength(FEDM_ISC_ISO_TABLE); idx++)
            {
                cout << idx << endl;
                // ��������� ���� ������������
                reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_TRTYPE, &trans_type);
                // ��������� ������ � ��������������� ������������
                reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR, serial_number, block_len); // TODO: ��������, ����� ��� ������ ���� � serial_number: char ��� unsigned char
                // ������ �������������� ������������ � ������                
                snr_array[idx] = serial_number;
            }
        }

        delete [] serial_number;

        return r_code;
    }


    /*
    ������� ��������� ���������� ������ � ������ ������������
    ���������:
        serial_number - ������������� ������������            
        read_data - ������, � ������� ����� �������� ��������� ������
        first_block - ����, � �������� ���������� ����������
        amount - ���������� ������, ������� ����� �������
    */
      // TODO (nb): ��� serial_number, ��������, ������ char const *
     __declspec(dllexport) int read_tag(FEDM_ISCReaderModule * reader, char * const & serial_number, char ** read_data)
    {
        unsigned char first_block = 0;
        unsigned char amount = 255;
        int r_code = 0; // ��� ������ ������

        // ��������� ���������� ��� ���������� ���������
        // ������� ���������� ������
        reader->SetData(FEDM_ISC_TMP_B0_CMD, (unsigned char)0x23);
        // ����� ���������
        reader->SetData(FEDM_ISC_TMP_B0_MODE, (unsigned char)0x01);
        // ����� ������������ �� ��������������
        reader->SetData(FEDM_ISC_TMP_B0_REQ_UID, serial_number);
        // ����������� ����� ����������
        reader->SetData(FEDM_ISC_TMP_B0_REQ_DB_ADR, first_block);
        // ����������� ���������� ������ ��� ����������
        reader->SetData(FEDM_ISC_TMP_B0_REQ_DBN, amount);
        
        // �������� ��������� ���������� ������
        r_code = reader->SendProtocol(0xB0);

        return r_code;
    }


    /*
    ������� ��������� ������ ������ �� ���� �����������
    ���������:
        serial_number - ������������� ������������          
        write_data - ������ ������, ������� ����� ��������
        first_block - ����, � �������� ���������� ����������
    */
     __declspec(dllexport) int write_tag(FEDM_ISCReaderModule * reader, char * serial_number,  char ** write_data)    
    {
        unsigned char first_block = 0;
        int r_code = 0; // ��� ������ ������
        int idx = 0;    // ������������� �����
        unsigned char block_size = 0;   // ������ ������ ����� ������ � ������
        unsigned char data[16]; // ����� ��� 4 ������ ������ �� 4 �����
        int data_len = 4;
        int block_len = 4;

        // ����� ������ � ������������ � ������� �� ��������������
        idx = reader->FindTableIndex(0, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_SNR, serial_number);  // TODO (nb): ��� ���-�� �� �� � ���������

        if(idx >= 0)
        {
            // ��������� ������� �����
            reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_BLOCK_SIZE, &block_size);
                
            // ��������� ������ �� �������
            for(int i=0; i<data_len; i++)
                reader->GetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_RxDB, first_block, &data[i*block_size], block_len);
                
            // ������ ������ ��� ��������� ��������
            for(int i=0; i<data_len; i++)
                reader->SetTableData(idx, FEDM_ISC_ISO_TABLE, FEDM_ISC_DATA_TxDB, first_block, &data[i*block_size], block_size);
                
            // �������� ��������� ������ ������
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

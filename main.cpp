
#include <stdio.h>

//!FIXME Make this global
#include "acr122.h"

int main(int argc, char *argv[])
{

    acr122* device = new acr122("/dev/ttyUSB0");
    device->EnableLcdBacklight(1);
    device->Beep(3,1,5);
    device->EnableLcdBacklight(0);
    /*HANDLE hReader;
    DWORD ret;
    DWORD numSlots;
    char firmwareVersion[15];
    DWORD firmwareVersionLen;
    DWORD i;

    // Open reader using COM1
    printf("Opening reader...\n");
    ret = ACR122_Open("/dev/ttyS0", &hReader);
    if (ret != ERROR_SUCCESS)
    {
        printf("Error: ACR122_Open failed with error 0x%08X\n", ret);
        return 1;
    }

    // Get number of slots
    printf("Getting number of slots...\n");
    ret = ACR122_GetNumSlots(hReader, &numSlots);
    if (ret != ERROR_SUCCESS)
    {
        printf("Error: ACR122_GetNumSlots failed with error 0x%08X\n", ret);
    }
    else
    {
        printf("Number of slots: %d\n", numSlots);
        printf("Getting firmware version...\n");
        for (i = 0; i < numSlots; i++)
        {
            firmwareVersionLen = sizeof(firmwareVersion);
            ret = ACR122_GetFirmwareVersion(hReader, i, firmwareVersion, &firmwareVersionLen);
            if (ret != ERROR_SUCCESS)
            {
                printf("Error: ACR122_GetFirmwareVersion failed with error 0x%08X\n", ret);
            }
            else
            {
                printf("Slot %d: %s\n", i, firmwareVersion);
            }
        }
    }

    // Close reader
    printf("Closing reader...\n");
    ret = ACR122_Close(hReader);
    if (ret != ERROR_SUCCESS)
    {
        printf("Error: ACR122_Close failed with error 0x%08X\n", ret);
    }

    return 0;*/
}


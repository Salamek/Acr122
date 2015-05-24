#ifndef ACR122_H
#define ACR122_H
#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <iostream>
#include <vector>

using namespace std;

class acr122
{
public:
    acr122(const char *device);
    ~acr122();
    int EnableLcdBacklight(bool state = true);
    int GetNumSlots();
    int GetBaudRate();
    int SetBaudRate();
    int GetTimeouts();
    int SetTimeouts();
    int GetFirmwareVersion();
    int DisplayLcdMessageEx();
    int DisplayLcdMessageGB();
    int DrawLcd();
    int StartLcdScrolling();
    int StopLcdScrolling();
    int PauseLcdScrolling();
    int ClearLcd();
    int SetLcdContrast();
    int EnableLed(int enabled);
    int SetLedStatesWithBeep();
    int SetLedStates();
    int DirectTransmit();
    int PowerOffIcc();
    int ExchangeApdu();
    int Beep(int on = 1, int off = 1, int repeats = 1);
    int PowerOnIcc();
    int DisplayLcdMessage(const std::string &message, const std::string &fontSet, bool bold, int position);
private:
    int handle;
    long commandCounter;
    const char Command(char *command);
    int set_interface_attribs(int fd, int speed, int parity);
    int DebugArray(char *arr, size_t arraySize);
};

#endif // ACR122_H

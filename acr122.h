#ifndef ACR122_H
#define ACR122_H

#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

class acr122
{
public:
    acr122(const char *device);
    ~acr122();
    int EnableLcdBacklight(int state = 1);
    int GetNumSlots();
    int GetBaudRate();
    int SetBaudRate();
    int GetTimeouts();
    int SetTimeouts();
    int GetFirmwareVersion();
    int DisplayLcdMessage();
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
private:
    int handle;
    long commandCounter;
    const char Command(char *command);
    int set_interface_attribs(int fd, int speed, int parity);
};

#endif // ACR122_H

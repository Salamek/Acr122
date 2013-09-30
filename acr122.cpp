#include "acr122.h"
#include <termios.h>
#include <string.h>
//!FIXME Only for devel, remove me
#include <stdlib.h>
#include <iostream>
using namespace std;

acr122::acr122(const char* device)
{
    //Reset command counter
     //!FIXME prevent owerflow
    commandCounter = 1;

    handle = open(device, O_RDWR | O_NOCTTY | O_NDELAY);

    if(handle < 0)
    {
        cout << "Failed to open a port " << device << endl;
        exit (EXIT_FAILURE);
    }
    else
    {
        this->set_interface_attribs (handle, B115200, 0);
    }
}

acr122::~acr122()
{
    close(handle);
}

const char acr122::Command(char* command)
{
    //Global config
    int commandStartByte = 0x02;
    int commandEndByte = 0x03;

    //Response config
    char wholeBuffer[50];//@TODO Maybe we will need bigger one, do some checks to prevent overflow
    int totalLength = 0;
    char responseFailHeader[] = {commandStartByte, 0xFF, 0xFF, commandEndByte};
    char responseHeaderSize = sizeof(responseFailHeader)/sizeof(responseFailHeader[0]);

    //Request config
    int finalOffset = 0;
    int commandSum = 0;
    char header[] = {0x6F, sizeof(command), 0x00, 0x00, 0x00, 0x00, commandCounter, 0x00, 0x00, 0x00};

    size_t commandSize = sizeof(command)/sizeof(command[0]);
    size_t headerSize = sizeof(header)/sizeof(header[0]);

    //+3 are command start c_stx, command end c_etx and command sum c_sum
    size_t finalSize = commandSize + headerSize + 3;


    //Build final command
    char final[finalSize];

    final[finalOffset++] = commandStartByte;

    //Append header
    for(int i = 0; i < headerSize; i ++ )
    {
        final[finalOffset++] = header[i];
    }

    //Append command
    for(int i = 0; i < commandSize; i ++ )
    {
        final[finalOffset++] = command[i];
    }

    //Append sum
    for(int i = 0; i < headerSize; i ++ )
    {
        commandSum ^= header[i];
    }

    for(int i = 0; i < commandSize; i ++ )
    {
        commandSum ^= command[i];
    }

    //final[finalOffset++] = commandSum;

    //End of command
    final[finalOffset++] = commandEndByte;

    //Send command to device
    write(handle, final, finalSize);

    //Read response
    while(1)
    {
        char whileBuffer[50]; //@TODO Maybe we will need bigger one, do some checks to prevent overflow
        ssize_t length = read(handle, &whileBuffer, sizeof(whileBuffer)/ sizeof(whileBuffer[0]));
        if(length > 0 )
        {
            whileBuffer[length] = '\0';
            for(int i = 0; i < length; i ++ )
            {
                wholeBuffer[totalLength++] = whileBuffer[i];
            }

            //Check header when i got firts 4 bytes (Thats status header)
            if(totalLength == responseHeaderSize)
            {
                if(strstr (wholeBuffer, responseFailHeader) > 0)
                {
                    cout << "Device do not understand this command or command is in wrong format!" << endl;
                    break;
                }
            }
            //We read more then 4 bytes, that means header was ok and also last byte wont be 0x03 as header end,
            //but 0x02 as body start or more(somewhere in middle of body), so i can wait for another 0x03 as body end and stop reading from port!
            //So data here should look like {0x02, 0x00, 0x00, 0x03, 0x02, ..., 0x03}
            else if(totalLength > responseHeaderSize && wholeBuffer[totalLength - 1] == commandEndByte)
            {
                wholeBuffer[totalLength] = '\0';
                break;
            }
        }
    }


    //Here i need only body, so lets prepare nice and clean char array for it
    char bodyBuffer[totalLength - responseHeaderSize];
    for(int i = responseHeaderSize; i < totalLength; i ++ )
    {
        bodyBuffer[i - responseHeaderSize] = wholeBuffer[i];
    }

    //Here we should have whole OK response
    for(int i = 0; i < totalLength; i ++ )
    {
        printf("Whole thing: %d \n", wholeBuffer[i]);
    }

    for(int i = 0; i < sizeof(bodyBuffer)/ sizeof(bodyBuffer[0]); i ++ )
    {
        printf("Body: %d \n", bodyBuffer[i]);
    }

    //Move up a commandCounter
    commandCounter++;
}

int acr122::set_interface_attribs (int fd, int speed, int parity)
{
    struct termios tty;
    memset (&tty, 0, sizeof tty);
    if (tcgetattr (fd, &tty) != 0)
    {
            //error_message ("error %d from tcgetattr", errno);
        cout << "Error tcgerattr failed";
            return -1;
    }

    cfsetospeed (&tty, speed);
    cfsetispeed (&tty, speed);

    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;     // 8-bit chars
    // disable IGNBRK for mismatched speed tests; otherwise receive break
    // as \000 chars
    tty.c_iflag &= ~IGNBRK;         // ignore break signal
    tty.c_lflag = 0;                // no signaling chars, no echo,
                                    // no canonical processing
    tty.c_oflag = 0;                // no remapping, no delays
    tty.c_cc[VMIN]  = 0;            // read doesn't block
    tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

    tty.c_iflag &= ~(IXON | IXOFF | IXANY); // shut off xon/xoff ctrl

    tty.c_cflag |= (CLOCAL | CREAD);// ignore modem controls,
                                    // enable reading
    tty.c_cflag &= ~(PARENB | PARODD);      // shut off parity
    tty.c_cflag |= parity;
    tty.c_cflag &= ~CSTOPB;
    tty.c_cflag &= ~CRTSCTS;

    if (tcsetattr (fd, TCSANOW, &tty) != 0)
    {
            //error_message ("error %d from tcsetattr", errno);
            cout << "Error tcgerattr failed 2";
            return -1;
    }
    return 0;
}


int acr122::EnableLcdBacklight(int state)
{
    int c_class = 0xFF;
    int c_ins = 0x00;
    int c_p1 = 0x64;
    int c_p2 = (state ? 0xFF : 0x00); //0x00  disable #0xFF enable
    int c_lc = 0x00;
    char command[] = {c_class, c_ins, c_p1, c_p2, c_lc};
    this->Command(command);
}

int acr122::GetNumSlots()
{
    throw "Not implemented";
}

int acr122::GetBaudRate()
{
    throw "Not implemented";
}

int acr122::SetBaudRate()
{
    throw "Not implemented";
}

int acr122::GetTimeouts()
{
    throw "Not implemented";
}

int acr122::SetTimeouts()
{
    throw "Not implemented";
}

int acr122::GetFirmwareVersion()
{
    throw "Not implemented";
}

int acr122::DisplayLcdMessage()
{
    throw "Not implemented";
}

int acr122::DisplayLcdMessageEx()
{
    throw "Not implemented";
}

int acr122::DisplayLcdMessageGB()
{
    throw "Not implemented";
}

int acr122::DrawLcd()
{
    \
}

int acr122::StartLcdScrolling()
{

}

int acr122::StopLcdScrolling()
{

}

int acr122::PauseLcdScrolling()
{

}

int acr122::ClearLcd()
{

}

int acr122::SetLcdContrast()
{

}

int acr122::EnableLed(int enabled)
{

}

int acr122::SetLedStatesWithBeep()
{

}

int acr122::SetLedStates()
{

}

int acr122::Beep(int on, int off, int repeats)
{
    char command[] = {0xFF, 0x00, 0x42, 0x00, 0x03, on, off, repeats};
    this->Command(command);
}

int acr122::DirectTransmit()
{

}

int acr122::PowerOnIcc()
{

}

int acr122::PowerOffIcc()
{

}

int acr122::ExchangeApdu()
{

}

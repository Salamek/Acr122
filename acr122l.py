#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       232b.py
#
#       Copyright 2011 Adam Schubert <feartohell@seznam.cz>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import serial
import time


class acr122l:

    #Configuration
    rs232_ok = 0x90

    #internal global values
    rs232_command_counter = 1
    rs232_command_done = True

    user_led_control = False


    #constructor
    def __init__(self, rs232_port = '/dev/ttyS0', rs232_baudrate = 115200 ):
        self.init_rs232(rs232_port, rs232_baudrate)
        #self.set_baudrate(rs232_baudrate)

    #************************
    #MAIN COMUNICATION
    #************************

    #serial port init
    def init_rs232(self, rs232_port, rs232_baudrate):
        self.ser = serial.Serial()
        self.ser.baudrate = rs232_baudrate
        self.ser.port = rs232_port
        self.ser.timeout = 3

        try:
            self.ser.open()
        except serial.SerialException, e:
            raise Exception('Connecion failed! is device connected to ' + rs232_port + '?')

        if self.ser.isOpen():
            print 'Serial port '+ rs232_port +' opened ...'
            #if self.get_sam_version()==False:
            #    raise Exception('Testing command failed, is device connected to '+ rs232_port +' ?')
            #else:
            #    print 'Connecion is OK!'


    def disconnect(self):
        if self.ser.isOpen():
            self.ser.close()


    #sending command wia serial port
    #@c_command command array
    #@c_stx stx of command default is set
    #@c_etx etx of command default is set
    #@custom_header if u need custom header
    def rs232_command(self, c_command, sleep = 0.1, c_stx = 0x02, c_etx = 0x03, custom_header = False):
        if self.ser.isOpen():
            if self.rs232_command_done:
                self.rs232_command_done = False
                print 'Sending command #:' + hex(self.rs232_command_counter)

                # building command
                c_command_joined = "".join([chr(int(x)) for x in c_command])
                c_command_len = len(c_command)

                #building header
                if custom_header:
                    #custom header
                    c_header = custom_header
                else:
                    #default header
                    c_header = [0x6F, c_command_len, 0x00, 0x00, 0x00, 0x00, self.rs232_command_counter, 0x00, 0x00, 0x00]

                c_header_joined = "".join([chr(x) for x in c_header])

                #building sum of header ^ command
                c_sum = 0
                for c_c_out in c_command:
                    c_sum ^= c_c_out

                for c_h_out in c_header:
                    c_sum ^= c_h_out

                print ("Sum is" + str(c_sum))
                #building full command to send
                joined = chr(c_stx)+c_header_joined+c_command_joined+chr(c_sum)+chr(c_etx)
                with open("total.dat","a+") as f:
                  f.write(joined)

                with open("header.dat","a+") as f:
                  f.write(c_header_joined)

                with open("command.dat","a+") as f:
                  f.write(c_command_joined)
                #time.sleep(sleep)
                #sending command
                if self.ser.isOpen():
                    self.ser.write(joined)
                #counting commands
                self.rs232_command_counter += 1

                if self.rs232_command_counter == 256:
                    self.rs232_command_counter = 1

                #lets w8 for serial port
                time.sleep(sleep)

                #reading output
                if self.ser.isOpen():
                    out = self.ser.read(1)
                    if out:
                        while self.ser.inWaiting() > 0:
                            out += self.ser.read(self.ser.inWaiting())
                        out_int = []
                        for i in out:
                            out_int.append(int(hex(ord(i)),16))

                        if out_int and self.ser.inWaiting()==0:
                            self.rs232_command_done = True

                        return out_int
                else:
                    return False
            else:
                time.sleep(sleep) #dame mu cas aby se dodelal
                self.rs232_command_done = True
        else:
            return False



    def is_respawn_ok(self, data):
        if data[1] == 0x00 and data[1] == 0x00:
            return True
        else:
            return False




    def is_connected(self):
        if self.ser.isOpen():
            return True
        else:
            return False
    #**************
    #POMOCNE FUNKCE
    #**************

    #encodes ascii to int
    def asci2int(self, char):
        hexa = (hex(ord(char)))[2:4]
        return int(hexa,16)

    #encodes int to ascii
    def int2asci(self, chars):
        char = chr(int(hex(chars),16))
        ch = "".join(i for i in char if ord(i)<128)
        if len(ch):
            return ch
        else:
            return False

    #returns type of card by sel_res
    def tag_type(self, sel_res):
        if sel_res == 0x00:
            return 'MIFARE Ultralight'
        elif sel_res == 0x08:
            return 'MIFARE 1K'
        elif sel_res == 0x09:
            return 'MIFARE MINI'
        elif sel_res == 0x18:
            return 'MIFARE 4K'
        elif sel_res == 0x20:
            return 'MIFARE DESFIRE'
        elif sel_res == 0x28:
            return 'JCOP30'
        elif sel_res == 0x98:
            return 'Gemplus MPCOS'


    #output debugging tool
    def debug(self, out):
        for c in out:
            print hex(c) + ' --> ' + str(int(hex(c),16)) + ' --> ' + chr(int(hex(c),16))

    #translate hex list
    def hextranslate(self, s):
        res = ''
        for i in s:
            res = res + chr(int(hex(i),16))
        return res


    #sets baudrate
    def set_baudrate(self, baudrate=115200):
        baudrate = int(baudrate)
        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x44

        if baudrate==115200:
            c_p2 = 0x01
        elif baudrate==9600:
            c_p2 = 0x00
        c_lc = 0x00

        command = [c_class, c_ins, c_p1, c_p2, c_lc]
        ret = self.rs232_command(command,0.1,0x32,0x33)
        if ret[15] == self.rs232_ok: #respawn is ok
            print 'Baudrate set to ' + str(baudrate)
            return True
        else:
            return False


    #************************
    #LCD CONTROL
    #************************

    #enables/disables LCD backlight
    #@state true/false
    def LCD_back_light(self, state=True):

        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x64
        if(state):
            c_p2 = 0xFF #0x00  disable #0xFF enable
        else:
            c_p2 = 0x00
        c_lc = 0x00

        command = [c_class, c_ins, c_p1, c_p2, c_lc]
        ret = self.rs232_command(command)
        if ret:
            if ret[15] == self.rs232_ok: #respawn is ok
                return True
            else:
                return False

    #writes text on LCD
    def LCD_Text(self, bold=False, font_set='A', position=0x00, message=None):
        if message:
            c_class = 0xFF
            if bold:
                bold = '1'
            else:
                bold = '0'

            if(font_set =='A'):
                font_set = '00'
                if position > 0x4F or position < 0x00: # je pozice v rozsahu fontsetu ?
                    return False

            elif(font_set =='B'):
                font_set = '01'
                if position > 0x6F  or position < 0x00: # je pozice v rozsahu fontsetu ?
                    return False

            elif(font_set =='C'):
                font_set = '10'
                if position > 0x6F  or position < 0x00: # je pozice v rozsahu fontsetu ?
                    return False

            c_ins = int(hex(int('0b'+bold+'000'+font_set+'00',2)), 16)
            c_p1 = 0x68
            c_p2 = position
            c_lc = len(message)



            command = [c_class, c_ins, c_p1, c_p2, c_lc]

            for char in message:
                command.append(self.asci2int(char))


            ret = self.rs232_command(command)
            if ret[15]== self.rs232_ok: #respawn is ok
                return True
            else:
                return False
        else:
            return False


    #writes text on LCD Chinese!
    def LCD_TextGB(self, bold=False,  position=0x00, message=''):
        c_class = 0xFF
        if bold:
            bold = '1'
        else:
            bold = '0'

        if position > 0x47 or position < 0x00: # je pozice v rozsahu fontsetu ?
            return False


        c_ins = int(hex(int('0b'+bold+'0000000',2)), 16)
        c_p1 = 0x68
        c_p2 = position
        c_lc = len(message)*2



        command = [c_class, c_ins, c_p1, c_p2, c_lc]

        for char in message:
            command.append(self.asci2int(char))


        ret = self.rs232_command(command)
        if ret[15] == self.rs232_ok: #respawn is ok
            return True
        else:
            return False


    #writes pixels on LCD
    def LCD_Graphic(self, bold=False,  line=0x00, pixels=False):
        c_class = 0xFF

        if line > 0x1F or line < 0x00: # je pozice v rozsahu fontsetu ?
            return False


        c_ins = 0x00
        c_p1 = 0x6A

        c_p2 = line
        c_lc = len(pixels)



        command = [c_class, c_ins, c_p1, c_p2, c_lc]

        for char in pixels:
            command.append(char)


        ret = self.rs232_command(command)
        if ret[15] == self.rs232_ok: #respawn is ok
            return True
        else:
            return False

    #Controls scroling Start
    def LCD_Scrolling(self, direcion='l2r', speed=1):
        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x6D
        c_p2 = 0x00
        c_lc = 0x06

        command = [c_class, c_ins, c_p1, c_p2, c_lc]

        if(direcion =='l2r'):#from left 2 right
            direcion_code='00'
        elif(direcion =='r2l'):#from right to left
            direcion_code='01'
        elif(direcion =='t2b'):#from top to bottom
            direcion_code='10'
        elif(direcion =='b2t'):#from bottom to top
            direcion_code='11'




        b4 = int(hex(int('0b1111',2)), 16)
        b5 = int(hex(int('0b'+direcion_code,2)), 16)
        default = [0x00, 0x00, 0x0F,0x1F, b4, b5]
        for c in default:
            command.append(c)



        ret = self.rs232_command(command)
        if ret[15] == self.rs232_ok: #respawn is ok
            return True
        else:
            return False

    #Controls scroling Stop/Pause
    def LCD_ScrollingControl(self, direcion='Pause'):
        c_class = 0xFF
        c_ins = 0x00
        if(direcion == 'Pause'):
            c_p1 = 0x6E
        elif(direcion == 'Stop'):
            c_p1 = 0x6F

        c_p2 = 0x00
        c_lc = 0x06

        command = [c_class, c_ins, c_p1, c_p2, c_lc]

        ret = self.rs232_command(command)
        if ret[15] == self.rs232_ok: #respawn is ok
            return True
        else:
            return False



    #clears LCD
    def LCD_Clear(self):
        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x60
        c_p2 = 0x00
        c_lc = 0x00

        command = [c_class, c_ins, c_p1, c_p2, c_lc]
        ret = self.rs232_command(command)
        if ret:
            if ret[15] == self.rs232_ok: #respawn is ok
                return True
            else:
                return False

    #sets LCD contrast min 0 max 15 or F Hex
    def LCD_Contrast(self, contrast=0x0F):
        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x6C
        c_p2 = contrast
        c_lc = 0x00

        command = [c_class, c_ins, c_p1, c_p2, c_lc]
        ret = self.rs232_command(command)
        if ret[15] == self.rs232_ok: #respawn is ok
            return True
        else:
            return False

    #************************
    #LED CONTROL
    #************************

    #control leds on device
    def LED_control(self, led=False):
        if not self.user_led_control and led:
            #first we must enable LEDs user control
            c_class = 0xFF
            c_ins = 0x00
            c_p1 = 0x43
            c_p2 = 0xFF

            c_lc = 0x00

            command = [c_class, c_ins, c_p1, c_p2, c_lc]
            ret_control = self.rs232_command(command)
            if ret_control[15] == self.rs232_ok: #respawn is ok
                self.user_led_control = True
            else:
                self.user_led_control = False

            #send new led state
            c_class = 0xFF
            c_ins = 0x00
            c_p1 = 0x41
            led = ''.join(reversed(led))

            c_p2 = int(hex(int('0b0111'+led,2)), 16)

            c_lc = 0x00

            command = [c_class, c_ins, c_p1, c_p2, c_lc]
            ret = self.rs232_command(command)
            if ret[15] == self.rs232_ok: #respawn is ok
                return True
            else:
                return False

        else:
            if led:
                #here we can control LEDs cos we enabled user control and led is set
                c_class = 0xFF
                c_ins = 0x00
                c_p1 = 0x41
                led = ''.join(reversed(led))

                c_p2 = int(hex(int('0b0111'+led,2)), 16)

                c_lc = 0x00

                command = [c_class, c_ins, c_p1, c_p2, c_lc]
                ret = self.rs232_command(command)
                if ret[15] == self.rs232_ok: #respawn is ok
                    return True
                else:
                    return False
            else:
                #led control is enabled but leds is not set, so disable led control
                c_class = 0xFF
                c_ins = 0x00
                c_p1 = 0x43
                c_p2 = 0x00
                c_lc = 0x00

                command = [c_class, c_ins, c_p1, c_p2, c_lc]
                ret_control = self.rs232_command(command)
                if ret_control[15] == self.rs232_ok: #respawn is ok
                    self.user_led_control = False
                else:
                    self.user_led_control = True


    #*********************
    #BUZZER CONTROL
    #*********************

    # buzzer control one unit  = 1000ms
    def Buzzer_control(self, on=0x01, off=0x01, repeat =0x01):
        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x42
        c_p2 = 0x00
        c_lc = 0x03

        command = [c_class, c_ins, c_p1, c_p2, c_lc]
        default = [on, off, repeat]
        for c in default:
            command.append(c)

        ret = self.rs232_command(command)
        if(len(ret)<15):
            return False
        else:
            if ret[15] == self.rs232_ok: #respawn is ok
                return True
            else:
                return False

    #***********************
    #BUZZER & LED CONTROL
    #***********************
    def Buzzer_Led_control(self, led_control='00000000',on=0x01, off=0x01, repeat =0x01,buzzer_link=False):
        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x40
        #LED State Control
        led_control = ''.join(reversed(led_control))
        c_p2 = int(hex(int('0b'+led_control,2)), 16)
        c_lc = 0x04

        command = [c_class, c_ins, c_p1, c_p2, c_lc]

        if buzzer_link:
            if buzzer_link == 'on':
                buzzer_link = 0x01
            elif buzzer_link == 'off':
                buzzer_link = 0x02
            elif buzzer_link == 'onoff':
                buzzer_link = 0x03
        else:
            buzzer_link = 0x00

        #Blinking Duration Control
        default = [on, off, repeat, buzzer_link]
        for c in default:
            command.append(c)


        ret = self.rs232_command(command)
        if(len(ret)<15):
            return False
        else:
            if ret[15] == self.rs232_ok: #respawn is ok
                return True
            else:
                return False

    def TAG_Polling(self):
        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x00
        c_p2 = 0x00
        c_lc = 0x09

        command = [c_class, c_ins, c_p1, c_p2, c_lc]

        default = [0xD4, 0x60, 0x01, 0x01, 0x20, 0x23, 0x11, 0x04, 0x10]
        for c in default:
            command.append(c)

        ret = self.rs232_command(command,0.7)

        if len(ret)>17:
            if ret[17] > 0:
                print str(ret[17]) + ' tags detected'

                target_number = ret[18] #Target number
                sens_res = [ret[19],ret[20]] #SENS_RES
                sel_res = ret[21] #SEL_RES
                len_uid = ret[22] #Length of the UID
                end_uid = 25+len_uid
                uid = []
                for i in range(25, end_uid):
                    uid.append(ret[i])

                arr = {'target_number':target_number,'sel_res':sel_res,'sel_res':sel_res,'uid':uid}

                return arr
            else:
                print 'No tag detected'
                return False
        else:
            return False

    def get_sam_version(self, sam=0x01):

        ver_start = 15

        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x48
        c_p2 = 0x00
        c_lc = 0x03

        command = [c_class, c_ins, c_p1, c_p2, c_lc]

        if sam == 0x01:
            c_stx = 0x02
            c_etx = 0x03
        elif sam == 0x02:
            c_stx = 0x12
            c_etx = 0x13
        elif sam == 0x03:
            c_stx = 0x22
            c_etx = 0x23

        ret = self.rs232_command(command,0.1, c_stx, c_etx)

        if ret:
            if len(ret) == 31:
                ver = []
                for i in range(ver_start,ver_start+ret[6]):
                    ver.append(ret[i])
                version = self.hextranslate(ver)

                if version:
                    return version
                else:
                    return False
            else:
                return False
        else:
            return False



    def TAG_Authenticate(self, block, key, uid = False, key_type='A'):

        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x00
        c_p2 = 0x00
        c_lc = 0x0f

        command = [c_class, c_ins, c_p1, c_p2, c_lc]

        if key_type =='A':
            key_type = 0x60
        elif(key_type =='B'):
            key_type = 0x61

        default = [0xD4, 0x40, 0x01, key_type]
        for c in default:
            command.append(c)

        command.append(block)

        for k in key:
            command.append(k)

        if uid:
            for u in uid:
                command.append(u)
        else:
            r = self.TAG_Polling()
            if r:
                for i in r['uid']:
                    command.append(i)
            else:
                return False

        ret = self.rs232_command(command)

        if len(ret) == 22:

            if ret[18] == self.rs232_ok and ret[17]==0x00:
                print 'Tag descripted'
                return True
            elif ret[18] == self.rs232_ok and ret[17]!=0x00:
                print 'Error - check table'
                return False
        else:
            return False


    def TAG_Read(self, block=0x01):

        c_class = 0xFF
        c_ins = 0x00
        c_p1 = 0x00
        c_p2 = 0x00
        c_lc = 0x05

        command = [c_class, c_ins, c_p1, c_p2, c_lc,0xD4, 0x40, 0x01, 0x30, int(block)]
        ret = self.rs232_command(command)
        if len(ret) >17:

            if ret[17]==0x00:
                out = ''
                for s in range(18,18+16): #we gonna read all the shitt on tag
                    if int(hex(ret[s]),16) > 0:
                      out = out + self.int2asci(ret[s])
                out = out.strip()
                if out:
                    if isinstance(out, str):
                        return out
                    else:
                        return str(out)
                else:
                    return False

            elif ret[17]!=0x00:
                raise Exception('Error, check table')
                return False
        else:
            return False

    def TAG_Update(self, block=0x01, data_in=False,data_type='HEX'):

        if len(data_in)>16:
            print 'data is too long'
        else:
            data = []
            for t in range(0,16):
                data.append(' ')

            cnt = 0
            for d in data_in:
                data.insert(cnt, d)
                cnt = cnt + 1

            c_class = 0xFF
            c_ins = 0x00
            c_p1 = 0x00
            c_p2 = 0x00
            c_lc = 0x15

            command = [c_class, c_ins, c_p1, c_p2, c_lc,0xD4, 0x40, 0x01, 0xA0, int(block)]

            if data_type=='HEX':
                for d in data:
                    command.append(d)
            elif data_type=='ASCII':
                for d in data:
                    command.append(self.asci2int(d))

            ret = self.rs232_command(command)

            if len(ret) >18:

                if ret[18]==0x90:
                    return True
                else:
                    return False
            else:
                return False










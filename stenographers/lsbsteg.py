
# Taken from the amazing script in https://github.com/RobinDavid/LSB-Steganography

from stenographers import Stenograph, SteganographyException


class LSBSteg(Stenograph):
    def __init__(self) :
        
        self.maskONEValues = [1,2,4,8,16,32,64,128]
        #Mask used to put one ex:1->00000001, 2->00000010 .. associated with OR bitwise
        self.maskONE = self.maskONEValues.pop(0) #Will be used to do bitwise operations
        
        self.maskZEROValues = [254,253,251,247,239,223,191,127]
        #Mak used to put zero ex:254->11111110, 253->11111101 .. associated with AND bitwise
        self.maskZERO = self.maskZEROValues.pop(0)
        
        self.curwidth = 0  # Current width position
        self.curheight = 0 # Current height position
        self.curchan = 0   # Current channel position

    def put_binary_value(self, bits): #Put the bits in the image
        for c in bits:
            val = list(self.image[self.curheight,self.curwidth]) #Get the pixel value as a list
            if int(c) == 1:
                val[self.curchan] = int(val[self.curchan]) | self.maskONE #OR with maskONE
            else:
                val[self.curchan] = int(val[self.curchan]) & self.maskZERO #AND with maskZERO
                
            self.image[self.curheight,self.curwidth] = tuple(val)
            self.next_slot() #Move "cursor" to the next space
        
    def next_slot(self): #Move to the next slot were information can be taken or put
        if self.curchan != self.nbchannels-1: #Next Space is the following channel
            self.curchan +=1
            return

        self.curchan = 0
        if self.curwidth != self.width-1: #Or the first channel of the next pixel of the same line
            self.curwidth +=1
            return

        self.curwidth = 0
        if self.curheight != self.height-1:#Or the first channel of the first pixel of the next line
            self.curheight +=1
            return
        self.curheight = 0

        if self.maskONE == 128: #Mask 1000000, so the last mask
            raise SteganographyException("No available slot remaining (image filled)")

        #Or instead of using the first bit start using the second and so on..
        self.maskONE = self.maskONEValues.pop(0)
        self.maskZERO = self.maskZEROValues.pop(0)

    def read_bit(self) -> str: #Read a single bit int the image
        val = self.image[self.curheight,self.curwidth][self.curchan]
        val = int(val) & self.maskONE
        self.next_slot()
        return "1" if val > 0 else "0"
    
    def read_byte(self):
        return self.read_bits(8)
    
    def read_bits(self, nb): #Read the given number of bits
        return "".join(self.read_bit() for _ in range(nb))

    def byteValue(self, val):
        return self.binary_value(val, 8)
        
    def binary_value(self, val, bitsize): #Return the binary value of an int as a byte
        binval = bin(val)[2:]
        if len(binval) > bitsize:
            raise SteganographyException("binary value larger than the expected size")
        while len(binval) < bitsize:
            binval = "0"+binval
        return binval

    def encode(self, data: bytes):
        l = len(data)
        if self.width*self.height*self.nbchannels < l+64:
            raise SteganographyException("Carrier image not big enough to hold all the datas to steganography")
        self.put_binary_value(self.binary_value(l, 64))
        for byte in data:
            byte = byte if isinstance(byte, int) else ord(byte) # Compat py2/py3
            self.put_binary_value(self.byteValue(byte))
        return self.image

    def decode(self) -> bytes:
        l = int(self.read_bits(64), 2)
        print(l)
        return b"".join(bytearray([int(self.read_byte(),2)]) for _ in range(l))


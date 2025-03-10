# Author: Marco Simoes
# Adapted from Java's implementation of Rui Pedro Paiva
# Teoria da Informacao, LEI, 2022

import sys
from huffmantree import HuffmanTree
from typing import Counter


class GZIPHeader:
    ''' class for reading and storing GZIP header fields '''

    ID1 = ID2 = CM = FLG = XFL = OS = 0
    MTIME = []
    lenMTIME = 4
    mTime = 0

    # bits 0, 1, 2, 3 and 4, respectively (remaining 3 bits: reserved)
    FLG_FTEXT = FLG_FHCRC = FLG_FEXTRA = FLG_FNAME = FLG_FCOMMENT = 0   
    
    # FLG_FTEXT --> ignored (usually 0)
    # if FLG_FEXTRA == 1
    XLEN, extraField = [], []
    lenXLEN = 2
    
    # if FLG_FNAME == 1
    fName = ''  # ends when a byte with value 0 is read
    
    # if FLG_FCOMMENT == 1
    fComment = ''   # ends when a byte with value 0 is read
        
    # if FLG_HCRC == 1
    HCRC = []
        
        
    
    def read(self, f):
        ''' reads and processes the Huffman header from file. Returns 0 if no error, -1 otherwise '''

        # ID 1 and 2: fixed values
        self.ID1 = f.read(1)[0]  
        if self.ID1 != 0x1f: return -1 # error in the header
            
        self.ID2 = f.read(1)[0]
        if self.ID2 != 0x8b: return -1 # error in the header
        
        # CM - Compression Method: must be the value 8 for deflate
        self.CM = f.read(1)[0]
        if self.CM != 0x08: return -1 # error in the header
                    
        # Flags
        self.FLG = f.read(1)[0]
        
        # MTIME
        self.MTIME = [0]*self.lenMTIME
        self.mTime = 0
        for i in range(self.lenMTIME):
            self.MTIME[i] = f.read(1)[0]
            self.mTime += self.MTIME[i] << (8 * i)                 
                        
        # XFL (not processed...)
        self.XFL = f.read(1)[0]
        
        # OS (not processed...)
        self.OS = f.read(1)[0]
        
        # --- Check Flags
        self.FLG_FTEXT = self.FLG & 0x01
        self.FLG_FHCRC = (self.FLG & 0x02) >> 1
        self.FLG_FEXTRA = (self.FLG & 0x04) >> 2
        self.FLG_FNAME = (self.FLG & 0x08) >> 3
        self.FLG_FCOMMENT = (self.FLG & 0x10) >> 4
                    
        # FLG_EXTRA
        if self.FLG_FEXTRA == 1:
            # read 2 bytes XLEN + XLEN bytes de extra field
            # 1st byte: LSB, 2nd: MSB
            self.XLEN = [0]*self.lenXLEN
            self.XLEN[0] = f.read(1)[0]
            self.XLEN[1] = f.read(1)[0]
            self.xlen = self.XLEN[1] << 8 + self.XLEN[0]
            
            # read extraField and ignore its values
            self.extraField = f.read(self.xlen)
        
        def read_str_until_0(f):
            s = ''
            while True:
                c = f.read(1)[0]
                if c == 0: 
                    return s
                s += chr(c)
        
        # FLG_FNAME
        if self.FLG_FNAME == 1:
            self.fName = read_str_until_0(f)
        
        # FLG_FCOMMENT
        if self.FLG_FCOMMENT == 1:
            self.fComment = read_str_until_0(f)
        
        # FLG_FHCRC (not processed...)
        if self.FLG_FHCRC == 1:
            self.HCRC = f.read(2)
            
        return 0
            



class GZIP:
    ''' class for GZIP decompressing file (if compressed with deflate) '''

    gzh = None
    gzFile = ''
    fileSize = origFileSize = -1
    numBlocks = 0
    f = None
    

    bits_buffer = 0
    available_bits = 0        

    
    def __init__(self, filename):
        self.gzFile = filename
        self.f = open(filename, 'rb')
        self.f.seek(0,2)
        self.fileSize = self.f.tell()
        self.f.seek(0)

        
    
    #EX 4 e 5
    def comprimentos(self, bloco, H_tree):
        
        
        H_lens = []
        
        while len(H_lens) < bloco:
            
            H_tree.resetCurNode()
            
            val = -2
            while val < 0:
                bit = self.readBits(1)
                val = H_tree.nextNode(str(bit))
                
            if val <= 15:
                H_lens.append(val)
            elif val == 16:
                repeat = 3 + self.readBits(2)
                ultimo = H_lens[-1]
                for i in range(repeat):
                    H_lens.append(ultimo)
            elif val == 17:
                repeat = 3 + self.readBits(3)
                for i in range(repeat):
                    H_lens.append(0)
            elif val == 18:
                repeat = 11 + self.readBits(7)
                for i in range(repeat):
                    H_lens.append(0)
                    
        return H_lens
    
    #EX 3 e 6
    def huffmanCodes(self, lenghts):
        
        code = 0
        
        Max_Bits = max(lenghts)
        next_code = [0 for i in range(Max_Bits + 1)]
        
        bl_count = [0 for i in range(Max_Bits + 1)]
        contador = Counter(lenghts)
        
        
        for elemento in contador:
            if(elemento in lenghts):
                bl_count[elemento] = contador[elemento]
        
        bl_count[0] = 0
        
        for bits in range(1, Max_Bits + 1):
            code = (code + bl_count[bits - 1] ) << 1 
            next_code[bits] = code
            
            
        values = [0 for i in range(len(lenghts))]    
        for n in range(len(lenghts)):
            lenght = lenghts[n]
            if(lenght != 0):
                values[n] = next_code[lenght]
                next_code[lenght]+=1
        
        
        for i in range(len(values)):
           if(lenghts[i] == 0):
               values[i] = '0'
               continue
           values[i] = str(bin(values[i])[2:]).zfill(lenghts[i])
        
        return values
        
    #Ex 7
    
    def deflate(self, H_lit_comp_tree, H_dist_tree):
        array = []
        i = 0
        while(True):
            pos_lit_comp = -2
            H_lit_comp_tree.resetCurNode()   
            while pos_lit_comp == -2:
                K = str(self.readBits(1))
                pos_lit_comp = H_lit_comp_tree.nextNode(K)
    
            if pos_lit_comp < 256:
                array.append(pos_lit_comp)
                i+=1
                pass
            elif pos_lit_comp > 256:
                lengths =  pos_lit_comp - 254
                if pos_lit_comp < 265:
                    lengths = pos_lit_comp - 254
                elif pos_lit_comp == 265:
                    lengths = 11 + self.readBits(1)
                elif pos_lit_comp == 266:
                    lengths = 13 + self.readBits(1)
                elif pos_lit_comp == 267:
                    lengths = 15 + self.readBits(1)
                elif pos_lit_comp == 268:
                    lengths = 17 + self.readBits(1)
                elif pos_lit_comp == 269:
                    lengths = 19 + self.readBits(2)
                elif pos_lit_comp == 270:
                    lengths = 23 + self.readBits(2)
                elif pos_lit_comp == 271:
                    lengths = 27 + self.readBits(2)
                elif pos_lit_comp == 272:
                    lengths = 31 + self.readBits(2)
                elif pos_lit_comp == 273:
                    lengths = 35 + self.readBits(3)
                elif pos_lit_comp == 274:
                    lengths = 43 + self.readBits(3)
                elif pos_lit_comp == 275:
                    lengths = 51 + self.readBits(3)
                elif pos_lit_comp == 276:
                    lengths = 59 + self.readBits(3)
                elif pos_lit_comp == 277:
                    lengths = 67 + self.readBits(4)
                elif pos_lit_comp == 278:
                    lengths = 83 + self.readBits(4)
                elif pos_lit_comp == 279:
                    lengths = 99 + self.readBits(4)
                elif pos_lit_comp == 280:
                    lengths = 115 + self.readBits(4)
                elif pos_lit_comp == 281:
                    lengths = 131 + self.readBits(5)
                elif pos_lit_comp == 282:
                    lengths = 163 + self.readBits(5)
                elif pos_lit_comp == 283:
                    lengths = 195 + self.readBits(5)
                elif pos_lit_comp == 284:
                    lengths = 227 + self.readBits(5)
                elif pos_lit_comp == 285:
                    lengths = 258
     
     
                dist = -2
                H_dist_tree.resetCurNode()
                while dist == -2:
                    j = str(self.readBits(1))
                    dist = H_dist_tree.nextNode(j)
				
                if dist >= 0 and dist < 4:
                    dist +=1
                elif dist == 4: 
                    dist = 5 + self.readBits(1) 
                elif dist == 5: 
                    dist = 7 + self.readBits(1) 
     
                elif dist == 6: 
                    dist = 9 + self.readBits(2) 
                elif dist == 7: 
                    dist = 13 + self.readBits(2) 
     
                elif dist == 8:
                    dist = 17 + self.readBits(3) 
                elif dist == 9:
                    dist = 25 + self.readBits(3) 
     
                elif dist == 10: 
                    dist = 33 + self.readBits(4) 
                elif dist == 11: 
                    dist = 49 + self.readBits(4) 
     
                elif dist == 12: 
                    dist = 65 + self.readBits(5) 
                elif dist == 13: 
                    dist = 97 + self.readBits(5) 
     
                elif dist == 14: 
                    dist = 129 + self.readBits(6) 
                elif dist == 15: 
                    dist = 193 + self.readBits(6) 
     
                elif dist == 16:
                    dist = 257 + self.readBits(7) 
                elif dist == 17:
                    dist = 385 + self.readBits(7) 
     
                elif dist == 18: 
                    dist = 513 + self.readBits(8) 
                elif dist == 19: 
                    dist = 769 + self.readBits(8) 
     
                elif dist == 20: 
                    dist = 1025 + self.readBits(9) 
                elif dist == 21: 
                    dist = 1537 + self.readBits(9) 
     
                elif dist == 22: 
                    dist = 2049 + self.readBits(10) 
                elif dist == 23: 
                    dist = 3073 + self.readBits(10) 
     
                elif dist == 24:
                    dist = 4097 + self.readBits(11) 
                elif dist == 25:
                    dist = 6145 + self.readBits(11) 
     
                elif dist == 26: 
                    dist = 8193 + self.readBits(12) 
                elif dist == 27: 
                    dist = 12289 + self.readBits(12) 
     
                elif dist == 28: 
                    dist = 16385 + self.readBits(13) 
                elif dist == 29: 
                    dist = 24577 + self.readBits(13) 


                for a in range(lengths):	
                    array.append(array[i-dist+a])
					
                i+=lengths

	
            elif pos_lit_comp == 256:
                break
        return (array) 
    
    #Ex 8
    
    def escreveFicheiro(self, fileName, arrayDeflate):
        
        file = open(fileName, 'wb')
        bArray = bytearray(arrayDeflate)
        
        file.write(bArray)
        
        file.close()
        
    def decompress(self):
        ''' main function for decompressing the gzip file with deflate algorithm '''
        
        numBlocks = 0

        # get original file size: size of file before compression
        origFileSize = self.getOrigFileSize()
        print(origFileSize)
        
        # read GZIP header
        error = self.getHeader()
        if error != 0:
            print('Formato invalido!')
            return
        
        # show filename read from GZIP header
        print(self.gzh.fName)
        
        
        # MAIN LOOP - decode block by block
        BFINAL = 0    
        while not BFINAL == 1:    
            
            BFINAL = self.readBits(1)
                            
            BTYPE = self.readBits(2)                    
            if BTYPE != 2:
                print('Error: Block %d not coded with Huffman Dynamic coding' % (numBlocks+1))
                return
            
                                    
            #---+STUDENTS --- ADD CODE HERE
            # 
            # 
            
            
            #---------EX 1----------
            HLIT = self.readBits(5)
            HDIST = self.readBits(5)
            HCLEN = self.readBits(4)
            
            HCLEN += 4
            HLIT += 257
            HDIST += 1
            #-----------------------
            
            #---------EX 2--------------
            cLens = [0 for i in range(19)]
            
            ordem =[16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]
                
            
            for i in range(HCLEN):
                lerBits = self.readBits(3)
                cLens[ordem[i]] = lerBits
            #-----------------------------   
            
            #----------EX 3---------------
            codesHCLEN = self.huffmanCodes(cLens)
            #-----------------------------                  
            
            #----------EX 4--------------------
            huffTree = HuffmanTree()
           
            for i in range(len(cLens)):
                if cLens[i] > 0:
                    huffTree.addNode(codesHCLEN[i], i)
                   

 
            HLIT_lens = self.comprimentos(HLIT, huffTree)
            HDIST_lens = self.comprimentos(HDIST, huffTree)
            #--------------------------------------------
               
            #------------EX 5----------------------------
            HLIT_Codes = self.huffmanCodes(HLIT_lens)
            print('<----------EXERCICIO 5------------>')
            print(HLIT_Codes)
            #--------------------------------------------
            
            #-------------EX 6--------------------------
            HDIST_Codes = self.huffmanCodes(HDIST_lens)
            print('<----------EXERCICIO 6------------>')
            print(HDIST_Codes)
            #------------------------------------------
            
            #-------------EX 7-----------------------------
            huffTree_HLIT = HuffmanTree()
            
            huffTree_HDIST = HuffmanTree()
            
            for i in range(len(HLIT_lens)):
                if HLIT_lens[i] > 0:
                    huffTree_HLIT.addNode(HLIT_Codes[i], i)
            
            for i in range(len(HDIST_lens)):
                if HDIST_lens[i] > 0:
                    huffTree_HDIST.addNode(HDIST_Codes[i], i)
                        
                    
            arrayDeflate = self.deflate(huffTree_HLIT, huffTree_HDIST)
            
            #----------------------------------------------------------
            
            #-------------EX 8------------------------------------------
            
            self.escreveFicheiro('FAQ',arrayDeflate)
           
            #--------------------------------------------------
            # update number of blocks read
            numBlocks += 1
        

        
        # close file            
        
        self.f.close()    
        print("End: %d block(s) analyzed." % numBlocks)
    
    
    def getOrigFileSize(self):
        ''' reads file size of original file (before compression) - ISIZE '''
        
        # saves current position of file pointer
        fp = self.f.tell()
        
        # jumps to end-4 position
        self.f.seek(self.fileSize-4)
        
        # reads the last 4 bytes (LITTLE ENDIAN)
        sz = 0
        for i in range(4): 
            sz += self.f.read(1)[0] << (8*i)
        
        # restores file pointer to its original position
        self.f.seek(fp)
        
        return sz        
    

    
    def getHeader(self):  
        ''' reads GZIP header'''

        self.gzh = GZIPHeader()
        header_error = self.gzh.read(self.f)
        return header_error
        

    def readBits(self, n, keep=False):
        ''' reads n bits from bits_buffer. if keep = True, leaves bits in the buffer for future accesses '''

        while n > self.available_bits:
            self.bits_buffer = self.f.read(1)[0] << self.available_bits | self.bits_buffer
            self.available_bits += 8
        
        mask = (2**n)-1
        value = self.bits_buffer & mask

        if not keep:
            self.bits_buffer >>= n
            self.available_bits -= n

        return value

    


if __name__ == '__main__':

    # gets filename from command line if provided
    fileName = "FAQ.txt.gz"
    if len(sys.argv) > 1:
        fileName = sys.argv[1]            

    # decompress file
    gz = GZIP(fileName)
    gz.decompress()
    
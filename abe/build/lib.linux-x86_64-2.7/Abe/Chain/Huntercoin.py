# Copyright(C) 2014 by Abe developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/agpl.html>.

import json
import sys
from .Sha256NmcAuxPowChain import Sha256NmcAuxPowChain
from . import SCRIPT_TYPE_UNKNOWN
from ..deserialize import opcodes
from .. import deserialize, BCDataStream, util

class Huntercoin(Sha256NmcAuxPowChain):
    """
    Huntercoin represents name operations in transaction output scripts.
    """
    def __init__(chain, **kwargs):
        chain.name = 'Huntercoin'
        chain.code3 = 'HUC'
        chain.address_version = '\x28'
        chain.magic = '\xf9\xbe\xb4\xd9'
        Sha256NmcAuxPowChain.__init__(chain, **kwargs)

    _drops = (opcodes.OP_NOP, opcodes.OP_DROP, opcodes.OP_2DROP)
    
    def getNameTx(chain,pubkey):
        result = {}
        result['name'] = ""
        result['msg'] = ""
        result['color'] = None
        #print("$$$$$$$$$$$$$$$$$$ GET NAME TX $$$$$$$$$$$$$$$$$$$$$$")
        #print(pubkey.encode('hex'))
        
        ds = util.str_to_ds(pubkey)
        
        firstByte = ord(ds.read_bytes(1))
        
        #if (firstByte > 83 and firstByte < 97):
        #    print(firstByte)
        #    sys.exit()
        
        if (firstByte == 83 or firstByte == 82):
            print("~~~~~~~~~ NAME OP")
            result['name'] = ds.read_bytes(ord(ds.read_bytes(1)))
            print("NAME: " + str(result['name']))
            
            if (firstByte == 82):
                result['type'] = 'name_firstupdate'
                byte = ord(ds.read_bytes(1))
                if (byte > opcodes.OP_0 and byte < opcodes.OP_PUSHDATA1):
                    result['rand'] = ds.read_bytes(byte)
                elif byte == opcodes.OP_PUSHDATA1:
                    result['rand'] =  ds.read_bytes(ord(ds.read_bytes(1)))
                elif byte == opcodes.OP_PUSHDATA2:
                    result['rand'] =  ds.read_bytes(ds.read_uint16())
                elif byte == opcodes.OP_PUSHDATA4:
                    result['rand'] =  ds.read_bytes(ds.read_uint32())
                #result['rand'] = ds.read_bytes(ord(ds.read_bytes(1)))
            elif (firstByte == 83):
            	result['type'] = 'name_update'
            
            print("TYPE: " + str(result['type']))
            	
            if (firstByte == 82 and result['rand'][:1] == "{"): 
                print("RAND TO JSON")
                result['json'] = result['rand']
                result['rand'] = ""
            else:
                byte = ord(ds.read_bytes(1))
                print("BYTE: " + str(byte))
                if (byte > opcodes.OP_0 and byte < opcodes.OP_PUSHDATA1):
                    result['json'] = ds.read_bytes(byte)
                elif byte == opcodes.OP_PUSHDATA1:
                    result['json'] =  ds.read_bytes(ord(ds.read_bytes(1)))
                elif byte == opcodes.OP_PUSHDATA2:
                    result['json'] =  ds.read_bytes(ds.read_uint16())
                elif byte == opcodes.OP_PUSHDATA4:
                    result['json'] =  ds.read_bytes(ds.read_uint32())

            result['json'] = result['json'].replace("\\'","'")
            result['json'] = result['json'].replace("\r\n","")
            #print(result['json'])    
            #js = json.loads(result['json'])
            try:
                js = json.loads(unicode(result['json'], "ISO-8859-1"))
                for key in js.keys():
                    if (key == "msg"):
                        result['msg'] = js['msg']
                    if (key == "color"):
                        result['color'] = js['color'] 
            except ValueError:
                print("JSON ERROR")
                #sys.exit()
     #    	    for key2 in js[key].keys():
     #    	        print(key2)
     #    	        print js[key][key2]
     
        return result
    
    def parse_decoded_txout_script(chain, decoded):
        #print("############## HUNTERCOIN PARSE_DECODED_TXOUT_SCRIPT ##############")
        start = 0
        pushed = 0
        # Tolerate (but ignore for now) name operations.
        for i in xrange(len(decoded)):
            opcode = decoded[i][0]
            if decoded[i][1] is not None or \
                    opcode == opcodes.OP_0 or \
                    opcode == opcodes.OP_1NEGATE or \
                    (opcode >= opcodes.OP_1 and opcode <= opcodes.OP_16):
                pushed += 1
            elif opcode in chain._drops:
                to_drop = chain._drops.index(opcode)
                if pushed < to_drop:
                    break
                pushed -= to_drop
                start = i + 1
            else:
                return Sha256NmcAuxPowChain.parse_decoded_txout_script(chain, decoded[start:])

        return SCRIPT_TYPE_UNKNOWN, decoded


    datadir_conf_file_name = "huntercoin.conf"
    datadir_rpcport = 8399

import snap7
import ctypes
import re
import struct
import logging

logger = logging.getLogger(__name__)

class LogoMulti(snap7.logo.Logo):
    def read_multi(self, vm_addresses: list[str]):
        """Reads from VM addresses of Siemens Logo. Examples: read("V40") / read("VW64") / read("V10.2")

        Args:
            vm_addresses: of Logo memory (e.g. V30.1, VW32, V24)

        Returns:
            integer
        """
        size = len(vm_addresses)
        data_items = (snap7.types.S7DataItem * size)()

        for i in range(size):
            data_items[i].Area = ctypes.c_int32(snap7.types.Areas.DB)
            data_items[i].DBNumber = ctypes.c_int32(1)
            data_items[i].Result = ctypes.c_int32(0)
            start = 0
            logger.debug(f"read, vm_address:{vm_addresses[i]}")
            if re.match(r"V[0-9]{1,4}\.[0-7]", vm_addresses[i]):
                # bit value
                logger.info(f"read, Bit address: {vm_addresses[i]}")
                address = vm_addresses[i][1:].split(".")
                # transform string to int
                address_byte = int(address[0])
                address_bit = int(address[1])
                start = (address_byte * 8) + address_bit
                wordlen = snap7.types.WordLen.Bit
            elif re.match("V[0-9]+", vm_addresses[i]):
                # byte value
                logger.info(f"Byte address: {vm_addresses[i]}")
                start = int(vm_addresses[i][1:])
                wordlen = snap7.types.WordLen.Byte
            elif re.match("VW[0-9]+", vm_addresses[i]):
                # byte value
                logger.info(f"Word address: {vm_addresses[i]}")
                start = int(vm_addresses[i][2:])
                wordlen = snap7.types.WordLen.Word
            elif re.match("VD[0-9]+", vm_addresses[i]):
                # byte value
                logger.info(f"DWord address: {vm_addresses[i]}")
                start = int(vm_addresses[i][2:])
                wordlen = snap7.types.WordLen.DWord
            else:
                logger.info("Unknown address format")
                return 0

            data_items[i].Start = ctypes.c_int32(start)
            data_items[i].WordLen = ctypes.c_int32(wordlen)
            data_items[i].Amount = snap7.types.wordlen_to_ctypes[wordlen.value]

            # create the buffer
            buffer = ctypes.create_string_buffer(data_items[i].Amount)

            # cast the pointer to the buffer to the required type
            pBuffer = ctypes.cast(ctypes.pointer(buffer),
                                ctypes.POINTER(ctypes.c_uint8))
            data_items[i].pData = pBuffer

        logger.debug(f"start:{start}, wordlen:{wordlen.name}={wordlen.value}, data-length:{len(data)}")

        result = self.library.Cli_ReadMultiVars(
            self.pointer,
            ctypes.byref(data_items),
            ctypes.c_int32(len(data_items))
        )

        # result = self.library.Cli_ReadArea(self.pointer, area.value, db_number, start,
        #                                    size, wordlen.value, byref(data))
        snap7.common.check_error(result, context="client")

        result_values = []

        for di in data_items:
            snap7.common.check_error(di.Result)
            if di.WordLen == snap7.types.WordLen.Bit:
                result_values.append(di.pData[0])
            if di.WordLen == snap7.types.WordLen.Byte:
                result_values.append(struct.unpack_from(">B", di.pData)[0])
            if di.WordLen == snap7.types.WordLen.Word:
                result_values.append(struct.unpack_from(">h", di.pData)[0])
            if di.WordLen == snap7.types.WordLen.DWord:
                result_values.append(struct.unpack_from(">l", di.pData)[0])

        return result_values

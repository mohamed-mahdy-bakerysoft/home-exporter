import snap7
import ctypes
import re
import logging

logger = logging.getLogger(__name__)

class LogoMulti(snap7.logo.Logo):
    def _data_items(self, vm_addresses: list[str]) -> list[snap7.types.S7DataItem]:
        size = len(vm_addresses)
        data_items = (snap7.types.S7DataItem * size)()

        for i in range(size):
            data_items[i].Area = ctypes.c_int32(snap7.types.Areas.DB.value)
            data_items[i].DBNumber = ctypes.c_int32(1)
            data_items[i].Result = ctypes.c_int32(0)
            data_items[i].VMAddress = vm_addresses[i]
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
            data_items[i].Amount = ctypes.c_int32(1)
            data_items[i].WordLen = ctypes.c_int32(wordlen.value)

            # create the buffer
            buffer = ctypes.create_string_buffer(data_items[i].Amount)

            # cast the pointer to the buffer to the required type
            pBuffer = ctypes.cast(ctypes.pointer(buffer),
                                ctypes.POINTER(ctypes.c_uint8))
            data_items[i].pData = pBuffer

        return data_items

    def _read_multi(
        self,
        data_items: list[snap7.types.S7DataItem]
    ) -> list[snap7.types.S7DataItem]:
        """Reads from VM addresses of Siemens Logo.
        Examples: read("V40") / read("VW64") / read("V10.2")

        Args:
            vm_addresses: of Logo memory (e.g. V30.1, VW32, V24)

        Returns:
            integer
        """
        result = self.library.Cli_ReadMultiVars(
            self.pointer,
            ctypes.byref(data_items),
            ctypes.c_int32(len(data_items))
        )

        snap7.common.check_error(result, context="client")

        return data_items

    def _data_results(self, data_items: list[snap7.types.S7DataItem]) -> dict:
        result_values = []
        data = 0
        for data_item in data_items:
            snap7.common.check_error(data_item.Result)
            if data_item.WordLen == snap7.types.WordLen.Bit.value:
                data = snap7.util.get_bool(data_item.pData, 0)
            elif data_item.WordLen == snap7.types.WordLen.Byte.value:
                # data = snap7.util.get_byte(data_item.pData, 0)
                data = data_item.pData
            elif data_item.WordLen == snap7.types.WordLen.Word.value:
                data = snap7.util.get_word(data_item.pData, 0)
            elif data_item.WordLen == snap7.types.WordLen.DWord.value:
                data = snap7.util.get_dword(data_item.pData, 0)

            result_values.append((str(data_item.Start), data))

        return dict(result_values)

    def read_multi(self, vm_addresses: list[str]) -> dict:
        data_items = self._data_items(vm_addresses)
        return self._data_results(self._read_multi(data_items))

    def byte_to_bool(self, byte) -> dict:
        result = []
        for i in range(8):
            result.append(snap7.util.get_bool(byte, 0, i))
        return result

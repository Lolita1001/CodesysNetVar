from utils.exeptions import PacketWrongLen


class Rcv:
    __slots__ = (
        "client_address",
        "_constant",
        "id_list",
        "n_package_in_list",
        "count_variable_in_packet",
        "count_bytes",
        "n_sends",
        "data_raw",
    )

    def __init__(self, message: bytes, client: tuple[str, int]) -> None:
        """
        class receive data, parse data and check len of received data
        
        0000000000000000
                        ^ 8 byte - unknown constant
                         0000
                             ^ 2 byte - List ID in int format
                              0000
                                  ^ 2 byte - Number of packets in unpacked data in int format
                                   0000
                                       ^ 2 byte - Number of variables in the package in int format
                                        0000
                                            ^ 2 byte - all package length in int format
                                             00000000
                                                     ^ 4 byte - Common Packet number in dint format
                                                      000000...
                                                                ^ X byte - Data


        :param message: raw bytes received data
        :param client: senders address
        """
        self.client_address = client
        self._constant = message[:8]
        self.id_list = int.from_bytes(message[8:10], "little")
        self.n_package_in_list = int.from_bytes(message[10:12], "little")
        self.count_variable_in_packet = int.from_bytes(message[12:14], "little")
        self.count_bytes = int.from_bytes(message[14:16], "little")
        self.n_sends = int.from_bytes(message[16:20], "little")
        self.data_raw = message[20:]
        self.check_packet(message)

    def check_packet(self, message: bytes) -> None:
        if len(message) != self.count_bytes:
            raise PacketWrongLen("The receive packet has wrong len")

    def print(self) -> str:
        text = f"""Unknown data {self._constant!r}
ID list: {self.id_list!r}
Number of packets in unpacked data: {self.n_package_in_list!r}
Number of variables in the package: {self.count_variable_in_packet!r}
Package length: {self.count_bytes!r}
Common Packet number: {self.n_sends!r}
Data: {self.data_raw!r}
"""
        return text

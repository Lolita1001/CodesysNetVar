from utils.exeptions import PacketWrongLen


class Rcv:
    __slots__ = 'client_address', '_constant', 'id_list', 'n_package_in_list', \
                'count_variable_in_packet', 'count_bytes', 'n_sends', 'data_raw'

    def __init__(self, message, client):
        """
        class receive data, parse data and check len of received data
        :param message: raw bytes received data
        :param client: senders address
        """
        self.client_address = client
        self._constant = message[:8]
        self.id_list = int.from_bytes(message[8:10], 'little')
        self.n_package_in_list = int.from_bytes(message[10:12], 'little')
        self.count_variable_in_packet = int.from_bytes(message[12:14], 'little')
        self.count_bytes = int.from_bytes(message[14:16], 'little')
        self.n_sends = int.from_bytes(message[16:20], 'little')
        self.data_raw = message[20:]
        self.check_packet(message)

    def check_packet(self, message) -> None:
        if len(message) != self.count_bytes:
            raise PacketWrongLen('The receive packet has wrong len')

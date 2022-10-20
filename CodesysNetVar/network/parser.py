from exeptions import PacketWrongLen


class Rcv:
    def __init__(self, message, client):
        """
        class receive data, parse data and check len of received data
        :param message: raw bytes received data
        :param client: senders address
        """
        self.message_raw = message
        self.client_address = client
        self._constant = self.message_raw[:8]
        self.id_list = int.from_bytes(self.message_raw[8:10], 'little')
        self.n_package_in_list = int.from_bytes(self.message_raw[10:12], 'little')
        self.count_variable_in_packet = int.from_bytes(self.message_raw[12:14], 'little')
        self.count_bytes = int.from_bytes(self.message_raw[14:16], 'little')
        self.n_sends = int.from_bytes(self.message_raw[16:20], 'little')
        self.data_raw = self.message_raw[20:]
        self.check_packet()

    def check_packet(self):
        if len(self.message_raw) != self.count_bytes:
            raise PacketWrongLen('The receive packet has wrong len')

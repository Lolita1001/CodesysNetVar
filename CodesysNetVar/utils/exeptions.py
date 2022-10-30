class ListIdMustBeUniq(AttributeError):
    """List id in NVL settings must be uniq"""


class IpAndPortWrong(AttributeError):
    """IP address and port must be equal with NVL"""


class AcknowledgeMustBeFalse(AttributeError):
    """Attribute "Acknowledge" must be False"""


class ChecksumMustBeFalse(AttributeError):
    """Attribute "Checksum" must be False"""


class PacketWrongLen(ValueError):
    """The received packet have wrong len"""


class UnsupportedType(TypeError):
    """Data type is not supported"""


class NodeNotFound(ValueError):
    """Node not found"""


class DataWrongLen(ValueError):
    """The data has different length for this Data type"""


class NVLFileNotFound(FileNotFoundError):
    """NVL file not found"""


class OutOfRange(ValueError):
    """Values of this data type are out of range"""

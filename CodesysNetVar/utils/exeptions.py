class ListIdMustBeUniq(AttributeError):
    """List id in NVL settings must be uniq"""


class IpAndPortWrong(AttributeError):
    """IP address and port must be equal with NVL"""


class AcknowledgeMustBeUniq(AttributeError):
    """Attribute "Acknowledge" must be False"""


class ChecksumMustBeUniq(AttributeError):
    """Attribute "Checksum" must be False"""


class PacketWrongLen(ValueError):
    """The received packet have wrong len"""


class UnsupportedType(TypeError):
    """Data type is not supported"""

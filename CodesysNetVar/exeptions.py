class ListIdMustBeUniq(AttributeError):
    """List id in NVL settings must be uniq"""


class AcknowledgeMustBeUniq(AttributeError):
    """Attribute "Acknowledge" must be False"""


class ChecksumMustBeUniq(AttributeError):
    """Attribute "Checksum" must be False"""


class PacketWrongLen(ValueError):
    """The received packet have wrong len"""

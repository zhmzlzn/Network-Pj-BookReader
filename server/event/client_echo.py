from protocol.message_type import MessageType
from protocol.secure_transmission.secure_channel import SecureChannel

def run(sc, parameters):
    sc.send(MessageType.server_echo, parameters)
import server.event.login
import server.event.comment
import server.event.register
import server.event.bad
import server.event.client_echo
from protocol.message_type import MessageType

event_handler_map = {
    MessageType.login: login,
    MessageType.comment: comment,
    MessageType.register: register,
    MessageType.client_echo: client_echo,
    MessageType.bad: bad,
}

def handle_event(sc, event_type, parameters):
    event_handler_map[event_type].run(sc, parameters)

import server.event.login
import server.event.register
import server.event.send_list
import server.event.send_book
import server.event.comment
import server.event.client_echo
import server.event.bad
from protocol.message_type import MessageType

event_handler_map = {
    MessageType.login: login,
    MessageType.register: register,    
    MessageType.require_list: send_list,
    MessageType.download: send_book,
    MessageType.comment: comment,
    MessageType.client_echo: client_echo,
    MessageType.bad: bad,
}

def handle_event(sc, event_type, parameters):
    event_handler_map[event_type].run(sc, parameters)

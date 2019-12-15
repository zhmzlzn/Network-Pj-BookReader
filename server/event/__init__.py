import server.event.login
import server.event.register
import server.event.send_list
import server.event.send_book
import server.event.start_read
import server.event.pre_page
import server.event.nxt_page
import server.event.comment
import server.event.bad
from protocol.message_type import MessageType

event_handler_map = {
    MessageType.login: login,
    MessageType.register: register,    
    MessageType.require_list: send_list,
    MessageType.download: send_book,
    MessageType.start_read: start_read,
    MessageType.pre_page: pre_page,
    MessageType.nxt_page: nxt_page,
    MessageType.comment: comment,
    MessageType.bad: bad,
}

def handle_event(sc, event_type, parameters):
    event_handler_map[event_type].run(sc, parameters)

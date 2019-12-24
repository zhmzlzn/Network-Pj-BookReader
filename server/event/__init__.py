import server.event.login
import server.event.register
import server.event.send_list
import server.event.send_book
import server.event.start_read
import server.event.send_page
import server.event.send_chapter
import server.event.update_bookmark
from protocol.message_type import MessageType

event_handler_map = {
    MessageType.login: login,
    MessageType.register: register,    
    MessageType.require_list: send_list,
    MessageType.download: send_book,
    MessageType.start_read: start_read,
    MessageType.require_page: send_page,
    MessageType.require_chapter: send_chapter,
    MessageType.update_bookmark: update_bookmark,
}

def handle_event(sc, event_type, parameters):
    event_handler_map[event_type].run(sc, parameters)
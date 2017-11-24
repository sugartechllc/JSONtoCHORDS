import socket
import _thread
import time
import sys
import json

"""
Capture wxflow datagrams in a queue and serve out to a consumer.

The JSON configuration file must contain at least:
{
    "listen_port": 5022
}

It is fine to include all of the configuration
needed by other modules (e.g. DecodeWxflow and ToChords).
"""

wxflow_msg_queue = []
wxflow_msg_queue_lock = _thread.allocate_lock()


def msg_capture(port):
    """Capture datagrams and place in a queue."""

    global wxflow_msg_queue
    global wxflow_msg_queue_lock
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    while True:
        try:
            jbytes, addr = sock.recvfrom(2000)
            wxflow_msg_queue_lock.acquire()
            wxflow_msg_queue.append(jbytes)
            wxflow_msg_queue_lock.release()
        except OSError as e:
            err_no = e.args[0]
            if err_no != 4:
                raise


def get_msgs():
    '''Return a list containing new messages. 
    
    If none are available, the list is empty.
    '''
    global wxflow_msg_queue
    global wxflow_msg_queue_lock
    
    msg_list = []
    wxflow_msg_queue_lock.acquire()
    for m in wxflow_msg_queue:
        msg_list.append(wxflow_msg_queue.pop(0).decode('UTF-8'))
    wxflow_msg_queue_lock.release()
    return msg_list


def startReader(port):
    """ Start the datagram reading thread."""
    
    _thread.start_new_thread(msg_capture, (port,))
    

#####################################################################
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print ("Usage:", sys.argv[0], 'config_file')
        sys.exit (1)
        
    config = json.loads(open(sys.argv[1]).read())
    
    startReader(port=config["listen_port"])
    
    while True:
        msgs = get_msgs()
        for m in msgs:
            print(m)



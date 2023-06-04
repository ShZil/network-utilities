from PacketSniffer import PacketSniffer


def log_packets():
    """
    The log_packets function is a simple wrapper for the PacketSniffer class as an analysis.
    It peeks inside the PacketSniffer class, and then iterates over each packet.
    The packets are then formatted as HTML and sent to a `popup`.
    """
    from gui.dialogs import popup
    packets = [str(packet.summary()) for packet in PacketSniffer()]
    packets = [packet.replace('>', '&gt;').replace('<', '&lt;').split('/') for packet in packets]
    packets = ['<span class="ip">['.join(layers) + ' ]</span>'*len(layers) for layers in packets]
    packets = [f"<tr><td><span>[ {packet}</td></tr>" for packet in packets]
    packets = '\n'.join(packets)
    packets = f"<table>{packets}</table>"
    popup("Packets", packets, info=True)


if __name__ == '__main__':
    print("This module contains the `log_packets` function,")
    print("i.e. the code of the Log Packets analysis.")

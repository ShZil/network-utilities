from PacketSniffer import PacketSniffer


def log_packets():
    from gui.dialogs import popup
    packets = [str(packet.summary()) for packet in PacketSniffer()]
    packets = ['</td><td>'.join(packet.replace('>', '&gt;').replace('<', '&lt;').split('/')) for packet in packets]
    packets = [f"<tr><td>{packet}</td></tr>" for packet in packets]
    packets = '\n'.join(packets)
    packets = f"<table>{packets}</table>"
    popup("Packets", packets, info=True)


if __name__ == '__main__':
    print("This module contains the `log_packets` function,")
    print("i.e. the code of the Log Packets analysis.")

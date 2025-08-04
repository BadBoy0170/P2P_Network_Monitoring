from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI

class SkyEyeKOMTopo(Topo):
    def build(self):
        # Root node (Coordinator)
        root = self.addHost('root')
        # Parent Coordinators
        p1 = self.addHost('p1')
        p2 = self.addHost('p2')
        # Peers
        peer1 = self.addHost('peer1')
        peer2 = self.addHost('peer2')
        # Links (hierarchical structure)
        self.addLink(root, p1)
        self.addLink(root, p2)
        self.addLink(p1, peer1)
        self.addLink(p2, peer2)

if __name__ == "__main__":
    topo = SkyEyeKOMTopo()
    net = Mininet(topo)
    net.start()
    CLI(net)
    net.stop()

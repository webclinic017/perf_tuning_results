import torch, timeit, sys
import torch.nn.functional as F
import functools as f
TIMES=500
x = torch.unsqueeze(torch.linspace(-1, 1, 100), dim=1 )
y = x.pow(2) +0.2*torch.rand(x.size())

class Net(torch.nn.Module):
    def __init__(self, nin, hidden, nout):
        super(Net, self).__init__()
        self.hidden = torch.nn.Linear(nin,hidden)
        self.out = torch.nn.Linear(hidden,nout)

    def forward(self,x):
        x = F.relu(self.hidden(x))
        x = self.out(x)
        return x

net = Net(1,10,1)
opt = torch.optim.SGD(net.parameters(), lr=0.5)
los = torch.nn.MSELoss()

def train():
    o = net(x)
    l = los(o,y)
    opt.zero_grad()
    l.backward()
    opt.step()

    #print(l.data.item())

if __name__ == "__main__":
    TIMES = int( sys.argv[1] )
    t = timeit.Timer( f.partial(train) ).timeit(TIMES)
    print("Python: {0:.5f}".format(t))

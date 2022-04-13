import torch
from torch import nn
from torch.autograd import Variable

class LSTM(nn.Module):

    def __init__(self, input_dim, hidden_dim, num_layers, output_dim):
        
        super(LSTM,self).__init__()

        self.hidden_dim = hidden_dim
        self.num_layers = num_layers


        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first = True)
            
        self.fc = nn.Linear(hidden_dim, output_dim)

        self.relu = nn.ReLU()
        

    def forward(self, x):

        h0 = Variable(torch.zeros(self.num_layers, x.shape[0], self.hidden_dim))
        c0 = Variable(torch.zeros(self.num_layers, x.shape[0],  self.hidden_dim))

        out, (hn,cn) = self.lstm(x, ( h0.detach(),c0.detach()) ) 
        hn = hn[-1]
        
        #out = self.relu(hn)
        out = self.fc(out[:, -1, :])
        
        return out
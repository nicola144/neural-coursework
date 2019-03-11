import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np
import sys
import seaborn as sns
import datetime

# Arguments
def ask():
    args = dict()

    args['n_inputs'] = int(input("Number of inputs: "))
    args['n_neurons'] = int(input("Number of hidden neurons: "))
    isnoise = input("Want noise? Return for yes")
    args['noise'] = True if isnoise == '' else False
    if(not (args['noise']) ):
        args['noise_val'] = 0.0
    return args

# Hyperparameters
EPOCHS = 500
learning_rate = 1e-4

# Model
class NN(nn.Module):

    def __init__(self, hidden_neurons):
        super(NN, self).__init__()
        self.fc1 = nn.Linear(2, hidden_neurons, True)
        self.fc2 = nn.Linear(hidden_neurons, 1, True)

    def forward(self, x):
        x = torch.sigmoid(self.fc1(x))
        x = self.fc2(x)
        return x

# Weight initialization
def weights_init(model):
    for m in model.modules():
        if isinstance(m, nn.Linear):
            # initialize the weight tensor, here we use a normal distribution
            m.weight.data.normal_(0, 1)

# Adding noise
def addnoise(data, args):
    data = np.asarray(data)
    noise_val = 0.25
    noise = np.random.normal(0, noise_val, data.shape)
    args['noise_val'] = noise_val
    newdata = data + noise
    return newdata, args

# Root mean squared error
def RMSELoss(yhat,y):
    return torch.sqrt(torch.mean((yhat-y)**2))

# Plotting dataset
def plot_data(data,labels):
    data = np.asarray(data)
    labels = np.asarray(labels)
    labels = labels.flatten()

    plt.figure(figsize=(12,8))
    plt.scatter(data[:,0], data[:,1], c=labels)
    plt.show()

if __name__ == "__main__":

    # Get settings
    args = ask()

    net = NN(hidden_neurons=args['n_neurons'])

    # Number of inputs (for each type)
    n = args['n_inputs']

    # Generate data
    data = [[0,0]] * n + [[0,1]] * n + [[1,0]] * n + [[1,1]] * n

    # add noise
    if(args['noise']):
        print("using noise")
        data,args = addnoise(data,args)

    # Generate labels
    labels = [[0]] * n + [[1]] * n + [[1]] * n + [[0]] * n

    plot_data(data,labels)

    inputs = list(map(lambda s: Variable(torch.Tensor([s])), data))
    targets = list(map(lambda s: Variable(torch.Tensor([s])), labels))

    criterion = nn.MSELoss()
    optimizer = optim.Adam(net.parameters(), lr=learning_rate)
    # criterion = RMSELoss
    # optimizer = optim.SGD(net.parameters(), lr=0.05)
    hold_loss=[]

    for epoch in range(0, EPOCHS):
        running_loss = 0.0
        for input, target in zip(inputs, targets):
            optimizer.zero_grad()   # zero the gradient buffers
            output = net(input)
            loss = criterion(output, target)
            running_loss += loss.data
            loss.backward()
            optimizer.step()    # Does the update
        hold_loss.append(running_loss)

    print("\nFinal results:")
    plt.plot(np.array(hold_loss))
    plt.savefig("./train_loss/train_loss_at_"+str(datetime.datetime.now())+"_model_("+str(args['n_inputs'])+','+str(args['n_neurons'])+','+str(args['noise_val'])+").png")
    plt.close()
    # Plotting decision boundary

    # For now testing with training set

    test_data = torch.FloatTensor(data)
    labels = np.asarray(labels)
    Y_test = labels.flatten()
    y_hat_test = net(test_data)
    y_hat_test_class = np.where(y_hat_test.detach().numpy()<0.5, 0, 1)
    test_accuracy = np.sum(Y_test.reshape(-1,1)==y_hat_test_class) / len(Y_test)
    print("Test Accuracy {:.2f}".format(test_accuracy))

    # Plot the decision boundary
    # Determine grid range in x and y directions
    x_min, x_max = test_data[:, 0].min()-0.1, test_data[:, 0].max()+0.1
    y_min, y_max = test_data[:, 1].min()-0.1, test_data[:, 1].max()+0.1

    # Set grid spacing parameter
    spacing = min(x_max - x_min, y_max - y_min) / 100

    # Create grid
    XX, YY = np.meshgrid(np.arange(x_min, x_max, spacing), np.arange(y_min, y_max, spacing))

    # Concatenate data to match input
    full_data = np.hstack((XX.ravel().reshape(-1,1), YY.ravel().reshape(-1,1)))

    # Pass data to predict method
    data_t = torch.FloatTensor(full_data)
    db_prob = net(data_t)

    clf = np.where(db_prob<0.5,0,1)

    Z = clf.reshape(XX.shape)

    plt.figure(figsize=(12,8))
    plt.contourf(XX, YY, Z, cmap=plt.cm.Accent, alpha=0.5)
    plt.scatter(test_data[:,0], test_data[:,1], c=Y_test, cmap=plt.cm.Accent)
    plt.savefig("./boundaries/decision_boundary_at_"+str(datetime.datetime.now())+"_model_("+str(args['n_inputs'])+','+str(args['n_neurons'])+','+str(args['noise_val'])+").png")
    plt.close()

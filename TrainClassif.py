
# coding: utf-8

# In[7]:

import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim as optim
import torch.utils.data
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import torchvision.models as models
from torch.autograd import Variable
import numpy as np
import random
from PIL import Image
from ipywidgets import FloatProgress
from IPython.display import display
from __future__ import print_function

from model import ModelDefinition
from dataset import ReadImages, collection


# Process the dataset :
# We have to compute the number of class, and the mean and std for image normalization

# Read the dataset and compute the mean and std dev :

# In[9]:

trainset = ReadImages.readImageswithPattern('/video/CLICIDE', lambda x:x.split('/')[-1].split('-')[0], openAll=True)


# In[11]:

print(trainset[0])


# In[12]:

m = collection.ComputeMean(trainset[:][0])
print("Mean : ", m)
#s = ComputeStdDev(imagesList, m)
#print("std dev : ", s)


# Define the network as class (from nn.Module) :

# Training

# In[138]:

#create the network
mymodel = Maxnet()


# In[143]:

#mymodel.cuda()
mymodel = best.train()
criterion = nn.loss.CrossEntropyLoss()
optimizer = optim.SGD(mymodel.parameters(), lr=0.0001, momentum=0.9)

#trainset, imagesList = readImages("CliList.txt")
#testset, imagesTest = readImages("CliListTest.txt")
#labels = open("CliConcept.txt").read().splitlines()

imageTransform = transforms.Compose( (transforms.Scale(300), transforms.RandomCrop(225), transforms.ToTensor(), transforms.Normalize(m,s)) )
testTransform = transforms.Compose( (transforms.Scale(225), transforms.ToTensor(), transforms.Normalize(m,s)))
batchSize = 64
bestScore = 0
for epoch in range(50): # loop over the dataset multiple times
    running_loss = 0.0
    for i in range(len(trainset)/batchSize):
        # get the inputs
        elIndex = [random.randrange(0, len(trainset)) for j in range(batchSize)]
        inputs = torch.Tensor(batchSize,3,225,225).cuda()
        for j in range(batchSize):
            inputs[j] = imageTransform(imagesList[elIndex[j]])
        inputs = Variable(inputs)
        lab = Variable(torch.LongTensor([labels.index(trainset[j].split('/')[-1].split('-')[0]) for j in elIndex]).cuda())
        #print(len(lab))
        # zero the parameter gradients
        optimizer.zero_grad()
        
        # forward + backward + optimize
        outputs = mymodel(inputs)
        loss = criterion(outputs, lab)
        loss.backward()
        optimizer.step()
        
        # print statistics
        running_loss += loss.data[0]
        if i % 10 == 9: # print every 10 mini-batches
            print('[%d, %5d] loss: %.3f' % (epoch+1, i+1, running_loss / 10))
            running_loss = 0.0
        if i % 50 == 49: #test every 20 mini-batches
            print('test :')
            mymodel = mymodel.eval()
            correct = 0
            tot = 0
            cpt = 0
            for j in range(len(testset)/batchSize):
                inp = torch.Tensor(batchSize,3,225,225).cuda()
                for k in range(batchSize):
                    inp[k] = testTransform(imagesTest[j*batchSize+k])
                    cpt += 1
                outputs = mymodel(Variable(inp))
                _, predicted = torch.max(outputs.data, 1)
                predicted = predicted.tolist()
                for k in range(batchSize):
                    if (testset[j*batchSize+k].split('/')[-1].split('-')[0] in labels):
                        correct += (predicted[k][0] == labels.index(testset[j*batchSize+k].split('/')[-1].split('-')[0]))
                        tot += 1
                        
            rest = len(testset)%batchSize
            inp = torch.Tensor(rest,3,225,225).cuda()
            for j in range(rest):
                inp[j] = testTransform(imagesTest[len(testset)-rest+j])
            outputs = mymodel(Variable(inp))
            _, predicted = torch.max(outputs.data, 1)
            predicted = predicted.tolist()
            for j in range(rest):
                if (testset[len(testset)-rest+j].split('/')[-1].split('-')[0] in labels):
                   correct += (predicted[j][0] == labels.index(testset[len(testset)-rest+j].split('/')[-1].split('-')[0]))
                   tot += 1
            print("Correct : ", correct, "/", tot)
            if (correct >= bestScore):
                best = mymodel
                bestScore = correct
                torch.save(best, "bestModel.ckpt")
            #else:
            #    mymodel = best
            torch.save(mymodel, "model-"+epoch+".ckpt")
            mymodel = mymodel.train()
            
print('Finished Training')

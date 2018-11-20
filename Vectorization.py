import math
import numpy as np
import time

import matplotlib.pyplot as plt

#------------------------
#system configuration

num_of_classes = 2 #1 for regression, n for classification
epoch = 1000
learningRate = np.array([0.1])
hidden_layers = [5, 5]

print("system configuration: epoch=",epoch,", hidden layers=",hidden_layers)

optimization_algorithm = 'adam' #gradient-descent or adam

#------------------------
#trainset

x = np.array( #xor dataset
	[ #bias, #x1, #x2
		[[1],[0],[0]], #instance 1
		[[1],[0],[1]], #instance 2
		[[1],[1],[0]], #instance 3
		[[1],[1],[1]]  #instace 4
	]
)

if num_of_classes > 1: #classification
	y = np.array(
		[
			[[1],[0]],
			[[0],[1]],
			[[0],[1]],
			[[1],[0]],
		]
	)
else: #regression
	y = np.array(
		[
			[0], #instance 1
			[1], #instance 2
			[1], #instance 3
			[0]  #instace 4
		]
	)

"""
#suppose that traindata stored in this file. each line refers to an instance.
#final item of an instance is label (y) whereas the other ones are features  (x)
#now, loading trainset from external resource is available for regression problems
from numpy import genfromtxt
dataset = genfromtxt('../xor.csv', delimiter=',')
features = dataset[:,0:dataset.shape[1]-1]
labels = dataset[:,dataset.shape[1]-1:]
bias = np.array([1]);
x = [0 for i in range(features.shape[0])]
for i in range(features.shape[0]):
	x[i] = np.array([np.append([1], features[i])]).T
y = [0 for i in range(labels.shape[0])]
for i in range(labels.shape[0]):
	if num_of_classes == 1: #regression
		y[i] = np.array([labels[i]]).T
	else:
		encoded = [0 for i in range(num_of_classes)]
		encoded[int(labels[i])] = 1
		y[i] = np.array([encoded]).T
x = np.array(x)
y = np.array(y)
"""
#print("features: ",x)
#print("target: ",y)
#------------------------

num_of_features = x.shape[1]-1 #minus 1 refers to bias
num_of_instances = x.shape[0]
num_of_layers = len(hidden_layers) + 2 #plus input layer and output layer

#------------------------
def initialize_weights(rows, columns):
	#lecture: https://www.coursera.org/learn/deep-neural-network/lecture/RwqYe/weight-initialization-for-deep-networks
	weights = np.random.randn(rows+1, columns) #standard normal distribution, +1 refers to bias unit
	weights = weights * np.sqrt(1/rows) #xavier initialization. this is good for tanh (http://proceedings.mlr.press/v9/glorot10a/glorot10a.pdf)
	#weights = weights * np.sqrt(2/rows) #this is good for relu (https://www.cv-foundation.org/openaccess/content_iccv_2015/papers/He_Delving_Deep_into_ICCV_2015_paper.pdf)
	#weights = weights * np.sqrt(6/(rows + columns)) #normalized initialization (same ref with xavier initialization)
	return weights

#weight initialization
w = [0 for i in range(num_of_layers-1)]

w[0] = initialize_weights(num_of_features, hidden_layers[0])

if len(hidden_layers) > 1:
	for i in range(len(hidden_layers) - 1):
		w[i+1] = initialize_weights(hidden_layers[i], hidden_layers[i+1])

w[num_of_layers-2] = initialize_weights(hidden_layers[len(hidden_layers) - 1], num_of_classes)

#print("initial weights: ", w)
#------------------------

def sigmoid(netinput):
	netoutput = np.ones((netinput.shape[0] + 1, 1)) 
	#ones because init values are same as bias unit
	#size of output is 1 plus input because of bias
	
	for i in range(netinput.shape[0]):
		netoutput[i+1] = 1/(1 + math.exp(-netinput[i][0]))
	return netoutput

def applyFeedForward(x, w):

	netoutput = [i for i in range(num_of_layers)]
	netinput = [i for i in range(num_of_layers)]

	netoutput[0] = x
	for i in range(num_of_layers - 1):
		netinput[i+1] = np.matmul(np.transpose(w[i]), netoutput[i])
		netoutput[i+1] = sigmoid(netinput[i+1])	
	
	netoutput[num_of_layers-1] = netoutput[num_of_layers-1][1:] #bias should not exist in output
	return netoutput

#------------------------

start_time = time.time()

def calculateCost():
	cost = 0
	for i in range(num_of_instances):
		nodes = applyFeedForward(x[i], w)
		predict = nodes[num_of_layers - 1]
		actual = y[i]
		
		cost = cost + sum(pow((actual - predict), 2)/2)
	
	cost = cost / num_of_instances
	return cost

#adam optimization parameters initialization
vdw = [0.0 for i in range(num_of_layers)]
sdw = [0.0 for i in range(num_of_layers)]
epsilon = np.array([pow(10, -8)])
beta1 = 0.9; beta2 = 0.999

J = [] #cost history
J.append(calculateCost()) #initial cost

for epoch in range(epoch):
	for i in range(num_of_instances):
		instance = x[i]
		nodes = applyFeedForward(instance, w)
		
		predict = nodes[num_of_layers - 1]
		actual = y[i]
		#print("predict: ",predict,", actual: ",actual)
		error = actual - predict
		#print("error: ",error)
		
		sigmas = [i for i in range(num_of_layers)] #error should not be reflected to input layer
		
		sigmas[num_of_layers - 1] = error
		for j in range(num_of_layers - 2, -1, -1):
			
			if sigmas[j + 1].shape[0] == 1:
				sigmas[j] = w[j] * sigmas[j + 1]
			else:
				if j == num_of_layers - 2: #output layer has no bias unit
					sigmas[j] = np.matmul(w[j], sigmas[j + 1])
				else: #otherwise remove bias unit from the following node because it is not connected from previous layer
					sigmas[j] = np.matmul(w[j], sigmas[j + 1][1:])
			
		#----------------------------------
		
		derivative_of_sigmoid = nodes * (np.array([1]) - nodes) #element wise multiplication and scalar multiplication
		sigmas = derivative_of_sigmoid * sigmas
		
		for j in range(num_of_layers - 1):
			
			if j == num_of_layers - 2: #outputlayer
				delta = nodes[j] * np.transpose(sigmas[j+1]) #no bias exist in output layer
			else:
				delta = nodes[j] * np.transpose(sigmas[j+1][1:])
			
			#-----------------------------------------------
			#optimization algorithm
			if optimization_algorithm == 'gradient-descent':
				w[j] = w[j] + learningRate * delta
			elif optimization_algorithm == 'adam':
				vdw[j] = beta1 * vdw[j] + (1 - beta1) * delta
				sdw[j] = beta2 * sdw[j] + (1 - beta2) * pow(delta, 2)
				
				vdw_corrected = vdw[j] / (1-pow(beta1, epoch+1))
				sdw_corrected = sdw[j] / (1-pow(beta2,epoch+1))
				
				w[j] = w[j] + learningRate * (vdw_corrected / (np.sqrt(sdw_corrected) + epsilon))
			##optimization algorithm end	
	J.append(calculateCost())
	
#training end

x_axis = [i for i in range(len(J))]
plt.plot(x_axis, J, c='blue', label=optimization_algorithm)
plt.xlabel('epoch')
plt.ylabel('error')
plt.show()

#---------------------
print("--- execution for vectorization lasts %s seconds ---" % (time.time() - start_time))

#print("final weights: ",w)

for i in range(num_of_instances):
	nodes = applyFeedForward(x[i], w)
	predict = nodes[num_of_layers - 1]
	actual = y[i]
	print(np.transpose(x[i][1:])," -> actual: ", np.transpose(actual)[0],", predict: ", np.transpose(predict)[0])

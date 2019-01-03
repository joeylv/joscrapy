
    # import BatchNormalization
    from keras.layers.normalization import BatchNormalization
    
    # instantiate model
    model = Sequential()
    
    # we can think of this chunk as the input layer
    model.add(Dense(64, input_dim=14, init="uniform"))
    model.add(BatchNormalization())
    model.add(Activation("tanh"))
    model.add(Dropout(0.5))
    
    # we can think of this chunk as the hidden layer    
    model.add(Dense(64, init="uniform"))
    model.add(BatchNormalization())
    model.add(Activation("tanh"))
    model.add(Dropout(0.5))
    
    # we can think of this chunk as the output layer
    model.add(Dense(2, init="uniform"))
    model.add(BatchNormalization())
    model.add(Activation("softmax"))
    
    # setting up the optimization of our weights 
    sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss="binary_crossentropy", optimizer=sgd)
    
    # running the fitting
    model.fit(X_train, y_train, nb_epoch=20, batch_size=16, show_accuracy=True, validation_split=0.2, verbose = 2)


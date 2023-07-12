class CFG:
    # data
    sr = 16000
    n_labels = 50
    duration = 5000  # ms
    batch_size = 20
    shift_pct = 0.4
    train_ratio = 0.8
    
    # model
    dropout = 0.1
    
    # opt
    lr = 3e-5
    beta1 = 0.9
    beta2 = 0.98
    weight_decay = 0.01
    cosine_T_max = 8000
    cosine_eta_min = 1e-8

    # train
    epochs = 30
    min_delta = 0
    patience = 3
workflow IDEKO {
  define task ReadData, AddPadding, SplitData, TrainModel;
  START -> ReadData -> AddPadding -> SplitData -> TrainModel -> END;
  configure task ReadData {
    implementation "tasks/IDEKO/read_data.py";
    dependency "tasks/IDEKO/src/**";
  }
  configure task AddPadding {...}
  configure task SplitData {...}
}

workflow AW1 from IDEKO {
  configure task TrainModel {
      implementation "tasks/IDEKO/train_nn.py";
  }
}

workflow AW2 from IDEKO {
  configure task TrainModel {
      implementation "tasks/IDEKO/train_rnn.py";
  }
}

experiment IDEKOExperiment {
    control {
        S1 -> E1;
        E1 ?-> S2 { condition "True"};
        E1 ?-> S3 { condition "False"};
        S2 -> E2;
        S3 -> E2;
        E2 -> S4;
    }
    event E1 {
        type automated;
        task check_accuracy_over_workflows_of_last_space;
    }
    event E2 {
        type manual;
        task change_and_restart;
    }
    space S1 of AW1 {
        strategy gridsearch;
        param epochs_vp = range(50,100,10);
        param batch_size_vp = enum(64, 128);
        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }
    space S2 of AW1 {...}
    space S3 of AW2 {...}
    space S4 of AW1 {
        strategy randomsearch;
        param epochs_vp = range(110,120,2);
        param batch_size_vp = range(20, 50);
        configure task TrainModel {...}
    }
}

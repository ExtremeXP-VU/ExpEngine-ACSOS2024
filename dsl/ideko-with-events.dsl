workflow IDEKO {

  define task ReadData;
  define task AddPadding;
  define task SplitData;
  define task TrainModel;

  START -> ReadData -> AddPadding -> SplitData -> TrainModel -> EvaluateModel -> END;

  configure task ReadData {
    implementation "tasks/IDEKO/read_data.py";
    dependency "tasks/IDEKO/src/**";
  }

  configure task AddPadding {
      implementation "tasks/IDEKO/add_padding.py";
      dependency "tasks/IDEKO/src/**";
    }

  configure task SplitData {
      implementation "tasks/IDEKO/split_data.py";
      dependency "tasks/IDEKO/src/**";
  }

  configure task TrainModel {
      dependency "tasks/IDEKO/src/**";
  }

   configure task EvaluateModel {
      implementation "tasks/IDEKO/evaluate_model.py";
      dependency "tasks/IDEKO/src/**";
  }

  define data InputData;

  configure data InputData {
    path "datasets/ideko-full-dataset/**";
  }

  InputData --> ReadData;

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



experiment EXP {
    control {

        //Automated
        S1 -> E1;

        E1 ?-> S2 { condition "True"};
        E1 ?-> S3 { condition "False"};

        S2 -> S4;
        S3 -> S4;

        //Manual
        // Note E2 is allowed to change any scheduled workflows after it
        S4 -> E2;
        E2 -> S5;

        S4 -> S5 || E2; // This an alternative to line 84. E2 is allowed to change S4 or S5 spaces at any point of time


        S4 -> E3; // checking for multiple events

    }

    event E1 {
        type automated;
        condition "the accuracy of the 5 lastly trained ML models is > 50%";
        task check_accuracy_over_workflows_of_last_space;
    }

    event E2 {
        type manual;
        task change_and_restart;
        restart True;
    }

    space S1 of AW1 {
        strategy gridsearch;
        param epochs_vp = range(80,90,10);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    space S2 of AW1 {
        strategy gridsearch;
        param epochs_vp = range(85,90);
        param batch_size_vp = enum(64, 128, 256);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    space S3 of AW2 {
        strategy gridsearch;
        param epochs_vp = enum(80, 90);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    space S4 of AW1 {
        strategy randomsearch;
        param epochs_vp = range(100,105,2);
        param batch_size_vp = range(60, 70);
        runs = 5;

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    space S5 of AW1 {
        strategy gridsearch;
        param epochs_vp = range(100,105);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }
}




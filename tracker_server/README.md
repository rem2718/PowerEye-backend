# PowerEye Tracker Server

The Tracker Server is composed of 3 interfaces and 11 classes, managing power data from Meross Cloud, storing device details in MongoDB, tracking events like energy goals, and delivering personalized recommendations and push notifications through the FCM Admin SDK. It centralizes backend operations, processes Meross device data, and offers valuable insights. Its event monitoring, personalized recommender, and push notification system boost user engagement and satisfaction.

## How to Run It:

- Inside the _trscker\_server_, place _.secrets_ folder, that we sent you before.

- create these empty folders inside the _tracker\_server_ folder:
    ```
        ├── logs
        ├── models_filesystem
        │  ├── cluster_models
        │  ├── forecast_models
        │  └── test_models
    ```

- In a new terminal, move to the _tracker\_server_ folder:
    ```
        cd tracker_server
    ```

- Create a virtual environment and activate it:
    ```
        python -m venv venv
        
        source myenv/bin/activate
    ```

- Run this code to install all required packages:
    ```
        pip install -r requirements.txt
    ```

- Your _tracker\_server_ folder should be similar to the one in the _codebase.tree_ file.

- Finally run this command to start the scheduler:

    ```
        python scheduler.py
    ```

## How to Run The Tests It:

- If you haven't completed the steps for running the server, follow all of them except for the last one; instead, run the following:

    ```
        pytests tests
    ```
- This command will run all the unit and integration tests. You can run them separately like this:

    ```
        pytest tests/unit
        # or  
        pytest tests/integration
    ```

## Thank You!

Hope you enjoy this implementation :)
For more detailed information about the whole system you can check _Report.pdf_.

Made by:

| Name         | Email               |
| ------------ | ------------------- |
| Reem Hejazi  | 219410002@psu.edu.sa|
| Sara Al Shagawi | 219410319@psu.edu.sa|

GitHub: [@rem2718](https://github.com/rem2718)

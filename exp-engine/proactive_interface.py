import proactive


def create_gateway_and_connect_to_it(username, password):
    print("Logging on proactive-server...")
    proactive_host = 'try.activeeon.com'
    proactive_port = '8443'
    proactive_url  = "https://"+proactive_host+":"+proactive_port
    # print("Creating gateway ")
    gateway = proactive.ProActiveGateway(proactive_url, debug=False)
    # print("Gateway created")

    print("Connecting on: " + proactive_url)
    gateway.connect(username=username, password=password)
    assert gateway.isConnected() is True
    print("Connected")
    return gateway


def create_job(gateway, workflow_name):
    print("Creating a proactive job...")
    proactive_job = gateway.createJob()
    proactive_job.setJobName(workflow_name)
    print("Job created.")
    return proactive_job


def create_fork_env(gateway, proactive_job):
    # print("Adding a fork environment to the import task...")
    proactive_fork_env = gateway.createForkEnvironment(language="groovy")
    proactive_fork_env.setImplementationFromFile("./scripts/fork_env.groovy")
    proactive_job.addVariable("CONTAINER_PLATFORM", "docker")
    proactive_job.addVariable("CONTAINER_IMAGE", "docker://activeeon/dlm3")
    proactive_job.addVariable("CONTAINER_GPU_ENABLED", "false")
    proactive_job.addVariable("CONTAINER_LOG_PATH", "/shared")
    proactive_job.addVariable("HOST_LOG_PATH", "/shared")
    # print("Fork environment created.")
    return proactive_fork_env


def create_python_task(gateway, task_name, fork_environment, task_impl, input_files=[], dependencies=[], is_precious_result=False):
    print(f"Creating task {task_name}...")
    task = gateway.createPythonTask()
    task.setTaskName(task_name)
    task.setTaskImplementationFromFile(task_impl)
    task.setForkEnvironment(fork_environment)
    # TODO Remove the next three lines after adding output files to the DSL
    if task_name == "TrainModel":
        print("inside TrainModel, adding output file")
        task.addOutputFile('datasets/**')
    for input_file in input_files:
        task.addInputFile(input_file)
    for dependency in dependencies:
        print(f"Adding dependency of '{task_name}' to '{dependency.getTaskName()}'")
        task.addDependency(dependency)
    task.setPreciousResult(is_precious_result)
    print("Task created.")
    return task


def configure_task(task, configurations):
    print(f"Configuring task {task.getTaskName()}")
    for k in configurations.keys():
        value = configurations[k]
        if type(value) == int:
            value = str(value)
        task.addVariable(k, value)


def create_flow_script(gateway, condition_task_name, if_task_name, else_task_name, continuation_task_name, condition):
    branch_script = """
if """ + condition + """:
    branch = "if"
else:
    branch = "else"
    """
    print(f"Creating flow script for condition task {condition_task_name}")
    flow_script = gateway.createBranchFlowScript(
        branch_script,
        if_task_name,
        else_task_name,
        continuation_task_name,
        script_language=proactive.ProactiveScriptLanguage().python()
    )
    return flow_script


def submit_job_and_retrieve_results_and_outputs(gateway, job):
    print("Submitting the job to the scheduler...")

    job_id = gateway.submitJobWithInputsAndOutputsPaths(job, debug=False)
    print("job_id: " + str(job_id))

    import time
    is_finished = False
    seconds = 0
    print(f"Current job status: Running...")
    while not is_finished:
        # Get the current state of the job
        job_status = gateway.getJobStatus(job_id)
        # task_status = gateway.getTaskStatus(job_id)

        # Print the current job status
        # print(f"Current job status: {job_status}: {seconds}")
        # Check if the job has finished
        if job_status.upper() in ["FINISHED", "CANCELED", "FAILED"]:
            is_finished = True
        else:
            # Wait for a few seconds before checking again
            seconds += 1
            time.sleep(1)

    print(f"Current job status: Finished")
    # print("Getting job results...")
    # job_result = gateway.getJobResult(job_id, 300000)
    # print("****")
    # print(type(job_result))
    # print(job_result)
    # print("****")

    # task_result = gateway.getTaskResult(job_id, "TrainModel", 300000)
    # print(task_result)

    print("Getting job result map...")
    result_map = dict(gateway.waitForJob(job_id, 600000).getResultMap())
    print("Results:")
    for key, value in result_map.items():
        print(f"    {key.capitalize()}: {value}")

    # print("Getting job outputs...")
    job_outputs = gateway.printJobOutput(job_id, 600000)
    # print(job_outputs)

    return job_id, result_map, job_outputs


def teardown(gateway):
    # print("Disconnecting")
    gateway.disconnect()
    # print("Disconnected")
    gateway.terminate()
    # print("Finished")


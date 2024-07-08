import textx
from itertools import product
import random
from classes import *
import proactive
import time
import os
import sys
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import credentials
from proactive_interface import *
import dsl_exceptions
import itertools
import matplotlib.pyplot as plt

nodes = set()
automated_events = set()
manual_events = set()
spaces = set()
space_configs = []
automated_dict = {}
manual_dict = {}
parsed_manual_events = []
parsed_automated_events = []
results = {}


def process_dependencies(task_dependencies, nodes, parsing_node_type, verbose_logging=False):
    if verbose_logging:
        print(parsing_node_type)
    for n1, n2 in zip(nodes[0::1], nodes[1::1]):
        if verbose_logging:
            print(str(n2.name), ' depends on ', str(n1))
        if n2.name in task_dependencies:
            print(f"{parsing_node_type}: Double dependency ({n2.name}), check your specification")
            # exit(0)
        else:
            # TODO what about tasks with multiple dependencies?
            task_dependencies[n2.name] = [n1.name]

def add_input_output_data(wf, nodes):
    for n1, n2 in zip(nodes[0::1], nodes[1::1]):
        if n1.__class__.__name__ == "DefineTask":
            ds = wf.get_dataset(n2.name)
            wf.get_task(n1.name).output_files.append(ds.path)
        if n1.__class__.__name__ == "DefineData":
            ds = wf.get_dataset(n1.name)
            wf.get_task(n2.name).input_files.append(ds.path)


def apply_task_dependencies_and_set_order(wf, task_dependencies):
    for t in wf.tasks:
        if t.name in task_dependencies.keys():
            t.add_dependencies(task_dependencies[t.name])
    re_order_tasks_in_workflow(wf)

def re_order_tasks_in_workflow(wf):
    first_task = [t for t in wf.tasks if not t.dependencies][0]
    order = 0
    first_task.set_order(order)
    dependent_tasks = [t for t in wf.tasks if first_task.name in t.dependencies]
    while dependent_tasks:
        order += 1
        new_dependent_tasks = []
        for dependent_task in dependent_tasks:
            dependent_task.set_order(order)
            new_dependent_tasks += [t for t in wf.tasks if dependent_task.name in t.dependencies]
        dependent_tasks = new_dependent_tasks

def find_dependent_tasks(wf, task, dependent_tasks):
    for t in wf.tasks:
        if task.name in t.dependencies:
            dependent_tasks.append(t)
        if t.sub_workflow:
            find_dependent_tasks(t.sub_workflow, task, dependent_tasks)
    return dependent_tasks


def exists_parent_workflow(wfs, wf_name):
    for wf in wfs:
        if wf_name in [task.sub_workflow.name for task in wf.tasks if task.sub_workflow]:
            return True
    return False


def set_is_main_attribute(wfs):
    for wf in wfs:
        wf.set_is_main(not exists_parent_workflow(wfs, wf.name))


def get_underlying_tasks(t, assembled_wf, tasks_to_add):
    i = 0
    for task in sorted(t.sub_workflow.tasks, key=lambda t: t.order):
        if not task.sub_workflow:
            if i==0:
                task.add_dependencies(t.dependencies)
            if i==len(t.sub_workflow.tasks)-1:
                dependent_tasks = find_dependent_tasks(assembled_wf, t, [])
                dep = [t.name for t in dependent_tasks]
                print(f"{t.name} --> {dep} becomes {task.name} --> {dep}")
                for dependent_task in dependent_tasks:
                    dependent_task.remove_dependency(t.name)
                    dependent_task.add_dependencies([task.name])
            tasks_to_add.append(task)
        else:
            get_underlying_tasks(task, assembled_wf, tasks_to_add)
        i += 1
    return tasks_to_add

def get_parsed_workflows(workflow_model):
    parsed_workflows = []
    for component in workflow_model.component:
        if component.__class__.__name__ == 'Workflow':
            wf = Workflow(component.name)
            parsed_workflows.append(wf)

            task_dependencies = {}

            for e in component.elements:
                if e.__class__.__name__ == "DefineTask":
                    task = WorkflowTask(e.name)
                    wf.add_task(task)

                if e.__class__.__name__ == "DefineData":
                    ds = WorkflowDataset(e.name)
                    wf.add_dataset(ds)

                if e.__class__.__name__ == "ConfigureTask":
                    task = wf.get_task(e.alias.name)
                    if e.workflow:
                        task.add_sub_workflow_name(e.workflow.name)
                    elif e.filename:
                        if not os.path.exists(e.filename):
                            raise dsl_exceptions.ImplementationFileNotFound(f"{e.filename} in task {e.alias.name}")
                        task.add_implementation_file(e.filename)
                    if e.dependency:
                        task.input_files.append(e.dependency)

                if e.__class__.__name__ == "ConfigureData":
                    ds = wf.get_dataset(e.alias.name)
                    ds.add_path(e.path)

                if e.__class__.__name__ == "StartAndEndEvent":
                    process_dependencies(task_dependencies, e.nodes, "StartAndEndEvent")

                if e.__class__.__name__ == "StartEvent":
                    process_dependencies(task_dependencies, e.nodes, "StartEvent")

                if e.__class__.__name__ == "EndEvent":
                    process_dependencies(task_dependencies, e.nodes, "EndEvent")

                if e.__class__.__name__ == "TaskLink":
                    process_dependencies(task_dependencies, [e.initial_node] + e.nodes, "TaskLink")

                if e.__class__.__name__ == "DataLink":
                    add_input_output_data(wf, [e.initial] + e.rest)

    apply_task_dependencies_and_set_order(wf, task_dependencies)

    set_is_main_attribute(parsed_workflows)

    return parsed_workflows


def get_fully_determined_workflow_data(workflow_model):
    assembled_workflows_data = []
    for component in workflow_model.component:
        if component.__class__.__name__ == 'AssembledWorkflow':
            assembled_workflow_data = {}
            assembled_workflows_data.append(assembled_workflow_data)
            assembled_workflow_data["name"] = component.name
            assembled_workflow_data["parent"] = component.parent_workflow.name
            assembled_workflow_tasks = {}
            assembled_workflow_data["tasks"] = assembled_workflow_tasks

            configurations = component.tasks

            while configurations:
                for config in component.tasks:
                    assembled_workflow_task = {}
                    if config.workflow:
                        assembled_workflow_task["workflow"] = config.workflow
                        assembled_workflow_tasks[config.alias.name] = assembled_workflow_task
                    elif config.filename:
                        if not os.path.exists(config.filename):
                            raise dsl_exceptions.ImplementationFileNotFound(
                                f"{config.filename} in task {config.alias.name}")
                        assembled_workflow_task["implementation"] = config.filename
                        assembled_workflow_tasks[config.alias.name] = assembled_workflow_task
                    configurations.remove(config)
                    configurations += config.subtasks

    return assembled_workflows_data


def read_dsl_file(file_path):
    try:
        with open(file_path, 'r') as file:
            dsl_content = file.read()
    except FileNotFoundError:
        print("File not found. Please check the path and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return dsl_content

def check_dsl(workflow_code):
    try:
        workflow_metamodel = textx.metamodel_from_file('../dsl/workflow_grammar_new.tx')
        workflow_model = workflow_metamodel.model_from_str(workflow_code)
        return workflow_model
    except FileNotFoundError:
        print("Workflow grammar file not found. Please check the path and try again.")
    except textx.exceptions.TextXSyntaxError as e:
        print(f"Syntax error in the DSL code: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def generate_final_assembled_workflows(wfs, assembled_wfs_data):
    new_wfs = []
    for assembled_wf_data in assembled_wfs_data:
        wf = next(w for w in wfs if w.name == assembled_wf_data["parent"]).clone()
        wf.name = assembled_wf_data["name"]
        new_wfs.append(wf)
        print(wf.name)
        for task in wf.tasks:
            if task.name in assembled_wf_data["tasks"].keys():
                print(f"Need to configure task '{task.name}'")
                task_data = assembled_wf_data["tasks"][task.name]
                if "implementation" in task_data:
                    print(f"Changing implementation of task '{task.name}' to '{task_data['implementation']}'")
                    task.add_implementation_file(task_data["implementation"])
            else:
                print(f"Do not need to configure task '{task.name}'")
            if task.sub_workflow:
                configure_wf(task.sub_workflow, assembled_wf_data)
        print_divider()
    return new_wfs

def flatten_workflows(assembled_wf):
    # print(f"Flattening assembled workflow with name {assembled_wf.name}")
    new_wf = Workflow(assembled_wf.name)
    for t in assembled_wf.tasks:
        if t.sub_workflow:
            tasks_to_add = get_underlying_tasks(t, assembled_wf, [])
            for t in tasks_to_add:
                new_wf.add_task(t)
        else:
            new_wf.add_task(t)
    re_order_tasks_in_workflow(new_wf)
    new_wf.set_is_main(True)
    return new_wf

def configure_wf(workflow, assembled_wf_data):
    print(workflow.name)
    for task in workflow.tasks:
        if task.name in assembled_wf_data["tasks"].keys():
            print(f"Need to configure task '{task.name}'")
            task_data = assembled_wf_data["tasks"][task.name]
            if "implementation" in task_data:
                print(f"Changing implementation of task '{task.name}' to '{task_data['implementation']}'")
                task.add_implementation_file(task_data["implementation"])
        else:
            print(f"Do not need to configure task '{task.name}'")
        if task.sub_workflow:
            configure_wf(task.sub_workflow, assembled_wf_data)


def get_exp_specification(workflow_model):
    for component in workflow_model.component:
        if component.__class__.__name__ == 'Experiment':
            print("Experiment name: ", component.name)

            for node in component.experimentNode:
                if node.__class__.__name__ == 'Event':
                    # print(f"Event: {node.name}")
                    # print(f"Type: {node.eventType}")
                    if node.eventType == 'automated':
                        automated_events.add(node.name)
                        parsed_event = AutomatedEvent(node.name, node.event_task)
                        parsed_automated_events.append(parsed_event)

                    if node.eventType == 'manual':
                        manual_events.add(node.name)
                        parsed_event = ManualEvent(node.name, node.event_task)
                        parsed_manual_events.append(parsed_event)


                elif node.__class__.__name__ == 'SpaceConfig':
                    print()
                    print(f"    Space: {node.name}")
                    print(f"    Assembled Workflow: {node.assembled_workflow.name}")
                    print(f"    Strategy : {node.strategy_name}")

                    spaces.add(node.name)

                    space_config_data = {
                        "name": node.name,
                        "assembled_workflow": node.assembled_workflow.name,
                        "strategy": node.strategy_name,
                        "tasks": {},
                        "VPs": [],
                        "runs": node.runs
                    }

                    if node.tasks:
                        for task_config in node.tasks:
                            print(f"    Task: {task_config.task.name}")
                            task_name = task_config.task.name
                            task_data = {}

                            for param_config in task_config.config:
                                print(f"        Param: {param_config.param_name} = {param_config.vp}")
                                param_name = param_config.param_name
                                param_vp = param_config.vp

                                task_data[param_name] = param_vp

                            space_config_data["tasks"][task_name] = task_data

                    if node.vps:
                        for vp in node.vps:
                            if hasattr(vp.vp_values, 'values'):
                                print(f"        {vp.vp_name} = enum{vp.vp_values.values};")
                                vp_data = {
                                    "name": vp.vp_name,
                                    "values": vp.vp_values.values,
                                    "type": "enum"
                                }
                                space_config_data["VPs"].append(vp_data)

                            elif hasattr(vp.vp_values, 'minimum') and hasattr(vp.vp_values, 'maximum'):
                                min_value = vp.vp_values.minimum
                                max_value = vp.vp_values.maximum
                                step_value = getattr(vp.vp_values, 'step', 1)
                                print(f"        {vp.vp_name} = range({min_value}, {max_value}, {step_value});")

                                vp_data = {
                                    "name": vp.vp_name,
                                    "minimum": min_value,
                                    "maximum": max_value,
                                    "step": step_value,
                                    "type": "range"
                                }
                                space_config_data["VPs"].append(vp_data)

                    if (node.runs != 0):
                        print(f"        Runs: ", {node.runs})

                    space_configs.append(space_config_data)

            nodes = automated_events | manual_events | spaces

            if component.control:
                print("\nControl exists")
                print_divider()
                print("Automated Events")
                for control in component.control:
                    for explink in control.explink:
                        if explink.__class__.__name__ == 'RegularExpLink':
                            if explink.initial_space and explink.spaces:
                                initial_space_name = explink.initial_space.name

                                if any(event in initial_space_name or any(
                                        event in space.name for space in explink.spaces) for event in automated_events):
                                    for event in automated_events:
                                        if event in initial_space_name or any(
                                                event in space.name for space in explink.spaces):
                                            print(f"Event: {event}")
                                            link = f"  Regular Link: {initial_space_name}"
                                            for space in explink.spaces:
                                                link += f" -> {space.name}"
                                                # if space.name in nodes:
                                                #     nodes.remove(space.name)
                                            print(link)

                                if initial_space_name not in automated_dict:
                                    automated_dict[initial_space_name] = {}

                                for space in explink.spaces:
                                    if space is not None:
                                        automated_dict[initial_space_name]["True"] = space.name
                                        if space.name in nodes:
                                            nodes.remove(space.name)


                        elif explink.__class__.__name__ == 'ConditionalExpLink':
                            if explink.fromspace and explink.tospace:
                                if any(event in explink.fromspace.name or event in explink.tospace.name for event in
                                       automated_events):
                                    line = f"  Conditional Link: {explink.fromspace.name}"
                                    line += f" ?-> {explink.tospace.name}"
                                    line += f"  Condition: {explink.condition}"
                                    print(line)

                                    if explink.tospace.name in nodes:
                                        nodes.remove(explink.tospace.name)

                                if explink.fromspace.name not in automated_dict:
                                    automated_dict[explink.fromspace.name] = {}

                                automated_dict[explink.fromspace.name][explink.condition] = explink.tospace.name

                print_divider()
                print("Manual Events")
                for control in component.control:
                    for explink in control.explink:
                        if explink.__class__.__name__ == 'RegularExpLink':
                            if explink.initial_space and explink.spaces:
                                initial_space_name = explink.initial_space.name
                                if initial_space_name == "START":
                                    initial_space_name = explink.start.name

                                if any(event in initial_space_name or any(
                                        event in space.name for space in explink.spaces) for event in manual_events):
                                    for event in manual_events:
                                        if event in initial_space_name or any(
                                                event in space.name for space in explink.spaces):

                                            link = f"  Regular Link: {initial_space_name}"
                                            for space in explink.spaces:
                                                link += f" -> {space.name}"
                                            print(link)

                                if initial_space_name not in manual_dict:
                                    manual_dict[initial_space_name] = {}

                                for space in explink.spaces:
                                    if space is not None:
                                        manual_dict[initial_space_name]["True"] = space.name

                        elif explink.__class__.__name__ == 'ConditionalExpLink':
                            if explink.fromspace and explink.tospace:
                                if any(event in explink.fromspace.name or event in explink.tospace.name for event in
                                       manual_events):
                                    line = f"  Conditional Link: {explink.fromspace.name}"
                                    line += f" ?-> {explink.tospace.name}"
                                    line += f"  Condition: {explink.condition}"
                                    print(line)

                                if explink.fromspace.name not in manual_dict:
                                    manual_dict[explink.fromspace.name] = {}

                                manual_dict[explink.fromspace.name][explink.condition] = explink.tospace.name


    return nodes,automated_events,manual_events,spaces,space_configs,automated_dict,manual_dict,parsed_manual_events,parsed_automated_events

def run_experiment(nodes,flat_wf):
    start_node = list(nodes)[0]
    print("Start Node: ", start_node)
    node = start_node

    result = execute_node(node, flat_wf)
    while node in automated_dict:
        next_action = automated_dict[node]
        node = next_action[result]
        result = execute_node(node,flat_wf)

def execute_node(node,flat_wf):
    if node in spaces:
        return execute_space(node,flat_wf)

    elif node in automated_events:
        return  execute_automated_event(node)

    elif node in manual_events:
        return execute_manual_event(node)

def execute_automated_event(node):
    # print(f"Executing automated event")
    e = next((e for e in parsed_automated_events if e.name == node), None)
    module = __import__('USECASE_events')
    func = getattr(module, "check_accuracy_over_workflows_of_last_space")
    ret = func(results)
    print_divider()
    return ret

def execute_manual_event(node):
    # print("executing manual event")
    e = next((e for e in parsed_manual_events if e.name == node), None)
    # print(e.task)
    module = __import__('USECASE_events')
    func = getattr(module,"change_and_restart")
    ret = func(automated_dict,space_configs,e.name)
    print_divider()
    return ret

def execute_wf(w):
    gateway = create_gateway_and_connect_to_it(credentials.proactive_username, credentials.proactive_password)
    job = create_job(gateway, w.name)
    fork_env = create_fork_env(gateway, job)

    previous_tasks = []
    for t in w.tasks:
        task_to_execute = create_python_task(gateway, t.name, fork_env, t.impl_file, t.input_files, previous_tasks)
        if len(t.params) > 0:
            configure_task(task_to_execute, t.params)
        job.addTask(task_to_execute)
        previous_tasks = [task_to_execute]
    print("Tasks added.")

    job_id, job_result_map, job_outputs = submit_job_and_retrieve_results_and_outputs(gateway, job)
    teardown(gateway)
    return job_result_map
def execute_space(node,flat_wf):
    space_config = next((s for s in space_configs if s['name'] == node), None)
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(space_config)
    print(f"\nRunning experiment of space '{space_config['name']}' of type '{space_config['strategy']}'")
    method_type = space_config["strategy"]

    if method_type == "gridsearch":
        run_grid_search(space_config,flat_wf)

    if method_type == "randomsearch":
        run_random_search(space_config,flat_wf)

    # print("node executed")
    print("Results so far")
    for s_key, s_value in results.items():
        print(f"Results for {s_key}:")
        for run_number, run_data in s_value.items():
            config = ", ".join(f"{key}: {value}" for key, value in run_data['configuration'])
            print(f"  Run {run_number}:")
            print(f"    Configuration: {config}")
            print(f"    Result: {run_data['result']}")
        print()
    plot_graph(results)
    print_divider()
    return 'True'

def run_grid_search(space_config,flat_wf):
     grid_search_combinations = []
     VPs = space_config["VPs"]
     vp_combinations = []

     for vp_data in VPs:
         if vp_data["type"] == "enum":
             vp_name = vp_data["name"]
             vp_values = vp_data["values"]
             vp_combinations.append([(vp_name, value) for value in vp_values])

         elif vp_data["type"] == "range":
             vp_name = vp_data["name"]
             min_value = vp_data["minimum"]
             max_value = vp_data["maximum"]
             step_value = vp_data.get("step", 1) if vp_data["step"] != 0 else 1
             vp_values = list(range(min_value, max_value + 1, step_value))
             vp_combinations.append([(vp_name, value) for value in vp_values])


     combinations = list(itertools.product(*vp_combinations))
     grid_search_combinations.extend(combinations)

     print(f"\nGrid search generated {len(combinations)} configurations to run.\n")
     for combination in combinations:
         print(combination)


     user_input = input("\nDo you want to proceed with the experiment (y/n)? ").strip().lower()
     if user_input == 'y':
         space_results = {}
         results[space_config['name']] = space_results
         run_count = 1
         for c in combinations:
             GREEN = '\033[92m'  # ANSI escape code for green
             BOLD = '\033[1m'
             RESET = '\033[0m'
             print_divider()
             print(f'{BOLD}{GREEN}Run {run_count}{RESET}')
             workflow_to_run = get_workflow_to_run(space_config, c, flat_wf)
             print_divider()
             # result = execute_wf(workflow_to_run)
             # workflow_results = {}
             # workflow_results["configuration"] = c
             # workflow_results["result"] = result
             # space_results[run_count] = workflow_results
             # print_divider()
             run_count += 1

     elif user_input == 'n':
         sys.exit()




def get_workflow_to_run(space_config, c,assembled_flat_wfs):
    c_dict = dict(c)
    w = next(w for w in assembled_flat_wfs if w.name == space_config["assembled_workflow"])
    for t in w.tasks:
        if t.name in space_config["tasks"].keys():
            task_config = space_config["tasks"][t.name]
            for param_name, param_vp in task_config.items():
                alias = param_vp
                print(f"Setting param '{param_name}' of task '{t.name}' to '{c_dict[alias]}'")
                t.set_param(param_name, c_dict[alias])
    return w

def  run_random_search(space_config, flat_wf):
    random_combinations = []

    vps = space_config['VPs']
    runs = space_config['runs']

    for i in range(runs):
        combination={}
        for vp_data in vps:
            vp_name = vp_data['name']
            if vp_data["type"] == "enum":
                values = vp_data['values']
                value = random.choice(values)
            elif vp_data["type"] == "range":
                minimum = vp_data['minimum']
                maximum = vp_data['maximum']
                value = random.randint(minimum, maximum)
            combination[vp_name] = value

        random_combinations.append((combination))


    print(f"\nRandom search generated {len(random_combinations)} configurations to run.\n")
    for c in random_combinations:
        print(c)

    user_input = input("\nDo you want to proceed with the experiment (y/n)? ").strip().lower()
    if user_input == 'y':
        run_count = 1
        space_results = {}
        results[space_config['name']] = space_results
        for c in random_combinations:
            GREEN = '\033[92m'  # ANSI escape code for green
            BOLD = '\033[1m'
            RESET = '\033[0m'
            print_divider()
            print(f'{BOLD}{GREEN}Run {run_count}{RESET}')
            workflow_to_run = get_workflow_to_run(space_config, c, flat_wf)
            result = execute_wf(workflow_to_run)
            workflow_results = {}
            workflow_results["configuration"] = c
            workflow_results["result"] = result
            space_results[run_count] = workflow_results
            print_divider()
            run_count += 1

    elif user_input == 'n':
        sys.exit()

def plot_graph(results):
    for s_key, s_value in results.items():
        print(f"Results for {s_key}:")
        for run_number, run_data in s_value.items():
            config = ", ".join(f"{key}: {value}" for key, value in run_data['configuration'])
            print(f"  Run {run_number}:")
            print(f"    Configuration: {config}")
            print(f"    Result: {run_data['result']}")
        print()

    # Extract and plot data for all scenarios
    fig, ax1 = plt.subplots(figsize=(12, 8))

    for scenario, runs in results.items():
        configurations = []
        accuracies = []

        for run_id, data in runs.items():
            configuration = data['configuration']
            accuracy = data['result']['accuracy']

            configurations.append(
                f"{scenario} run{run_id}: epochs={configuration[0][1]}, batch_size={configuration[1][1]}")
            accuracies.append(accuracy)

        # Plot data for the current scenario
        ax1.plot(configurations, accuracies, marker='o', label=f'{scenario} Accuracy')

    # Set labels and title
    ax1.set_xlabel('Configurations')
    ax1.set_ylabel('Accuracy')
    plt.title('Accuracy for All Configurations')

    # Rotate x-tick labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Add legend to the side
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # Adjust layout to prevent label overlap
    fig.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust right margin to make space for legend

    # Show plot
    plt.show()


def get_terminal_width():
    return os.get_terminal_size().columns

def print_centered_message(message):
    terminal_width = get_terminal_width()
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    print_border()
    for line in message:
        centered_line = line.center(terminal_width)
        print(f'{BOLD}{BLUE}{centered_line}{RESET}')
    print_border()

def print_left_aligned_message(message):
    terminal_width = get_terminal_width()
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    print_border()
    for line in message:
        print(f'{BOLD}{BLUE} {line.ljust(terminal_width - 3)}{RESET}')  # Adjust for borders
    print_border()
def print_border():
    terminal_width = get_terminal_width()
    border = '*' * terminal_width
    print(border)

def print_divider():
    terminal_width = get_terminal_width()
    border = '-' * terminal_width
    print(border)


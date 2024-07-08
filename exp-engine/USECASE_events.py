import pprint
import sys


def check_accuracy_over_workflows_of_last_space(results):
    accuracies=[]
    GREEN = '\033[92m'  # ANSI escape code for green
    BOLD = '\033[1m'
    RESET = '\033[0m'
    print(f'{BOLD}{GREEN}Executing check_average_accuracy_over_workflows_of_last_space{RESET}')


    for s in results:
        # Iterating over the second-level keys (e.g., 1, 2, etc.)
        for r in results[s]:
            # Accessing the accuracy value and adding it to the list
            accuracy = results[s][r]['result']['accuracy']
            accuracies.append(accuracy)

    average_accuracy = sum(accuracies) / len(accuracies)

    print("Accuracies achieved so far: ", accuracies)

    print("The average accuracy is ", average_accuracy)

    if average_accuracy > 0.80:
        print("Average accuracy > 80%: True")

    while True:
        user_input = input("Do you want to proceed with the result (y/n)? ").strip().lower()
        if user_input == 'y':
                return 'True'

        elif user_input == 'n':
            sys.exit()
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def change_and_restart(control_dict, space_configs,event_name):
    GREEN = '\033[92m'  # ANSI escape code for green
    BOLD = '\033[1m'
    RESET = '\033[0m'
    print(f'{BOLD}{GREEN}Executing change_and_restart{RESET}')

    # print("Control Dictionary:")
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(control_dict)

    # print("Space Configurations:")
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(space_configs)

    next_space = next((control_dict[e]['True'] for e in control_dict if e == event_name), None)
    # print(next_space)

    for config in space_configs:
        if config['name'] == next_space:
            next_space_config = config
            vps = config["VPs"]

    print("Configuration of the next space")
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(next_space_config)

    print(f"Space: ",next_space_config['name'])

    print(f"Assembled Workflow: ",next_space_config['assembled_workflow'])
    print(f"Params with values: ")
    # print(vps)
    for vp in vps:
        if vp['type'] =="range":
            print(vp['name'], "=" , vp['type'],"[", vp['min'], ',' , vp['max'], ',' , vp['step'],']')

        elif vp['type'] == 'enum':
             print(vp['name'], "=" , vp['type'],vp['values'])

    print()
    user_input = input("Do you want to change the param values (y/n)? ").strip().lower()
    if user_input == 'y':
        update_config(next_space_config)
        return 'True'

    elif user_input == 'n':
        return 'True'

def update_config(config):
    for vp in config['VPs']:
        user_input = input(f"Do you want to change the {vp['name']} values (y/n)? ").strip().lower()
        if user_input == 'y':
            type_choice = input("Do you want to use (range/enum)? ").strip().lower()
            if type_choice == 'range':
                min_val = int(input("Enter min value for epochs_vp: ").strip())
                max_val = int(input("Enter max value for epochs_vp: ").strip())
                step_val = int(input("Enter step value for epochs_vp: ").strip())

                vp['min'] = min_val
                vp['max'] = max_val
                vp['step'] = step_val
                vp['type'] = 'range'
                vp.pop('values', None)

            elif type_choice == 'enum':
                values = input("Enter values for epochs_vp (comma-separated): ").strip()
                values_list = list(map(int, values.split(',')))

                vp['values'] = values_list
                vp['type'] = 'enum'
                vp.pop('min', None)
                vp.pop('max', None)
                vp.pop('step', None)

    print("Updated configuration:")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(config)


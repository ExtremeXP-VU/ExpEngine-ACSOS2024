from functions import *

print_centered_message(["Welcome to the ExptremeXP ExpEngine"])

file_path = input("Please provide the path to the DSL file: ")

# file_path = "../dsl/usecase-with-events-demo.exp"
workflow_code = read_dsl_file(file_path)
workflow_model = check_dsl(workflow_code)

while True:
    print("1. View parsed workflows")
    print("2. View fully determined workflows data")
    print("3. View experiment specification")
    print("4. Run experiment")
    print("5. Exit")

    try:
        choice = int(input("Enter the option: "))
        if choice == 1:
            print_centered_message(["PARSED WORKFLOWS"])
            parsed_worfklows = get_parsed_workflows(workflow_model)

            for wf in parsed_worfklows:
                wf.print()
            print_border()

        elif choice == 2:
            print_centered_message(["FULLY DETERMINED WORKFLOWS DATA"])
            assembled_workflows_data = get_fully_determined_workflow_data(workflow_model)

            for item in assembled_workflows_data:
                print(f"Name: {item['name']}")
                print(f"Parent: {item['parent']}")
                print("Tasks:")
                for task_name, task_details in item['tasks'].items():
                    print(f"    Task: {task_name}")
                    for detail_name, detail_value in task_details.items():
                        print(f"    {detail_name}: {detail_value}")
                print()


            print_centered_message(["GENERATE FULLY DETERMINED WORKFLOWS"])
            assembled_flat_wfs = []

            assembled_wfs = generate_final_assembled_workflows(parsed_worfklows, assembled_workflows_data)

            assembled_flat_wfs = []

            for wf in assembled_wfs:
                flat_wf = flatten_workflows(wf)
                assembled_flat_wfs.append(flat_wf)
                flat_wf.print()

            print_border()


        elif choice == 3:
            print_centered_message(["EXPERIMENT SPECIFICATION"])
            nodes, automated_events, manual_events, spaces, space_configs, automated_dict, manual_dict, parsed_manual_events, parsed_automated_events = get_exp_specification(
                workflow_model)
            print_border()

        elif choice == 4:
            print_centered_message(["RUNNING EXPERIMENTS"])
            run_experiment(nodes, assembled_flat_wfs)
            print_border()

        elif choice == 5:
            plot_graph(results)
        else:
            print("Invalid choice. Please enter a valid option.")
    except ValueError:
        print("Invalid input. Please enter a number.")











class Workflow():

    def __init__(self, name):
        self.is_main = None
        self.name = name
        self.tasks = []
        self.datasets = []

    def add_task(self, task):
        self.tasks.append(task)

    def add_dataset(self, dataset):
        self.datasets.append(dataset)

    def get_task(self, name):
        return next(t for t in self.tasks if t.name == name)

    def get_dataset(self, name):
        return next(ds for ds in self.datasets if ds.name == name)

    def is_flat(self):
        for t in self.tasks:
            if t.sub_workflow:
                return False
        return True

    def set_is_main(self, is_main):
        self.is_main = is_main

    def clone(self):
        new_w = Workflow(self.name)
        new_w.is_main = self.is_main
        for t in self.tasks:
            new_t = t.clone()
            new_w.tasks.append(new_t)
        return new_w

    def print(self, tab=""):
        print(f"{tab}Workflow with name: {self.name}")
        for t in self.tasks:
            t.print(tab + "\t")
            if t.sub_workflow:
                t.sub_workflow.print(tab + "\t\t")


class WorkflowTask():

    def __init__(self, name):
        self.params = {}
        self.order = None
        self.sub_workflow_name = None
        self.sub_workflow = None
        self.impl_file = None
        self.input_files = []
        self.output_files = []
        self.dependencies = []
        self.conditional_dependencies = []
        self.name = name
        self.if_task_name = None
        self.else_task_name = None
        self.continuation_task_name = None
        self.condition = None

    def add_conditional_dependency(self, task, condition):
        self.conditional_dependencies.append((task, condition))

    def set_conditional_tasks(self, task_if, task_else, task_continuation, condition):
        self.if_task_name = task_if
        self.else_task_name = task_else
        self.continuation_task_name = task_continuation
        self.condition = condition

    def is_condition_task(self):
        return self.condition is not None

    def add_implementation_file(self, impl_file):
        self.impl_file = impl_file

    def add_sub_workflow_name(self, workflow_name):
        self.sub_workflow_name = workflow_name

    def add_sub_workflow(self, workflow):
        self.sub_workflow = workflow

    def add_dependencies(self, dependencies):
        self.dependencies += dependencies

    def remove_dependency(self, dependency):
        self.dependencies.remove(dependency)

    def set_order(self, order):
        self.order = order

    def set_param(self, key, value):
        self.params[key] = value

    def clone(self):
        new_t = WorkflowTask(self.name)
        new_t.add_implementation_file(self.impl_file)
        new_t.add_sub_workflow_name(self.sub_workflow_name)
        if self.sub_workflow_name:
            new_t.add_sub_workflow(next(w for w in parsed_workflows if w.name == self.sub_workflow_name).clone())
        new_t.add_dependencies(self.dependencies)
        new_t.input_files = self.input_files
        new_t.output_files = self.output_files
        new_t.set_order(self.order)
        new_t.params = self.params
        new_t.condition = self.condition
        new_t.if_task_name = self.if_task_name
        new_t.else_task_name = self.else_task_name
        new_t.continuation_task_name = self.continuation_task_name
        return new_t

    def print(self, tab=""):
        print(f"{tab}with task name : {self.name}")
        print(f"{tab}\twith task implementation: {self.impl_file}")
        print(f"{tab}\twith sub_workflow_name: {self.sub_workflow_name}")
        print(f"{tab}\twith sub_workflow: {self.sub_workflow}")
        print(f"{tab}\twith dependencies: {self.dependencies}")
        print(f"{tab}\twith inputs: {self.input_files}")
        print(f"{tab}\twith outputs: {self.output_files}")
        print(f"{tab}\twith order: {self.order}")
        print()


class WorkflowDataset():

    def __init__(self, name):
        self.name = name
        self.path = None

    def add_path(self, path):
        self.path = path


class AutomatedEvent():
    def __init__(self, name, task):
        self.name = name
        self.task = task

class ManualEvent():
    def __init__(self, name, task):
        self.name = name
        self.task = task

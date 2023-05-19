import inspect
from collections import deque
from typing import Any, Callable, Dict, List, Tuple


def create_dataclass_wrapper(
    conversion_functions: Dict[Tuple[type, type], Callable[..., Any]]
):
    # Infer the dataclasses from the conversion_functions
    dataclasses = {src for src, _ in conversion_functions.keys()} | {
        dest for _, dest in conversion_functions.keys()
    }

    # Construct the graph for BFS
    graph: Dict[type, List[type]] = {dataclass: [] for dataclass in dataclasses}
    for (src, dest), func in conversion_functions.items():
        graph[src].append(dest)

    def bfs_path(src: type, dest: type) -> List[type]:
        queue = deque([(src, [src])])
        while queue:
            node, path = queue.popleft()
            if node == dest:
                return path
            for next_node in graph[node]:
                if next_node not in path:
                    queue.append((next_node, path + [next_node]))
        return []

    def dataclass_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)

        def wrapped_func(*args, **kwargs):
            print(f"Original args: {args}")
            print(f"Original kwargs: {kwargs}")
            new_args = []
            new_kwargs = {}

            for i, (param_name, param) in enumerate(sig.parameters.items()):
                target_type = param.annotation
                if target_type in dataclasses:
                    input_dataclass = args[i] if i < len(args) else kwargs.get(param_name)

                    if input_dataclass is not None:
                        print(f"Input dataclass: {input_dataclass}")
                        input_type = type(input_dataclass)
                        if input_type != target_type:
                            if input_type in graph and target_type in graph:  # added condition here
                                path = bfs_path(input_type, target_type)
                                if path:
                                    for j in range(len(path) - 1):
                                        conversion_func = conversion_functions.get((path[j], path[j + 1]))
                                        if conversion_func is not None:
                                            input_dataclass = conversion_func(input_dataclass)
                                        # else: leave input_dataclass as is, because path[j] == path[j + 1]
                                else:
                                    raise ValueError(
                                        f"No conversion path for {input_type} to {target_type}"
                                    )

                    if i < len(args):
                        new_args.append(input_dataclass)
                    else:
                        new_kwargs[param_name] = input_dataclass
                else:  # for non-dataclass parameters, simply pass them through
                    if i < len(args):
                        new_args.append(args[i])
                    else:
                        new_kwargs[param_name] = kwargs.get(param_name)

            print(f"New args: {new_args}")
            print(f"New kwargs: {new_kwargs}")
            return func(*new_args, **new_kwargs)

        return wrapped_func

    return dataclass_wrapper

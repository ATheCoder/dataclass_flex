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
            new_args = []
            new_kwargs = {}
            for i, (param_name, param) in enumerate(sig.parameters.items()):
                target_type = param.annotation
                if target_type in dataclasses:
                    input_dataclass = args[i] if i < len(args) else kwargs.get(param_name)

                    if input_dataclass is not None:
                        input_type = type(input_dataclass)
                        if input_type != target_type:
                            try:
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
                            except KeyError as e:
                                raise ValueError(f'Input of type {e} is not right.')

                    if i < len(args):
                        new_args.append(input_dataclass)
                    else:
                        new_kwargs[param_name] = input_dataclass
                        
            return func(*new_args, **new_kwargs)

        return wrapped_func
    return dataclass_wrapper

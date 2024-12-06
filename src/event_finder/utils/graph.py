from typing import List, Set


def get_connected_component(node_index: int, adj_matrix: List[List[int]]) -> Set[int]:
    visited = set()
    number_nodes = len(adj_matrix)

    def dfs(index: int):
        visited.add(index)
        for i in range(number_nodes):
            if adj_matrix[index][i] == 1 and i not in visited:
                dfs(i)

    dfs(node_index)
    return visited
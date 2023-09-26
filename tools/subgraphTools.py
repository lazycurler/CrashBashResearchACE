import igraph as ig
import matplotlib.pyplot as plt

# The entirety of this function was written by ChatGPT, thanks bud!
# Apparently it's a modified version of Tarjan's Algorithm
def find_terminal_subgraphs(graph):
    # Counter for assigning unique indices during depth-first search
    index_counter = [0]
    # Stack to keep track of vertices in the depth-first search
    stack = []
    # Lowlink values for vertices
    lowlink = {}
    # Indices assigned to vertices during depth-first search
    index = {}
    # List to store the identified terminal subgraphs
    terminal_subgraphs = []

    def strongconnect(vertex):
        # Assign index and lowlink values to the vertex
        index[vertex] = index_counter[0]
        lowlink[vertex] = index_counter[0]
        index_counter[0] += 1
        stack.append(vertex)

        # Traverse the outgoing edges of the vertex
        neighbors = graph.neighbors(vertex, mode='OUT')
        for neighbor in neighbors:
            # Recursive call for unvisited neighbors
            if neighbor not in index:
                strongconnect(neighbor)
                # Update the lowlink value of the vertex based on the neighbor
                lowlink[vertex] = min(lowlink[vertex], lowlink[neighbor])
            # Check if the neighbor is on the stack, indicating a back edge in a cycle
            elif neighbor in stack:
                # Update the lowlink value of the vertex based on the neighbor's index
                lowlink[vertex] = min(lowlink[vertex], index[neighbor])

        # Check if the vertex is a root of a strongly connected component
        if lowlink[vertex] == index[vertex]:
            # Create a new subgraph for the terminal subgraph
            subgraph = set()
            while True:
                # Pop vertices from the stack and add them to the subgraph
                top = stack.pop()
                subgraph.add(top)
                # Stop when the root vertex is reached
                if top == vertex:
                    break
            # Add the subgraph to the list of terminal subgraphs
            terminal_subgraphs.append(subgraph)

    # Perform depth-first search for each unvisited vertex in the graph
    for vertex in graph.vs:
        if vertex.index not in index:
            strongconnect(vertex.index)

    return terminal_subgraphs

# This was also written by ChatGPT
def remove_vertices(graph, indices_to_remove):
    edges_to_remove = []
    for index in indices_to_remove:
        # Get the incident edges of the vertex
        edges_to_remove.extend(graph.incident(index, mode="ALL"))

    # Delete the edges associated with the vertices
    graph.delete_edges(edges_to_remove)

    # Delete the vertices
    graph.delete_vertices(indices_to_remove)

# This one was written by me, Lazycurler. Easy after ChatGPT did the hard part lol
def remove_all_terminal_subgraphs(graph):
    subgraphs = find_terminal_subgraphs(graph)
    sorted_subgraphs = sorted(subgraphs, key=len, reverse=True)
    #print(sorted_subgraphs)
    remove_me = sorted_subgraphs[1:]
    #print("Removing the following terminal subgraphs: ", remove_me)
    #print("Keeping: ", sorted_subgraphs[0])
    indices_to_remove = [element for s in remove_me for element in s]
    remove_vertices(graph, indices_to_remove)
    return remove_me


def main():
    # Example usage
    graph = ig.Graph(directed=True)
    graph.add_vertices(7)
    graph.add_edges([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (4, 5), (5, 6)])

    print("Before removal:")
    print(graph)

    _, ax = plt.subplots()
    ig.plot(graph, target=ax)
    plt.show()

    remove_all_terminal_subgraphs(graph)

    print("After removal:")
    print(graph)

    _, ax = plt.subplots()
    ig.plot(graph, target=ax)
    plt.show()

if __name__ == "__main__":
    main()
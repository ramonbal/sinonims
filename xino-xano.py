import re
import networkx as nx
import sys

def read_sinonims_file(filename):
    """
    Read synonyms file and return list of synonym groups.
    
    Args:
        filename (str): Path to the synonyms file
        
    Returns:
        list: List of synonym groups, where each group is a list of synonymous words
    """
    result = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            # Remove leading tag up to and including ':'
            line = re.sub(r'^.*?:', '', line)
            # Remove text in parentheses () and braces {}
            line = re.sub(r'\([^)]*\)', '', line)
            line = re.sub(r'\{[^}]*\}', '', line)
            # Split by commas and strip whitespace
            words = [w.strip() for w in line.split(',') if w.strip()]
            if words:
                result.append(words)
    return result

def build_synonym_graph(synonym_groups):
    """
    Build a graph from synonym groups where each word is connected to all other words
    in the same synonym group.
    
    Args:
        synonym_groups (list): List of synonym groups
        
    Returns:
        networkx.Graph: Graph with words as nodes and synonym relationships as edges
    """
    G = nx.Graph()
    for group in synonym_groups:
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                G.add_edge(group[i], group[j])
    return G

def find_paths_with_n_intermediate_nodes(graph, word1, word2, n_intermediate, max_paths=100):
    """
    Find all simple paths between two words with exactly n intermediate nodes.
    
    Args:
        graph (networkx.Graph): The synonym graph
        word1 (str): Source word
        word2 (str): Target word
        n_intermediate (int): Number of intermediate nodes (not counting source and target)
        max_paths (int): Maximum number of paths to return (for performance)
        
    Returns:
        list: List of paths, where each path is a list of words
        
    Raises:
        nx.NodeNotFound: If either word is not in the graph
        nx.NetworkXNoPath: If no path exists between the words
    """
    # Path length = number of intermediate nodes + 2 (source and target)
    target_path_length = n_intermediate + 2
    
    # Check if nodes exist in graph
    if word1 not in graph:
        raise nx.NodeNotFound(f"Node {word1} not in graph")
    if word2 not in graph:
        raise nx.NodeNotFound(f"Node {word2} not in graph")
    
    # Quick check if there's any path at all
    if not nx.has_path(graph, word1, word2):
        raise nx.NetworkXNoPath(f"No path between {word1} and {word2}")
    
    try:
        # Use generator and limit results for better performance
        paths_with_n_intermediate = []
        path_generator = nx.all_simple_paths(graph, word1, word2, cutoff=target_path_length)
        
        for path in path_generator:
            if len(path) == target_path_length:
                paths_with_n_intermediate.append(path)
                # Limit the number of paths to avoid infinite loops
                if len(paths_with_n_intermediate) >= max_paths:
                    break
        
        return paths_with_n_intermediate
    
    except nx.NodeNotFound:
        raise
    except nx.NetworkXNoPath:
        raise

def find_synonym_paths(filename, word1, word2, n_intermediate, max_paths=100):
    """
    Complete function to find paths between two words with n intermediate nodes.
    
    Args:
        filename (str): Path to the synonyms file
        word1 (str): Source word
        word2 (str): Target word
        n_intermediate (int): Number of intermediate nodes
        max_paths (int): Maximum number of paths to return (for performance)
        
    Returns:
        list: List of paths between the words
        
    Raises:
        FileNotFoundError: If the synonyms file doesn't exist
        nx.NodeNotFound: If either word is not in the synonym graph
        nx.NetworkXNoPath: If no path exists between the words
    """
    # Read synonyms and build graph
    synonym_groups = read_sinonims_file(filename)
    graph = build_synonym_graph(synonym_groups)
    
    # Find paths
    return find_paths_with_n_intermediate_nodes(graph, word1, word2, n_intermediate, max_paths)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <word1> <word2> <n_intermediate_nodes>")
        print(f"Example: python {sys.argv[0]} 'barat' 'econòmic' 3")
        sys.exit(1)

    w1 = sys.argv[1]
    w2 = sys.argv[2]
    try:
        n_intermediate = int(sys.argv[3])
    except ValueError:
        print("Error: n_intermediate_nodes must be an integer")
        sys.exit(1)

    try:
        paths = find_synonym_paths('sinonims.txt', w1, w2, n_intermediate)
        
        if paths:
            print(f'Camins de "{w1}" a "{w2}" amb {n_intermediate} nodes intermedis:')
            for i, path in enumerate(paths, 1):
                print(f'\t{i}. {" -> ".join(path)}')
            if len(paths) == 100:  # max_paths limit reached
                print(f'\t(Mostrant només els primers 100 camins)')
        else:
            print(f'No hi ha cami entre "{w1}" i "{w2}" amb {n_intermediate} nodes intermedis.')
            
    except FileNotFoundError:
        print("Error: No s'ha pogut trobar el fitxer 'sinonims.txt'")
    except nx.NetworkXNoPath:
        print(f'No hi ha cami entre "{w1}" i "{w2}".')
    except nx.NodeNotFound as e:
        print(f'Error: {str(e)}')
    except Exception as e:
        print(f'Error inesperat: {str(e)}')
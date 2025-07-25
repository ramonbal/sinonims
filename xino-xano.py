import re
import networkx as nx
import sys

def read_sinonims_file(filename):
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



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <word1> <word2>")
        sys.exit(1)

    w1 = sys.argv[1]
    w2 = sys.argv[2]

    try:
        sinonims = read_sinonims_file('sinonims.txt')
        G = nx.Graph()
        for group in sinonims:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    G.add_edge(group[i], group[j])

        paths = list(nx.all_simple_paths(G, w1, w2, cutoff=5))
        paths_len5 = [p for p in paths if len(p) == 5]
        if paths_len5:
            for p in paths_len5:
                print(f'\tcami de "{w1}" a "{w2}":\n\t\t {p}')
        else:
            print(f'No hi ha cami entre "{w1}" i "{w2}".')
    except nx.NetworkXNoPath:
        print(f'No hi ha cami entre "{w1}" i "{w2}".')
    except nx.NodeNotFound as e:
        print(str(e))
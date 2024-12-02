import sre_parse
import networkx as nx
import matplotlib.pyplot as plt


def visualize_pattern(parsed_pattern):
    graph = nx.DiGraph()
    node_id = [0]

    def add_node(label, parent=None):
        node_id[0] += 1
        graph.add_node(node_id[0], label=label)
        if parent is not None:
            graph.add_edge(parent, node_id[0])
        return node_id[0]

    def parse_subpattern(subpattern, parent=None):
        for token_type, value in subpattern:
            if token_type == sre_parse.LITERAL:
                label = f"LITERAL('{chr(value)}')"
                add_node(label, parent)
            elif token_type == sre_parse.BRANCH:
                branch_node = add_node("BRANCH", parent)
                for branch in value[1]:
                    parse_subpattern(branch, branch_node)
            elif token_type == sre_parse.IN:
                in_node = add_node("IN", parent)
                for sub_token in value:
                    parse_subpattern([sub_token], in_node)
            elif token_type == sre_parse.CATEGORY:
                label = f"CATEGORY({value})"
                add_node(label, parent)
            elif token_type == sre_parse.MAX_REPEAT:
                min_repeat, max_repeat, sub = value
                label = f"REPEAT({min_repeat},{max_repeat})"
                repeat_node = add_node(label, parent)
                parse_subpattern(sub, repeat_node)
            elif token_type == sre_parse.SUBPATTERN:
                subpattern_node = add_node(f"SUBPATTERN({value[0]})", parent)
                parse_subpattern(value[3], subpattern_node)
            elif token_type == sre_parse.AT:
                label = f"AT({value})"
                add_node(label, parent)
            elif token_type == sre_parse.ASSERT:
                assert_node = add_node("ASSERT", parent)
                parse_subpattern(value[1], assert_node)
            elif token_type == sre_parse.ASSERT_NOT:
                assert_not_node = add_node("ASSERT_NOT", parent)
                parse_subpattern(value[1], assert_not_node)
            elif token_type == sre_parse.RANGE:
                label = f"RANGE({value[0]}-{value[1]})"
                add_node(label, parent)

    root = add_node("ROOT")
    parse_subpattern(parsed_pattern, root)

    pos = nx.spring_layout(graph, seed=42)
    labels = nx.get_node_attributes(graph, 'label')
    nx.draw(graph, pos, with_labels=True, labels=labels, node_size=2500, node_color="lightblue", font_size=9, font_color="black", edge_color='gray')
    plt.show()


if __name__ == "__main__":
    pattern = r"^(?:[a-zA-Z]+|\d{1,3})(?=\d+)[a-z]*\b$"
    parsed_pattern = sre_parse.parse(pattern)
    print("正则表达式解析成功，正在生成可视化...")
    visualize_pattern(parsed_pattern)

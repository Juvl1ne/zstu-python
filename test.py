import sre_parse
from graphviz import Digraph

def visualize_regex(pattern):
    # 创建一个Graphviz的Digraph对象，用于生成有向图
    dot = Digraph(comment='Regex Visualization', format='png')
    # 设置图的方向为从左到右，并调整大小
    dot.attr(rankdir='LR', size='12,8')

    # 添加开始节点和结束节点
    dot.node('Start', 'Start', shape='circle', color='green')
    dot.node('End', 'End', shape='doublecircle', color='red')

    # 解析正则表达式模式
    parsed_pattern = sre_parse.parse(pattern)
    print(parsed_pattern)
    counter = 0

    def add_nodes(dot, parent, parsed, counter):
        # 用于存储匹配的字面字符
        matched_string = ""
        for token in parsed:
            if isinstance(token, tuple):
                token_type, value = token
                token_type = str(token_type)

                if token_type == 'LITERAL':
                    # 将字面字符追加到matched_string中
                    matched_string += chr(value)
                elif token_type == 'SUBPATTERN':
                    # 如果在SUBPATTERN之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理子模式（分组）
                    group_number, flags, content_offset, inner_tokens = value
                    label = f'Group {group_number}'
                    node_id = f'node{counter}'
                    dot.node(node_id, label, shape='ellipse', color='purple')
                    dot.edge(parent, node_id)
                    counter += 1
                    sub_counter = add_nodes(dot, node_id, inner_tokens, counter)
                    counter = sub_counter
                elif token_type in ['MAX_REPEAT', 'MIN_REPEAT']:
                    # 如果在MAX_REPEAT/MIN_REPEAT之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理重复次数
                    min_count, max_count, inner_tokens = value
                    repeat_label = f'Repeat {min_count} to {max_count} times'
                    node_id = f'node{counter}'
                    dot.node(node_id, repeat_label, shape='diamond', color='pink')
                    dot.edge(parent, node_id)
                    counter += 1
                    sub_counter = add_nodes(dot, node_id, inner_tokens, counter)
                    counter = sub_counter
                elif token_type == 'ANY':
                    # 如果在ANY之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理任意字符
                    node_id = f'node{counter}'
                    dot.node(node_id, 'Any Character', shape='box', color='orange')
                    dot.edge(parent, node_id)
                    counter += 1
                elif token_type == 'CATEGORY':
                    # 如果在CATEGORY之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理字符类别（例如数字）
                    category_type = value
                    if category_type == sre_parse.CATEGORY_DIGIT:
                        node_id = f'node{counter}'
                        dot.node(node_id, 'Digit', shape='box', color='yellow')
                        dot.edge(parent, node_id)
                        counter += 1
                    elif category_type == sre_parse.CATEGORY_WORD:
                        node_id = f'node{counter}'
                        dot.node(node_id, 'Word', shape='box', color='yellow')
                        dot.edge(parent, node_id)
                        counter += 1
                    elif category_type == sre_parse.CATEGORY_SPACE:
                        node_id = f'node{counter}'
                        dot.node(node_id, 'Space', shape='box', color='yellow')
                        dot.edge(parent, node_id)
                        counter += 1
                    else:
                        node_id = f'node{counter}'
                        dot.node(node_id, str(category_type), shape='box', color='yellow')
                        dot.edge(parent, node_id)
                        counter += 1
                elif token_type == 'BRANCH':
                    # 如果在BRANCH之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理分支
                    branch_type, branches = value
                    branch_labels = []
                    for i, branch in enumerate(branches):
                        branch_node_id = f'branch{i}_{counter}'
                        dot.node(branch_node_id, f'Branch {i}', shape='parallelogram', color='cyan')
                        dot.edge(parent, branch_node_id)
                        sub_counter = add_nodes(dot, branch_node_id, branch, counter)
                        counter = sub_counter
                        branch_labels.append(branch_node_id)
                    parent = branch_labels[-1]
                elif token_type == 'ASSERT':
                    # 如果在ASSERT之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理断言
                    assert_type, _ = value
                    assert_label = ''
                    if assert_type == sre_parse.ASSERT:
                        assert_label = 'Assert Position'
                    elif assert_type == sre_parse.ASSERT_NOT:
                        assert_label = 'Assert Not Position'
                    elif assert_type == sre_parse.AT_BEGINNING:
                        assert_label = 'At Beginning'
                    elif assert_type == sre_parse.AT_END:
                        assert_label = 'At End'
                    elif assert_type == sre_parse.AT_BOUNDARY:
                        assert_label = 'At Boundary'
                    elif assert_type == sre_parse.AT_NON_BOUNDARY:
                        assert_label = 'At Non-Boundary'
                    node_id = f'node{counter}'
                    dot.node(node_id, assert_label, shape='hexagon', color='blue')
                    dot.edge(parent, node_id)
                    counter += 1
                elif token_type == 'AT':
                    # 如果在AT之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理位置锚点
                    at_type = value
                    at_label = ''
                    if at_type == sre_parse.AT_BEGINNING:
                        at_label = 'At Beginning'
                    elif at_type == sre_parse.AT_END:
                        at_label = 'At End'
                    elif at_type == sre_parse.AT_BOUNDARY:
                        at_label = 'At Boundary'
                    elif at_type == sre_parse.AT_NON_BOUNDARY:
                        at_label = 'At Non-Boundary'
                    node_id = f'node{counter}'
                    dot.node(node_id, at_label, shape='hexagon', color='blue')
                    dot.edge(parent, node_id)
                    counter += 1
                elif token_type == 'IN':
                    # 如果在IN之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理字符集合
                    set_items = value
                    set_label = ', '.join([str(item) for item in set_items])
                    node_id = f'node{counter}'
                    dot.node(node_id, f'Set: [{set_label}]', shape='polygon', color='limegreen')
                    dot.edge(parent, node_id)
                    counter += 1
                elif token_type == 'NEGATE':
                    # 如果在NEGATE之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理否定字符类
                    negate_items = value
                    negate_label = ', '.join([str(item) for item in negate_items])
                    node_id = f'node{counter}'
                    dot.node(node_id, f'Negate Set: [{negate_label}]', shape='polygon', color='salmon')
                    dot.edge(parent, node_id)
                    counter += 1
                elif token_type == 'GROUPREF':
                    # 如果在GROUPREF之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理引用之前的分组
                    group_ref = value
                    node_id = f'node{counter}'
                    dot.node(node_id, f'Reference Group {group_ref}', shape='octagon', color='violet')
                    dot.edge(parent, node_id)
                    counter += 1
                elif token_type == 'RANGE':
                    # 如果在RANGE之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理字符范围
                    range_start, range_end = value
                    node_id = f'node{counter}'
                    dot.node(node_id, f'Range {chr(range_start)}-{chr(range_end)}', shape='pentagon', color='olive')
                    dot.edge(parent, node_id)
                    counter += 1
                elif token_type == 'CHARSET':
                    # 如果在CHARSET之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 处理字符集
                    charset_items = value
                    charset_label = ', '.join([str(item) for item in charset_items])
                    node_id = f'node{counter}'
                    dot.node(node_id, f'Charset: [{charset_label}]', shape='rectangle', color='turquoise')
                    dot.edge(parent, node_id)
                    counter += 1
                else:
                    # 如果在未知令牌类型之前有匹配的字符串，则创建一个节点
                    if matched_string:
                        matched_node_id = f'node{counter}'
                        dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
                        dot.edge(parent, matched_node_id)
                        parent = matched_node_id
                        counter += 1
                        matched_string = ""

                    # 其他令牌类型
                    node_id = f'node{counter}'
                    dot.node(node_id, str(token_type), shape='box', color='gray')
                    dot.edge(parent, node_id)
                    counter += 1

        # 如果在处理完所有令牌后仍有剩余的匹配字符串，则创建一个节点
        if matched_string:
            matched_node_id = f'node{counter}'
            dot.node(matched_node_id, f'Matched String: "{matched_string}"', shape='box', color='lightgreen')
            dot.edge(parent, matched_node_id)
            counter += 1

        return counter

    # 从开始节点开始添加所有节点
    counter = add_nodes(dot, 'Start', parsed_pattern, counter)
    # 连接最后一个节点到结束节点
    dot.edge(f'node{counter - 1}', 'End')

    # 渲染图并保存为PNG文件
    dot.render('regex_visualization', cleanup=True)
    print("Regex visualization image has been generated!")

# 示例正则表达式
regex_pattern = r'(Trident/.*; rv:)(\d+)'
visualize_regex(regex_pattern)




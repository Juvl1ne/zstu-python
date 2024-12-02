from railroad import Diagram, Choice, Sequence, Terminal, NonTerminal, Optional, OneOrMore, ZeroOrMore
import sre_parse
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*module 'sre_parse' is deprecated")

def visualize_regex_railroad(pattern):
    # 解析正则表达式模式
    parsed_pattern = sre_parse.parse(pattern)
    print(parsed_pattern)

    def build_diagram(parsed):
        elements = []
        current_literals = []

        for token in parsed:
            if isinstance(token, tuple):
                token_type, value = token
                token_type = str(token_type)

                if token_type == 'LITERAL':
                    current_literals.append(chr(value))
                else:
                    if current_literals:
                        elements.append(Terminal(''.join(current_literals)))
                        current_literals = []
                    if token_type == 'SUBPATTERN':
                        group_number, flags, content_offset, inner_tokens = value
                        elements.append(NonTerminal(f'Group {group_number}'))
                        elements.extend(build_diagram(inner_tokens))
                    elif token_type in ['MAX_REPEAT', 'MIN_REPEAT']:
                        min_count, max_count, inner_tokens = value
                        if min_count == 0 and max_count == 1:
                            elements.append(Optional(Sequence(*build_diagram(inner_tokens))))
                        elif min_count == 1 and max_count == 1:
                            elements.extend(build_diagram(inner_tokens))
                        elif min_count == 0 :
                            elements.append(ZeroOrMore(Sequence(*build_diagram(inner_tokens))))
                        elif min_count == 1 :
                            elements.append(OneOrMore(Sequence(*build_diagram(inner_tokens))))
                        else:
                            # 设置一个合理的最大重复次数
                            max_repeats = min(max_count - min_count + 1, 5)  # 例如，最多生成10个重复项
                            elements.append(Choice(min_count, *([Sequence(*build_diagram(inner_tokens))] * max_repeats)))
                    elif token_type == 'ANY':
                        elements.append(Terminal('any character'))
                    elif token_type == 'CATEGORY':
                        category_type = value
                        if category_type == sre_parse.CATEGORY_DIGIT:
                            elements.append(Terminal(r'\d'))
                        elif category_type == sre_parse.CATEGORY_WORD:
                            elements.append(Terminal(r'\w'))
                        elif category_type == sre_parse.CATEGORY_SPACE:
                            elements.append(Terminal(r'\s'))
                        else:
                            elements.append(Terminal(str(category_type)))
                    elif token_type == 'BRANCH':
                        branches = value[1]
                        non_empty_branches = [branch for branch in branches if branch]
                        if not non_empty_branches:
                            continue
                        choices = [Sequence(*build_diagram(branch)) for branch in non_empty_branches]
                        elements.append(Choice(0, *choices))
                    elif token_type == 'ASSERT':
                        assert_type, _ = value
                        if assert_type == sre_parse.ASSERT:
                            elements.append(Terminal(r'(?=...)'))
                        elif assert_type == sre_parse.ASSERT_NOT:
                            elements.append(Terminal(r'(?!...)'))
                        elif assert_type == sre_parse.AT_BEGINNING:
                            elements.append(Terminal(r'^'))
                        elif assert_type == sre_parse.AT_END:
                            elements.append(Terminal(r'$'))
                        elif assert_type == sre_parse.AT_BOUNDARY:
                            elements.append(Terminal(r'\b'))
                        elif assert_type == sre_parse.AT_NON_BOUNDARY:
                            elements.append(Terminal(r'\B'))
                    elif token_type == 'AT':
                        at_type = value
                        if at_type == sre_parse.AT_BEGINNING:
                            elements.append(Terminal(r'^'))
                        elif at_type == sre_parse.AT_END:
                            elements.append(Terminal(r'$'))
                        elif at_type == sre_parse.AT_BOUNDARY:
                            elements.append(Terminal(r'\b'))
                        elif at_type == sre_parse.AT_NON_BOUNDARY:
                            elements.append(Terminal(r'\B'))
                    elif token_type == 'IN':
                        set_items = value
                        set_elements = []
                        for item in set_items:
                            if isinstance(item, tuple) and item[0] == 'RANGE':
                                set_elements.append(Terminal(f'{chr(item[1][0])}-{chr(item[1][1])}'))
                            elif isinstance(item, tuple):
                                set_elements.extend(build_diagram([item]))
                            else:
                                set_elements.append(Terminal(chr(item)))
                        elements.append(Choice(0, *set_elements))
                    elif token_type == 'NEGATE':
                        negate_items = value
                        negate_elements = []
                        for item in negate_items:
                            if isinstance(item, tuple) and item[0] == 'RANGE':
                                negate_elements.append(Terminal(f'{chr(item[1][0])}-{chr(item[1][1])}'))
                            else:
                                negate_elements.append(Terminal(chr(item[1])))
                        elements.append(Choice(0, *negate_elements))
                    elif token_type == 'GROUPREF':
                        group_ref = value
                        elements.append(Terminal(f'\\{group_ref}'))
                    elif token_type == 'RANGE':
                        range_start, range_end = value
                        elements.append(Terminal(f'{chr(range_start)}-{chr(range_end)}'))
                    elif token_type == 'CHARSET':
                        charset_items = value
                        charset_elements = []
                        for item in charset_items:
                            if isinstance(item, tuple) and item[0] == 'RANGE':
                                charset_elements.append(Terminal(f'{chr(item[1][0])}-{chr(item[1][1])}'))
                            else:
                                charset_elements.append(Terminal(chr(item[1])))
                        elements.append(Choice(0, *charset_elements))
                    else:
                        elements.append(Terminal(str(token_type)))

        if current_literals:
            elements.append(Terminal(''.join(current_literals)))

        return elements

    diagram_elements = build_diagram(parsed_pattern)
    diagram = Diagram(*diagram_elements)

    # 将生成的SVG保存到文件
    with open('regex_visualization.svg', 'w') as f:
        diagram.writeSvg(f.write)

    print("Regex visualization SVG file has been generated!")

if __name__ == '__main__':
    # 示例正则表达式
    regex_pattern = r'Version\/([\d.]+)( Mobile\/.+?)? Safari\/\d+'
    visualize_regex_railroad(regex_pattern)
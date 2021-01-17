from __future__ import annotations
import itertools


class FPNode(object):
    '''
    FPtree的节点
    '''

    def __init__(self, value, count, parent):
        '''

        :param value: 节点包含的值
        :param count: 值出现的次数
        :param parent: 父节点
        '''
        self.value = value
        self.count = count
        self.parent = parent
        self.neighbor = None
        self.children = []

    def has_child(self, value) -> bool:
        '''
        该节点中的子节点中是否包含value

        :param value:
        :return:
        '''
        for child in self.children:
            if child.value == value:
                return True

        return False

    def get_child(self, value):
        '''
        返回包含value的一个子节点

        :param value:
        :return:
        '''
        for node in self.children:
            if node.value == value:
                return node

        return None

    def add_child(self, value) -> FPNode:
        '''
        添加一个子节点，并返回该子节点

        :param value: 赋给子节点的值
        :return:
        '''
        child = FPNode(value, 1, self)
        self.children.append(child)
        return child

    def __repr__(self):
        return "{}:{}".format(self.value, self.count)


class FPTree(object):
    '''
    FPtree类

    当root_val为空时表示FPtree；
    root_val非空时表示FPtree的子树，root_val为条件模式基中的叶节点值
    '''

    def __init__(self, transactions, threshold, root_value, root_count):
        '''

        :param transactions: 所有事务
        :param threshold:
        :param root_value: 根节点值，用于区别FPtree和子树
        :param root_count: 根节点次数
        '''
        self.root = FPNode(root_value, root_count, None)

        self.item2sup = dict()
        self.header_tab = dict()

        self.item_filter(transactions, threshold)
        self.build_header_table()

        self.build_fptree(transactions)

    def item_filter(self, transactions: list, threshold) -> None:
        '''
        筛选sup大于阈值的那些item，记录在item2sup中

        :param transactions:
        :param threshold:
        :return:
        '''
        for transaction in transactions:
            for item in transaction:
                if item in self.item2sup:
                    self.item2sup[item] += 1
                else:
                    self.item2sup[item] = 1

        for key in list(self.item2sup.keys()):
            if self.item2sup[key] < threshold:
                del self.item2sup[key]

    def build_header_table(self) -> None:
        '''
        构建空header tab

        :param frequent: item2sup
        :return:
        '''
        for key in self.item2sup.keys():
            self.header_tab[key] = None

    def build_fptree(self, transactions) -> None:
        '''
        构建PFtree和header_tab

        :param transactions:
        :param frequent:
        :return:
        '''
        for transaction in transactions:
            sorted_items = [x for x in transaction if x in self.item2sup]
            sorted_items.sort(key=lambda x: self.item2sup[x], reverse=True)
            if len(sorted_items) > 0:
                self.insert_tree(sorted_items, self.root)

    def insert_tree(self, items: list, node: FPNode) -> None:
        '''
        将一条事务中大于sup阈值的items插入FPtree

        :param items: 满足sup阈值的倒序item列表
        :param node: 起始插入节点
        :return:
        '''
        first = items[0]  # sup最高的item
        child = node.get_child(first)

        # item是否存在于子节点中
        if child is not None:
            child.count += 1
        else:  # 不存在则新建分支
            child = node.add_child(first)

            # 更新项头表
            if self.header_tab[first] is None:
                self.header_tab[first] = child
            else:
                current = self.header_tab[first]
                while current.neighbor is not None:
                    current = current.neighbor
                current.neighbor = child

        # 递归插入
        remaining_items = items[1:]
        if remaining_items:
            self.insert_tree(remaining_items, child)

    def tree_has_single_path(self, node):
        '''
        判断树是否单分支

        :param node:
        :return:
        '''
        num_children = len(node.children)
        if num_children > 1:
            return False
        elif num_children == 0:
            return True
        else:
            return True and self.tree_has_single_path(node.children[0])

    def mine_patterns(self, threshold):
        '''
        在FPtree中挖掘频繁项

        :param threshold: 支持度阈值
        :return:
        '''
        if self.tree_has_single_path(self.root):  # 单分支FPtree
            return self.generate_pattern_list()
        else:
            return self.zip_patterns(self.mine_sub_trees(threshold))

    def zip_patterns(self, patterns):
        '''
        当对子树调用mine时，频繁项集还需要加上原始叶子节点（即根节点值）

        :param patterns:
        :return:
        '''
        base_val = self.root.value

        if base_val is not None:
            new_patterns = dict()
            for key in patterns.keys():
                new_patterns[tuple(sorted(list(key) + [base_val]))] = patterns[key]

            return new_patterns

        return patterns

    def generate_pattern_list(self):
        '''
        生成频繁项集

        :return:
        '''
        patterns = dict()
        items = self.item2sup.keys()

        # 可根据root的value是否是None来判断是否是条件FPtree
        if self.root.value is None:  # FPtree
            suffix_value = []
        else:  # 条件FPtree
            suffix_value = [self.root.value]
            patterns[tuple(suffix_value)] = self.root.count

        for i in range(1, len(items) + 1):
            for subset in itertools.combinations(items, i):  # 生成item的全组合
                pattern = tuple(sorted(list(subset) + suffix_value))
                patterns[pattern] = min([self.item2sup[x] for x in subset])

        return patterns

    def mine_sub_trees(self, threshold) -> dict:
        '''
        多分支FPtree挖掘频繁项集

        :param threshold:
        :return:
        '''
        fp_sets = dict()    # 频繁项集
        mining_order = sorted(self.item2sup.keys(), key=lambda x: self.item2sup[x])  # 由sup最小的item开始

        for item in mining_order:    # 遍历header_tab中的每一个item
            leaf_nodes = list()
            conditional_tree_input = list()
            node = self.header_tab[item]

            # 根据路径找到item的所有节点，即sub_tree的所有叶节点
            while node is not None:
                leaf_nodes.append(node)
                node = node.neighbor

            for leaf_node in leaf_nodes:
                frequency = leaf_node.count  # 以叶节点的次数为准
                bottom_up_path = list()  # 自底向上的路径（不包括叶节点）

                parent = leaf_node.parent
                while parent.parent is not None:
                    bottom_up_path.append(parent.value)
                    parent = parent.parent

                for i in range(frequency):  # 叶节点有多少次就使用多少条路径来构造子树，不包括叶节点
                    conditional_tree_input.append(bottom_up_path)

            # 构建子树，子树中所有节点的次数等于叶节点的总次数，在子树中挖掘频繁项集
            subtree = FPTree(conditional_tree_input, threshold, item, self.item2sup[item])
            subtree_patterns = subtree.mine_patterns(threshold)

            # 加入频繁项集
            for pattern in subtree_patterns.keys():
                if pattern in fp_sets:
                    fp_sets[pattern] += subtree_patterns[pattern]
                else:
                    fp_sets[pattern] = subtree_patterns[pattern]

        return fp_sets


def fp_growth(transactions: list, sup_thresh):
    '''
    fp-growth算法

    :param transactions: 输入事务
    :param sup_thresh: 支持度阈值
    :return:
    '''
    tree = FPTree(transactions, sup_thresh, None, None)
    return tree.mine_patterns(sup_thresh)


def generate_association_rules(patterns, confidence_threshold):
    """
    Given a set of frequent itemsets, return a dict
    of association rules in the form
    {(left): ((right), confidence)}
    """
    rules = {}
    for itemset in patterns.keys():
        upper_support = patterns[itemset]

        for i in range(1, len(itemset)):
            for antecedent in itertools.combinations(itemset, i):
                antecedent = tuple(sorted(antecedent))
                consequent = tuple(sorted(set(itemset) - set(antecedent)))

                if antecedent in patterns:
                    lower_support = patterns[antecedent]
                    confidence = float(upper_support) / lower_support

                    if confidence >= confidence_threshold:
                        rules[antecedent] = (consequent, confidence)

    return rules

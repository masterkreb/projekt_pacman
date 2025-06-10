class NodeGroup(object):
    def __init__(self, level):
        self.level = level
        self.nodesLUT = {}
        self.nodeSymbols = ['+', 'p', 'n']
        self.pathSymbols = ['.', '|', 'p']
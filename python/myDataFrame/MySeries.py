class MySeries:
    def __init__(self, values, index = None):
        self.s_dict = {}
        if isinstance(values, dict):
            for key in values.keys():
                self.s_dict[key] = values[key]
        elif isinstance(values, list) and index == None:
            for i in range(len(values)):
                self.s_dict[i] = values[i]
        elif isinstance(values, list) and isinstance(index, list):
            if len(values) == len(index):
                for i in range(len(index)):
                    self.s_dict[index[i]] = values[i]
            else:
                raise ValueError("error: value-index mismatch!")
        elif not isinstance(index, list):
            raise TypeError("error: index must be a list of indexes")
        elif not isinstance(values, list):
            raise TypeError("error: argument(s) must be of type list")
        else:
            raise TypeError("error: arguments of invalid type(s)")


    def min(self):
        return min(self.s_dict.values())


    def max(self):
        return max(self.s_dict.values())


    def mean(self):
        summation = 0
        for key in self.s_dict.keys():
            if not (isinstance(self.s_dict[key], int) or isinstance(self.s_dict[key], float)):
                return None
            else:
                summation += self.s_dict[key]
        return summation / len(self.s_dict)


    def print(self):
        for key in self.s_dict.keys():
            print("{:<15} {:<15}".format(key, self.s_dict[key]))


    def item_at_ind(self, index):
        return self.s_dict[index]
        

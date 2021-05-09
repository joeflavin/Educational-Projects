class MyDataFrame:
    """ MyDataFrame uses MySeries Class """
    def __init__(self, dictionary, index = None):
        self.df_dict = {}
        if isinstance(dictionary, dict) and index == None:
            for key in dictionary.keys():
                self.df_dict[key] = MySeries(dictionary[key])
        elif isinstance(dictionary, dict) and isinstance(index, list):
            for key in dictionary.keys():
                if len(dictionary[key]) != len(index):
                    raise ValueError("error: value-index mismatch!")
            for key in dictionary.keys():
                self.df_dict[key] = MySeries(dictionary[key], index)
        else:
            raise TypeError("error: input arguments must be a dictionary and optionally an indexing list")


    def print(self):
        """ Prints MyDataFrame instance """
        columns = list(self.df_dict.keys())
        print("{:<15} {:<15} {:<15} {:<15} {:<15} {:<15}".format('',*columns))
        column = columns[0]
        for subkey in self.df_dict[column].s_dict.keys():
            row = subkey
            values = []
            for columnkey in self.df_dict.keys():
                values.append(self.df_dict[columnkey].s_dict[row])
            print("{:<15} {:<15} {:<15} {:<15} {:<15} {:<15}".format(row, *values))


    def sort_values(self, key):
        """ Sorts a Data Frame instance in-place by key """
        if key not in self.df_dict.keys():
            raise ValueError("error: given key not found in data frame instance")
        column = self.df_dict[key].s_dict
        sorted_keys = sorted(column, key=column.get)
        for columnkey in self.df_dict.keys():
            sorted_column = {}
            for rowkey in sorted_keys:
                sorted_column[rowkey] = self.df_dict[columnkey].s_dict[rowkey]
            self.df_dict[columnkey].s_dict.clear()
            for key in sorted_column.keys():
                self.df_dict[columnkey].s_dict[key] = sorted_column[key]


    def min(self):
        for key in self.df_dict.keys():
            minimum = self.df_dict[key].min()
            if type(minimum) == str:
                print("{:<15} {}".format(key, minimum))
            else:
                print("{:<15} {:8.2f}".format(key, minimum))


    def max(self):
        for key in self.df_dict.keys():
            maximum = self.df_dict[key].max()
            if type(maximum) == str:
                print("{:<15} {}".format(key, maximum))
            else:
                print("{:<15} {:8.2f}".format(key, maximum))


    def mean(self):
        for key in self.df_dict.keys():
            average = self.df_dict[key].mean()
            if average == None:
                continue
            else:
                print("{:<15} {:8.2f}".format(key, average))

                

class Flag: 
    def __init__(self):
        self.flag = False 

    def set_value(self, value: bool):
        if isinstance(value, bool):
            self.flag = value
        else:
            raise ValueError("The value must be a boolean.")

    def get_value (self): 
        return self.flag
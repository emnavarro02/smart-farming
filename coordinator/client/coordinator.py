class Coordinator(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id
    
    @name.setter
    def name(self,name):
        self.__name = name
    
    @id.setter
    def id(self,id):
        self.__id = id

    @id.getter
    def getId(self):
        return self.__id

    @name.getter
    def getName(self):
        return self.__name
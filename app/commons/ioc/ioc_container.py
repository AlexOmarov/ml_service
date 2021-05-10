class IocContainer(object):
    beans = {}

    def __init__(self):
        pass

    def get_bean(self, clazz):
        return self.beans[clazz]

    def set_bean(self, clazz, bean):
        self.beans[clazz] = bean

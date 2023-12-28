# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: cairowang

import sys
from typing import Any

class _const:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in self.__dict__:
            raise self.ConstError('can not change const %s' % __name)
        if not __name.isupper():
            raise self.ConstCaseError('const name %s is not all uppercase' % __name)
        self.__dict__[__name] = __value

sys.modules[__name__] = _const() 
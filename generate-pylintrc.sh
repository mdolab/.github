#!/usr/bin/sh

pylint \
--disable all \
--enable basic,classes,exceptions,miscellaneous,newstyle,refactoring,similarities,stdlib,string,typecheck,variables \
--disable c-extension-no-member,anomalous-backslash-in-string,missing-module-docstring,missing-class-docstring,missing-function-docstring,fixme \
--argument-naming-style=any \
--argument-naming-style=any \
--attr-naming-style=any \
--function-naming-style=any \
--method-naming-style=any \
--module-naming-style=any \
--variable-naming-style=any \
--class-naming-style=any \
--generate-rcfile \
> .pylintrc

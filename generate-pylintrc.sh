#!/usr/bin/sh

pylint \
--disable all \
--enable basic,classes,exceptions,imports,newstyle,refactoring,stdlib,string,typecheck,variables \
--disable C,R,I,unspecified-encoding,protected-access,import-error \
--generate-rcfile \
> .pylintrc

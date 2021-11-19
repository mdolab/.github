#!/usr/bin/sh

pylint \
--disable all \
--enable basic,classes,exceptions,newstyle,refactoring,stdlib,string,typecheck,variables \
--disable C,R,I,unspecified-encoding,protected-access \
--generate-rcfile \
> .pylintrc

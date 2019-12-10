# prmake
Preprocessor to build more powerful makefiles

Free to reuse and modify under the terms of the GPL.

prmake has a single source: prmake.py
To use, download, put it in a directory of your choice (let's call it MYDIR).
You can then call it with "python MYDIR/prmake.py"
but I like to alias this to the command prmake, i.e. add this line to .bashrc:

alias prmake='python MYDIR/prmake.py'

You can then invoke "prmake" just as you would normally run "make".

For usage, type:

prmake -h

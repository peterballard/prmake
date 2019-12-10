# prmake
Preprocessor to build more powerful makefiles

Free to reuse and modify under the terms of the GPL.

Installation
------------
prmake has a single source: prmake.py
To use, download, put it in a directory of your choice (let's call it MYDIR).
You can then call it with "python MYDIR/prmake.py"
but I like to alias this to the command prmake, i.e. add this line to .bashrc:

alias prmake='python MYDIR/prmake.py'

You can then invoke "prmake" just as you would normally run "make".

Usage
-----
In prmake, a Makefile has two additional commands:

    #begincode <commands>

and

    #endcode

<commands> need not be a single word, but usually it is, e.g. "python".

The text between the #begincode and #endcode lines is put in a temporary file,
and then the command

     <commands> <temporary_file>

is run as a Python subprocess,
with its standard output piped to the post-processed Makefile.
Everything else in the Makefile is piped unchanged to the post-processed Makefile.

So if you have 100 very similar targets, and "make" wildcards are not suitable,
you simply generate them using a Python loop.

Then you run "prmake" just as you would "make", e.g.

    prmake myfile.txt

License
-------
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

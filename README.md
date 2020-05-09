# prmake
Preprocessor to build more powerful makefiles

(c) Peter Ballard, 2019, 2020

Free to reuse and modify under the terms of the GPLv3 (see "License" below).

Version
-------
Version 0.3 was released in May 2020. It is a major change, breaking compatibility with Versions 0.1 and 0.2

Earlier versions are retrospectively named 0.2 (March 2020) and 0.1 (December 2019),

Installation
------------
prmake has a single source: prmake.py

To use: download it, and put it in a directory of your choice (let's call it MYDIR).
You can then call it with "python MYDIR/prmake.py"
but I like to alias this to the command prmake, i.e. add this line to .bashrc:

    alias prmake='python MYDIR/prmake.py'

Overview
--------
"make" ( https://www.gnu.org/software/make/ ) is a great tool, but it is hard to make complicated rules.
prmake makes it easier to write complicated makefile rules,
without requiring any change to the simple makefile rules.

prmake processes a prfile (usually called "Makefile.pr")
in a high level language (such as Python),
then creates a post-processed Makefile (usually called "Makefile"),
then invokes "make" on that post-processed Makefile.

So e.g. if you have 100 very similar targets, and "make" wildcards are not suitable,
prmake will generate them using a loop in Python (or any other interpreted language).

Assuming you have set up the alias described above, you then run "prmake" just as you would "make", e.g.

    prmake myfile.dat

prmake is designed to be novice friendly:
- Any makefile can be a prfile.
  So start with an existing makefile as your prfile, and add as much or as little specialised code as you want.
- prmake by default writes its output to "Makefile",
  so a makefile is where a non-prmake-user would expect to find it.
  This means one user can use prmake without requiring all future users to use prmake.
- prmake only overwrites a makefile which has been created by prmake,
  so this safeguards against it blowing away source code.

Usage
-----
In prmake, a prfile has two additional commands:

    #begincode <commands>

and

    #endcode

<commands> need not be a single word, but usually it is, e.g. "python".
The text between the #begincode and #endcode lines is put in a temporary file,
and then the command

    <commands> <temporary_file>

is run as a Python subprocess,
with its standard output piped to the makefile.
Everything else in the prfile is piped unchanged to the makefile.

    Usage: prmake [options]    or    python prmake.py [options]
    The following options are processed by prmake:
    -f <Makefile>         specifies the makefile
    --file=<Makefile>     specifies the makefile
    --makefile=<Makefile> specifies the makefile
    -h displays this message
    --make=<NAME> specifies the "make" executable, default is "make"
    --prfile=<PRFILE> specifies prfile name. Overrides --prext. Defaults in order: "GNUmakefile.pr", "makefile.pr", "Makefile.pr".
    --prext=<PREXT> specifies extension of prfiles. Default is ".pr"
    i.e. makefile usually called "Makefile", prfile usually called "Makefile.pr"
    -prforce=1 forces the rebuild of the post-processed Makefile (normally only remade if out of date)
    --prkeep=1 means temporary files are kept (and their locations printed)
    All other command line arguments are passed to "make".

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

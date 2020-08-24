# prmake
Preprocessor to build more powerful makefiles

(c) Peter Ballard, 2019, 2020

Free to reuse and modify under the terms of the GPLv3 (see "License" below).

Version
-------
Current version is 0.3.1, 24-Aug-2020.
This is a minor change from 0.3, adding a little more information to the comment header in a Makefile.

Version 0.3 was released in May 2020. It is a major change, breaking compatibility with Versions 0.1 and 0.2

Earlier versions are retrospectively named 0.2 (March 2020) and 0.1 (December 2019),

Installation
------------
prmake has a single source: prmake.py

To use: download it, and put it in a directory of your choice (let's call it MYDIR).
You can then call it with `python MYDIR/prmake.py`
but I like to alias this to the command prmake, i.e. add this line to .bashrc:

    alias prmake='python MYDIR/prmake.py'

Description
-----------
make ( https://www.gnu.org/software/make/ ) is a great tool, but it is hard to make complicated rules.
prmake makes it easier to write complicated makefile rules,
without requiring any change to the simple makefile rules.

prmake processes a prfile (usually called `Makefile.pr`)
in a high level language (such as Python),
then creates a post-processed Makefile (usually called `Makefile`),
then invokes `make` on that post-processed Makefile.

So e.g. if you have 100 targets which are very similar, but not similar enough to use "make" wildcards,
prmake can generate them using a loop in Python (or any other interpreted language).

Assuming you have set up the alias described above, you then run "prmake" just as you would "make", e.g.

    prmake myfile.dat

prmake is designed to be novice friendly:
- All GNU make flags are supported.
- Any makefile can be a prfile. So you can start with an existing makefile as your prfile,
  and add as much or as little specialised code as you want.
- prmake by default writes its output to `Makefile`,
  so a makefile is where a non-prmake-user would expect to find it.
  This means one user can use prmake without requiring all future users to use prmake.
- prmake only overwrites a makefile which has been created by prmake,
  so this safeguards against it blowing away source code.
- If no prfile is present, prmake runs make instead.

Usage
-----
In prmake, a prfile has three additional commands:

    #begincode <commands>

and

    #endcode

and

    #includecode <filename>

`<commands>` need not be a single word, but usually it is, e.g. `python`.

The text between the `#begincode` and `#endcode` lines is put in a temporary file,
as is the contents of any `<filename>` specified by `#includecode`.

Then the command

    <commands> <temporary_file>

is run as a Python subprocess,
with its standard output piped to the makefile.
Everything else in the prfile is piped unchanged to the makefile.

    Usage: prmake [options]    or    python prmake.py [options]
    The following options are processed by prmake:
    -f FILE         specifies FILE as a *makefile*.
    --file=FILE     specifies FILE as a *makefile*.
    --makefile=FILE specifies FILE as a *makefile*.
    -h              Displays this message.
    --make=NAME     Specifies NAME as the make executable, default is "make".
    --prfile=FILE   Specifies FILE as the *prfile* name.
    --prext=PREXT   If --prfile not set, the *prfile* name is the *makefile*
                    name plus PREXT as an extension. Default is ".pr".
    --prforce       Forces the rebuild of the *makefile*.
    --prkeep        Temporary files are kept, and their names printed.
    --prhelp        For more help.
    All other command line options are passed to "make".

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

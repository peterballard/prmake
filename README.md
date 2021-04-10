# prmake version 0.4.2
Preprocessor to build more powerful makefiles

(c) Peter Ballard, 2019, 2020, 2021

Free to reuse and modify under the terms of the GPLv3 (see "License" below).

Installation
------------
1. Download `prmake-0.4.2.tar.gz`
2. Untar `prmake-0.4.2.tar.gz`; on most Unix-like systems the command `tar -xf prmake-0.4.2.tar.gz` will do this.
3. `cd prmake-0.4.2`
4. `python setup.py install`

If for someone reason this does not work, simply copy the file `prmake` to somewhere in your `PATH`.

Description
-----------
`make` ( https://www.gnu.org/software/make/ ) is a great tool, but it is hard to make complicated rules.
`prmake` makes it easier to write complicated makefile rules.

`prmake` processes a *prfile* (usually called `Makefile.pr`)
in a high level language (such as Python),
creating a post-processed makefile (usually called `Makefile`);
then invokes `make` on that post-processed makefile.

`prmake` is designed so that it can replace `make` gradually and without disruption:
- `prmake` is invoked in the same way as `make`.
- `prmake` by default writes its output to `Makefile`,
  so a makefile is where a non-prmake-user would expect to find it.
  This means one user can use `prmake` without requiring other users to use `prmake`.
- `prmake` refuses to overwrite a hand-edited makefile;
  it only overwrites a makefile which has been created by `prmake`.
- If no prfile is present, `prmake` runs `make` instead.
- All `make` code still works. So the user can start with an existing makefile as their prfile,
  and add as much or as little specialised code as they want.

Usage - prmake syntax
---------------------
In `prmake`, a prfile has three additional commands:

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

Usage - command line
--------------------

    Usage: prmake [options]    or    python prmake.py [options]
    The following options are processed by prmake:
    -f FILE         specifies FILE as a *makefile*.
    --file=FILE     specifies FILE as a *makefile*.
    --makefile=FILE specifies FILE as a *makefile*.
                    Default *makefile* names, in order of precedence, are
                    "GNUMakefile", "makefile" and "Makefile".
    -h              Displays this message.
    --make=NAME     Specifies NAME as the make executable, default is "make".
    --prfile=FILE   Specifies FILE as the *prfile* name.
    --prext=PREXT   If --prfile not set, the *prfile* name is the *makefile*
                    name plus PREXT as an extension. Default is ".pr".
    --prforce       Forces the rebuild of the *makefile*.
    --prkeep        Temporary files are kept, and their names printed.
    --prhelp        For more help.
    All other command line options are passed to "make".

Name and History
----------------
The name pays homage to `pmake`, which was `make` with a C pre-processor,
and was heavily used at two of my previous employers:
[Austek Microsystems](https://en.wikipedia.org/wiki/Austek_Microsystems)
and [RADLogic](https://www.radlogic.com.au/).
The "pr" stands for "pre-processor".

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

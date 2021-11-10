# prmake 

Description
-----------
`make` ( https://www.gnu.org/software/make/ ) is a great tool, 
but it is hard to write complicated rules in `make`.

`prmake` is a `make` wrapper, designed to make it easier write complicated rules.
It processes a *prfile* (usually called `Makefile.pr`),
creating a *makefile* (usually called `Makefile`);
and then invokes `make` on that *makefile*.

The *prfile* can contain loops and conditionals written in a high-level language such as Python,
allowing almost arbitrary complexity in `make` targets and rules.

A key feature of 
`prmake` is that it can replace `make` gradually and without disruption.
When `prmake` is invoked:
- If no *prfile* is present, `prmake` runs `make` instead.

- Otherwise, if a *makefile* is present which has not been written by `prmake`,
  `prmake` stops and issues a warning.

- Otherwise, `prmake` writes a *makefile*,
  before running `make` using that *makefile*.

This means:
- **It is safe for non-prmake users.**
Another user can come into the project without having to learn `pmake`,
find *makefiles* where they would expect them,
and edit *makefiles* safe in the knowledge that `prmake` will not overwrite them.

- **It is safe for prmake users.**
If the *makefile* has been changed by another user,
`prmake` will refuse to run.
So there is no danger of missing updates.

- **You can use  as much or as little `prmake` functionality as you want to.**
All `make` code works under `prmake`,
and all `make` command line options work under `prmake`,
so a user can start with an existing *makefile* as their *prfile*
and add as much or as little specialised code as they want,
In fact, the simplest way to start is to simply rename `Makefile` to `Makefile.pr`
and invoke `prmake` instead of `make`;
and no functionality will change.

Installation
------------
1. Download the source (code -> Download zip)
2. unzip the source.
3. Go to the directory containing the source files.
4. type `python setup.py install`

If for someone reason this does not work,
there is a manual workaround:
1. Download the file `prmake`.
2. Ensure that it is executable (`chmod a+x prmake`).
3. Move it to somewhere in your `PATH`.

Usage - prmake syntax
---------------------
In `prmake`, a *prfile* has three special commands:

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
with its standard output piped to the *makefile*.

Everything else in the *prfile* is piped unchanged to the *makefile*.
`prmake` then invokes `make` on that *makefile*,
passing all command line options (except special `prmake` options) to `make`.

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

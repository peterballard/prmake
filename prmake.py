# prmake.py
#
#(C) Peter Ballard, 2019, 2020
# Version 0.3, 9-May-2020
# Version 0.3.1, 24-Aug-2020  (this should match printed comment header)
#  Free to reuse and modify under the terms of the GPL

import sys
import os
import subprocess
import tempfile

################################################################################ <-- 80 columns
def usagelong():
    sys.stdout.write("""prmake is a "make" pre-processor.
It processes a *prfile* and builds a *makefile*,
then invokes "make" using *makefile* as the makefile.
This (in the author's opinion) simplifies the creation and maintenance of
makefiles with complicated rules or many similar targets.

prmake can co-exist with "make":
* "make" users are not forced to use prmake; they can continue to use "make"
  instead of prmake, whether or not a *prfile* exists
* prmake users are not forced to use "make"; prmake behaves exactly like "make"
  (using *makefile*) if no *prfile* exists.
* prmake users cannot accidentally overwrite a useful *makefile*.
  Every *makefile* created by prmake has a special comment in its first line.
  prmake exits if *makefile* does not begin with than comment.

A *prfile* has 3 special commands: #begincode, #includecode and #endcode.
The #begincode and #endcode commands must be a pair,
optionally with one or more #includecode lines in between them,
like this:

#begincode EXECUTABLE
<code>
#includecode FILENAME
<perhaps more code>
#endcode

EXECUTABLE need not be a single word, but usually it is, e.g. "python".

Everything between #begincode and #endcode is piped to a temporary file
(which we refer to as TMPFILE); except for any #includecode lines,
in which case the contents of FILENAME is piped to TMPFILE.

Then the command:
 EXECUTABLE TMPFILE
is run, with its standard output piped to *makefile*.

Everything else in *prfile* is piped unchanged to *makefile*.

Then "make" is run, using the newly created *makefile* as the makefile.
""")
    sys.exit(1)
################################################################################ <-- 1 columns

################################################################################ <-- 80 columns
def usage():
    sys.stdout.write("""Usage: prmake [options]    or    python prmake.py [options]
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
""")
    sys.exit(1)
################################################################################ <-- 1 columns

# prfile is the original Makefile.pr
# makefile is the post-processed Makefile
def make_Makefile(prfile, makefile, prforce, prkeep):
    if not os.path.exists(prfile) and not os.path.exists(makefile):
        sys.stdout.write("prmake error: Neither %s nor %s exists, exiting.\n" % (prfile, makefile))
        usage()
        
    if not os.path.exists(prfile):
        sys.stdout.write("prmake: No %s, so not rebuilding %s\n" % (prfile, makefile))
        return

    ip = open(prfile, "r")
    lines = ip.readlines()
    ip.close()

    # makefile always depends on prfile
    dependencies = [prfile]
    # check for extra dependencies in any #includecode statements
    for line in lines:
        words = line.split()
        if len(words) and words[0]=="#includecode":
            dependencies.append(words[1])

    # determine whether makefile is already up-to-date
    if os.path.exists(makefile) and not prforce:
        # makefile exists, and we are not forcing a rebuild using prmake --prforce,
        # So maybe it is up to date: let's just check the dependencies
        for d in dependencies:
            if not os.path.exists(d):
                sys.stdout.write("prmake: Cannot find dependency %s\n" % d)
                break
            if os.path.getmtime(d) >= os.path.getmtime(makefile):
                break # dependency is newer, we have to rebuild makefile
        else:
            # makefile is also later than all dependencies, so it is up to date
            sys.stdout.write("prmake: %s is up to date\n" % makefile)
            return

    # if makefile exists, check it is not a source
    if os.path.exists(makefile):
        ip = open(makefile, "r")
        line = ip.readline()
        ip.close()
        if line.find("# created automatically by prmake") != 0:
            sys.stdout.write("prmake warning: Stopping because %s already exists and is not output from prmake. Rename or delete %s, or use make instead of prmake.\n" % (makefile, makefile))
            sys.exit(1)

    sys.stdout.write("prmake: Building %s\n" % makefile)
    # write to makefile with "fail" postpended, only rename to makefile if all is successful
    if os.path.exists(makefile):
        os.remove(makefile)
    if os.path.exists(makefile+"fail"):
        os.remove(makefile+"fail")

    op = open(makefile+"fail", "w")
    op.write("# created automatically by prmake  <--- prmake checks for this string\n")
    op.write("##########################\n")
    op.write("# Generated from %s using the 'prmake' command.\n" % (prfile))
    op.write("# https://github.com/peterballard/prmake (version 0.3.1, 24-Aug-2020)\n")
    op.write("# If you are using prmake, edit %s rather than this file, because %s is the source.\n" % (prfile, prfile))
    op.write("# \n")
    op.write("# If you are NOT using prmake, and need to edit this file:\n")
    op.write("#   delete the string '# created automatically by prmake' in the first line of this file,\n")
    op.write("#   to prevent prmake overwriting this file in future.\n")
    op.write("##########################\n")
    op.write("\n")
    
    doing_code = 0
    linenum = 0
    for line in lines:
        linenum += 1
        words = line.split()
        
        if len(words) and words[0]=="#begincode":
            if doing_code:
                raise Exception("nested #begincode statements at line %d\n" % linenum)
            if len(words)==1:
                raise Exception("Missing command in #begincode on line %d\n" % linenum)
            doing_code = 1
            # This is the command that will be called, minus the file name (which will be supplied)
            # normally "command" will be something like "python" or "gawk", though the path can also be included e.g. "/usr/bin/python"
            command = line.replace("#begincode", "", 1).strip()
            codefragment = ""
            
        elif len(words) and words[0]=="#endcode":
            if not doing_code:
                raise Exception("#endcode statements at line %d without matching #begincode\n" % linenum)
            doing_code = 0
            # tf is short for temporary file
            # we put "codefragment" in this temporary file
            (tfhandle, tfname) = tempfile.mkstemp()
            tf = os.fdopen(tfhandle, "w")
            tf.write(codefragment)
            tf.close()
            # add the file name to "command"
            cmd = command + " " + tfname
            if prkeep:
                sys.stdout.write("prmake: Keeping temporary file from command: %s\n" % cmd)
            try:
                s = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError: # this is raised if the subprocess raises an error
                # delete temporary file, then re-raise exception
                if not prkeep:
                    os.remove(tfname)  # even in the case of an error, we do not keep the temporary file unless prkeep is set
                raise
            op.write(s.decode("utf-8")) # s is the standard output from "cmd", so write it to makefile
            if not prkeep:
                os.remove(tfname)  # temporary file is no longer needed, so delete it
                
        elif doing_code:
            if len(words) and words[0]=="#includecode":
                if len(words) >= 2:
                    ip2 = open(words[1], "r")
                    contents = ip2.read()
                    ip2.close()
                    codefragment += contents
                if len(words) > 2:
                    sys.stdout.write("prmake: Including code but ignoring redundant words in line: %s\n" % line.strip())
                if len(words) == 1:
                    sys.stdout.write("prmake: Ignoring line: %s\n" % line.strip())
            else:
                codefragment += line
            
        else:
            op.write(line)

    if doing_code:
        raise Exception("missing #endcode statement")
    op.close()
    os.rename(makefile+"fail", makefile)


def main():
    #### 1. Set up defaults and process the command line
    makeargs = [] # arguments which will be passed to "make"
    prfiles = []   # names of prfile(s) 
    makefiles = [] # nmes of makefile(s)
    j = 1
    prforce = False
    prkeep = False
    prext = ".pr"
    make = "make" # executable for make. User may want to specify a path, or even a different version of "make"
    while j < len(sys.argv):
        arg = sys.argv[j]

        # arguments beginning with "--pr" or "-pr" are used by prmake, and are not passed on to "make"
        if arg[:4]=="--pr" or arg[:3]=="-pr":
             # little trick to handle either "-" or "--" before the argument name
            if arg[:4]=="--pr":
                pvar = arg[2:]
            else:
                pvar = arg[1:]

            if pvar[:6]=="prext=":
                prext = pvar[6:]
            elif pvar[:7]=="prfile=":
                prfiles.append(pvar[7:])
            elif pvar=="prforce":
                prforce = True
            elif pvar=="prhelp":
                usagelong()
            elif pvar=="prkeep":
                prkeep = True
            else:
                sys.stdout.write("prmake: unknown prmake option %s\n" % arg)
                usage()
                
        # It would be super confusing to call this option --prmake, so call it --make even though it is a prmake option
        elif arg[:7]=="--make=":
            make = arg[7:]

        elif arg in ["-h"]: #, "-help", "--help", "-usage", "--usage"]:
            usage()

            # any argument specifying the Makefile name has to be handled specially.
            # Use the same 3 arguments as GNU make does
        elif arg=="-f":
            makefiles.append(sys.argv[j+1])
            j += 1  # increment one because there is a space between -f and the file name
        elif arg[:7]=="--file=":
            makefiles.append(arg[7:])
        elif arg[:11]=="--makefile=":
            makefiles.append(arg[11:])
            
        else:
            # all other arguments are passed on to "make"
            makeargs.append(arg)
        j += 1

    ################
    # different actions depending on makefiles and prfiles

    if len(makefiles)==0 and len(prfiles)==0:
        # probably the most common case. Find a default prfile and work from there
        dir = os.listdir(".") 
        for makefile in ["GNUmakefile", "makefile", "Makefile"]:
            prfile = makefile + prext
            if prfile in dir:
                prfiles.append(prfile)
                makefiles.append(makefile)
                break
        else:
            sys.stdout.write("prmake: No GNUmakefile%s, makefile%s or Makefile%s found, invoking ordinary make instead...\n" % (prext, prext, prext))
            cmd = "make " + " ".join(makeargs)
            sys.stdout.write("prmake: Running: " + cmd + "\n")
            status = subprocess.call(cmd, shell=True)
            sys.exit(status)

    elif len(makefiles)>0 and len(prfiles)==0:
        # find the prfile(s) to match the makefile(s)
        for makefile in makefiles:
            prfile = makefile + prext
            prfiles.append(prfile)

    elif len(makefiles)==0 and len(prfiles)>0:
        # find the makefile(s) to match the prfile(s)
        k = len(prext)
        for prfile in prfiles:
            # just do the substitution, we check for the existence of makefile later
            if prfile[-k:]==prext:
                makefile = prfile[:-k]
                makefiles.append(makefile)
            else:
                sys.stdout.write("prmake error: cannot determine makefile name, because prfile '%s' does not end in string prext='%s'\n", prfile, prext)
                usage()

    else: # len(makefiles)>0 and len(prfiles)>0:
        if len(makefiles) != len(prfiles):
            # this can happen if both makefiles and prfiles are specified from command line
            sys.stdout.write("prmake error: specified %d makefiles but %d prfiles\n" % (len(makefiles), len(prfiles)))
            usage()

    ###########
    # Now we have makefiles and prfiles of equal (nonzero) length
    # but no idea whether all specified files exist

    for j in range(len(prfiles)):
        prfile = prfiles[j]
        makefile = makefiles[j]
        # This command writes (or re-writes) makefile
        # but also checks existence of prfile, whether makefile is up-to-date, and whether makefile is a source
        make_Makefile(prfile, makefile, prforce, prkeep)

    ###########
    #### Build the command line in order to run "make", using the generated makefile (usually called "Makefile") as the Makefile.
    #  (and GNU make can support multiple Makefiles, hence the little loop)
    cmd = make
    for makefile in makefiles:
        cmd = cmd + " -f " + makefile
    cmd = cmd + " " + " ".join(makeargs)
    sys.stdout.write("prmake: Running: " + cmd + "\n")

    #### run that command line. This is the line which actually invokes "make"
    status = subprocess.call(cmd, shell=True)

    #### last of all, return whatever status "make" returns
    sys.exit(status)
    
main()

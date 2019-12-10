# prmake.py
#
#(C) Peter Ballard, December 2019.
#  Free to reuse and modify under the terms of the GPL

import sys
import os
import subprocess
import tempfile

################################################################################ <-- 80 columns
def usage():
    print("""
prmake processes a Makefile (usually called "Makefile")
 and creates a post-processed Makefile (usually called "Makefilepr"),
 then invokes "make" on that post-processed Makefile.
   
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

Usage: prmake [options]    or    python prmake.py [options]
   The following options are processed by prmake:
     -f <Makefile>         specifies the Makefile
     --file=<Makefile>     specifies the Makefile
     --makefile=<Makefile> specifies the Makefile
     -h displays this message
     --make=<NAME> specifies the "make" executable, default is "make"
     --prforce=1 forces the rebuild of the post-processed Makefile (normally only remade if out of date)
     --prkeep=1 means temporary files are kept (and their locations printed)
     --prsuffix=<SUFFIX> specifies the suffix for post-processed Makefiles, default is "pr"
   All other command line arguments are passed to "make".

If no Makefile is specified, prmake searches for the following files as
 the Makefile, in order: "prmakefile", "GNUmakefile", "makefile", "Makefile".
""")
    sys.exit(1)
################################################################################ <-- 80 columns

# makefile is the original Makefile
# prfile is the post-processed Makefile
def make_Makefile(makefile, prfile, prforce, prkeep):
    if not os.path.exists(makefile):
        sys.stdout.write("No %s, exiting\n" % makefile)
        sys.exit(1)
    if not prforce and os.path.exists(prfile) and os.path.getmtime(makefile) < os.path.getmtime(prfile):
        # prfile exists and is up to date, and we are not forcing a rebuild using prmake, so do nothing
        #sys.stdout.write("not building: %s is up to date\n" % prfile)
        return
    sys.stdout.write("Building: %s\n" % prfile)
    # write to prfile with "fail" postpended, only rename to prfile if all is successful
    if os.path.exists(prfile):
        os.remove(prfile)
    if os.path.exists(prfile+"fail"):
        os.remove(prfile+"fail")
    ip = open(makefile, "r")
    op = open(prfile+"fail", "w")
    op.write("# Generated from %s using prmake.py, command line arguments (sys.argv) were:\n" % makefile)
    op.write("#     %s\n" % str(sys.argv))
    op.write("#\n")
    
    doing_code = 0
    linenum = 0
    for line in ip.readlines():
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
                sys.stdout.write("Keeping temporary file from command: %s\n" % cmd)
            try:
                s = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError: # this is raised if the subprocess raises an error
                # delete temporary file, then re-raise exception
                if not prkeep:
                    os.remove(tfname)  # even in the case of an error, we do not keep the temporary file unless prkeep is set
                raise
            op.write(s) # s is the standard output from "cmd", so write it to prfile
            if not prkeep:
                os.remove(tfname)  # temporary file is no longer needed, so delete it
                
        elif doing_code:
            codefragment += line
            
        else:
            op.write(line)
    ip.close()
    op.close()
    os.rename(prfile+"fail", prfile)


def main():
    #### 1. Set up defaults and process the command line
    makeargs = [] # arguments which will be passed to "make"
    makefiles = []   # names of Makefile(s)
    j = 1
    prforce = 0
    prkeep = 0
    make = "make" # executable for make. User may want to specify a path, or even a different version of "make"
    prsuffix = "pr" # suffix used for post-processed files, suitable for running on "make"
    while j < len(sys.argv):
        arg = sys.argv[j]

        # arguments beginning with "--prmake" or "-prmake" are used by prmake, and are not passed on to "make"
        if arg[:7]=="--prmake" or arg[:6]=="-prmake":
            parts = arg.split("=")
            pvar = parts[0].replace("-", "") # little trick to handle either "-" or "--" before the argument name

            if pvar in ["prforce", "prkeep"] and parts[1] not in ["0", "1"]:
                raise Exception("argument %s can only take values 0 (meaning false) or 1 (meaning true)" % pvar)
            
            if len(parts)==2 and pvar=="prforce":
                prforce = int(parts[1])
            elif len(parts)==2 and pvar=="prkeep":
                prkeep = int(parts[1])
            elif len(parts)==2 and pvar=="prsuffix":
                prsuffix = parts[1]
            else:
                sys.stdout.write("unknown prmake argument %s\n" % arg)
                usage()

        elif arg[:7]=="--make=":
            make = arg[7:]

        elif arg in ["-h"]: #, "-help", "--help", "-usage", "--usage"]:
            usage()

            # any argument specifying the Makefile name has to be handled specially.
            # Use the same 3 arguments as GNU make does
        elif arg=="-f":
            makefile = sys.argv[j+1]
            j += 1  # increment one because there is a space between -f and the file name
        elif arg[:7]=="--file=":
            makefile = arg[7:]
        elif arg[:11]=="--makefile=":
            makefile = arg[11:]
            
        else:
            # all other arguments are passed on to "make"
            makeargs.append(arg)
        j += 1

    #### 2. Search for a Makefile if none has been specified.
    #        GNU make searches for "GNUmakefile", "makefile", "Makefile" in order.
    #        For prmake, we add "prmakefile" in case user wants to create a makefile for prmake,
    #        but wants a different Makefile available if prmake is unavailable. (Though I do not recommend doing this!)
    if len(makefiles)==0:
        # do not use os.file.exists() because Mac OS is case independent on file names,
        #  meaning os.file.exists("makefile") will be true if only "Makefile" exists,
        #  causing prfile to be called "makefilepr" instead of "Makefilepr"
        dir = os.listdir(".") 
        for makefilename in ["prmakefile", "GNUmakefile", "makefile", "Makefile"]:
            if makefilename in dir:
                makefiles.append(makefilename)
                break
        else:
            raise Exception("no prmakefile, GNUmakefile, makefile or Makefile found\n")

    #### 3. For each makefile (Makefile), create a prfile (post-processed Makefile)
    # it is very rare to have more than one Makefile in a single command, but GNU "make" can handle it, so we support it
    prfiles = []
    for makefile in makefiles:
        prfile = makefile + prsuffix
        make_Makefile(makefile, prfile, prforce, prkeep)
        prfiles.append(prfile)

    if len(prfiles)==0:
        # We should never get to this point, but just in case...
        raise Exception("something has gone wrong: no makefiles to run")

    #### 4. Build the command line in order to run "make", using the generated "prfile" (usually called "Makefilepr") as the Makefile.
    #  (and GNU make can support multiple Makefiles, hence the little loop)
    cmd = make
    for prfile in prfiles:
        cmd = cmd + " -f " + prfile
    cmd = cmd + " " + " ".join(makeargs)
    sys.stdout.write("Running: " + cmd + "\n")

    #### 5. run that command line. This is the line which actually invokes "make"
    status = subprocess.call(cmd, shell=True)

    #### 6. last of all, return whatever status "make" returns
    sys.exit(status)
    
main()

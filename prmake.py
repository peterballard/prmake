# prmake.py
#
#(C) Peter Ballard, 2019, 2020
# Version 0.3, 9-May-2020
#  Free to reuse and modify under the terms of the GPL

import sys
import os
import subprocess
import tempfile

################################################################################ <-- 80 columns
def usage():
    print("""
prmake processes a prfile (usually called "Makefile.pr")
and creates a post-processed Makefile (usually called "Makefile"),
then invokes "make" on that post-processed Makefile.
   
In prmake, a Makefile.pr has two additional commands:
    #begincode <commands>
and
    #endcode
<commands> need not be a single word, but usually it is, e.g. "python".
The text between the #begincode and #endcode lines is put in a temporary file,
and then the command
    <commands> <temporary_file>
is run as a Python subprocess,
with its standard output piped to the post-processed Makefile.
Everything else in the prfile is piped unchanged to the post-processed Makefile.

Usage: prmake [options]    or    python prmake.py [options]
    The following options are processed by prmake:
    -f <Makefile>         specifies the Makefile
    --file=<Makefile>     specifies the Makefile
    --makefile=<Makefile> specifies the Makefile
    -h displays this message
    --make=<NAME> specifies the "make" executable, default is "make"
    --prfile=<PRFILE> specifies prfile name. Overrides --prext. Defaults in order: "GNUmakefile.pr", "makefile.pr", "Makefile.pr".
    --prext=<PREXT> specifies extension of prfiles. Default is ".pr"
    i.e. Makefile usually called "Makefile", so prfile usually called "Makefile.pr"
    --prforce=1 forces the rebuild of the post-processed Makefile (normally only remade if out of date)
    --prkeep=1 means temporary files are kept (and their locations printed)
    All other command line arguments are passed to "make".
""")
    sys.exit(1)
################################################################################ <-- 1 columns

# prfile is the original Makefile.pr
# makefile is the post-processed Makefile
def make_Makefile(prfile, makefile, prforce, prkeep):
    if not os.path.exists(prfile) and not os.path.exists(makefile):
        sys.stdout.write("Neither %s nor %s exists, exiting.\n" % (prfile, makefile))
        sys.exit(1)
        
    if not os.path.exists(prfile):
        sys.stdout.write("No %s, so not rebuilding %s\n" % (prfile, makefile))
        return
    
    if not prforce and os.path.exists(makefile) and os.path.getmtime(prfile) < os.path.getmtime(makefile):
        # makefile exists and is up to date, and we are not forcing a rebuild using prmake, so do nothing
        sys.stdout.write("%s is up to date\n" % makefile)
        return

    # if makefile exists, check it is not a source
    if os.path.exists(makefile):
        ip = open(makefile, "r")
        line = ip.readline()
        ip.close()
        if line.find("# created automatically by prmake") != 0:
            sys.stdout.write("Stopping because %s already exists and is not output from prmake. Rename or delete %s, or use make instead of prmake.\n" % (makefile, makefile))
            sys.exit(1)

    sys.stdout.write("Building: %s\n" % makefile)
    # write to makefile with "fail" postpended, only rename to makefile if all is successful
    if os.path.exists(makefile):
        os.remove(makefile)
    if os.path.exists(makefile+"fail"):
        os.remove(makefile+"fail")
    ip = open(prfile, "r")
    op = open(makefile+"fail", "w")
    op.write("# created automatically by prmake  <--- prmake checks for this string\n")
    op.write("##########################\n")
    op.write("# Generated from %s using the 'prmake' command.\n" % (prfile))
    op.write("# If you are using prmake, edit %s rather than this file, because %s is the source.\n" % (prfile, prfile))
    op.write("# \n")
    op.write("# If you are NOT using prmake, and need to edit this file:\n")
    op.write("#   delete the string '# created automatically by prmake' in the first line of this file,\n")
    op.write("#   to prevent prmake overwriting this file in future.\n")
    op.write("##########################\n")
    op.write("\n")
    
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
            op.write(s.decode("utf-8")) # s is the standard output from "cmd", so write it to makefile
            if not prkeep:
                os.remove(tfname)  # temporary file is no longer needed, so delete it
                
        elif doing_code:
            codefragment += line
            
        else:
            op.write(line)
    ip.close()
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
    prforce = 0
    prkeep = 0
    prext = ".pr"
    make = "make" # executable for make. User may want to specify a path, or even a different version of "make"
    while j < len(sys.argv):
        arg = sys.argv[j]

        # arguments beginning with "--pr" or "-pr" are used by prmake, and are not passed on to "make"
        if arg[:4]=="--pr" or arg[:3]=="-pr":
            parts = arg.split("=")
            if len(parts)!=2:
                usage()
            
            pvar = parts[0].replace("-", "") # little trick to handle either "-" or "--" before the argument name

            if pvar in ["prforce", "prkeep"] and parts[1] not in ["0", "1"]:
                sys.stdout.write("Error: argument %s can only take values 0 (meaning false) or 1 (meaning true)" % pvar)
                usage()
            
            if len(parts)==2 and pvar=="prforce":
                prforce = int(parts[1])
            elif len(parts)==2 and pvar=="prkeep":
                prkeep = int(parts[1])
            elif len(parts)==2 and pvar=="prext":
                prext = parts[1]
            elif len(parts)==2 and pvar=="prfile":
                prfiles.append(parts[1])
            else:
                sys.stdout.write("unknown prmake argument %s\n" % arg)
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
            sys.stdout.write("no GNUmakefile%s, makefile%s or Makefile%s found, invoking ordinary make instead...\n" % (prext, prext, prext))
            cmd = "make " + " ".join(makeargs)
            sys.stdout.write("Running: " + cmd + "\n")
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
                sys.stdout.write('Error: cannot create makefile name because prfile "%s" does not end in string prext="%s"\n', prfile, prext)
                usage()

    else: # len(makefiles)>0 and len(prfiles)>0:
        if len(makefiles) != len(prfiles):
            # this can happen if both makefiles and prfiles are specified from command line
            sys.stdout.write("Error: specified %d makefiles but %d prfiles\n" % (len(makefiles), len(prfiles)))
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
    sys.stdout.write("Running: " + cmd + "\n")

    #### run that command line. This is the line which actually invokes "make"
    status = subprocess.call(cmd, shell=True)

    #### last of all, return whatever status "make" returns
    sys.exit(status)
    
main()

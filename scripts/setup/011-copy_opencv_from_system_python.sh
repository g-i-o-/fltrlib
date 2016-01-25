#! /bin/sh

## get node root (we will install the virtual environment there)
envdir=".env"

progdir=`dirname $0`
rpprogdir=`readlink -f $progdir`
pkgroot=`readlink -f $rpprogdir/../..`

envpath="$pkgroot/$envdir"
to_copy="cv cv2"

if [ -d "$envpath" ]; then
    syspython=`which python`
    echo "System python: $syspython\n"    
    echo "Virtual environment :  $envpath"
    envpython="$envpath/bin/python"
    echo "  path     : $envpath"
    echo "  python   : $envpython"
    envpackages=`$envpython -c 'import sys; p=[x for x in sys.path if "packages" in x and "local" not in x];sys.stdout.write(p[0]) if p else None'`
    echo "  packages : $envpackages"
    
    echo "Copying packages :"
    for i in $to_copy; do
        echo "  $i :"
        pgkfile=`$syspython -c "import $i; print $i.__file__"`
        file=`basename $pgkfile`
        dest="$envpackages/$file"
        echo "    from : $pgkfile"
        echo "    to   : $dest"
        cp $pgkfile $dest
    done
    
else
    echo "Error: Virtual environment not found"
fi

 #!/bin/bash
SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

if [ ! -d dnsdmpstr ]; then
    git clone https://github.com/zeropwn/dnsdmpstr.git $SCRIPTPATH/dnsdmpstr
    touch $SCRIPTPATH/dnsdmpstr/__init__.py
fi
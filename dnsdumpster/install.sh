 
#!/bin/bash
SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

if [! dnsdmpstr ]; then
    git clone https://github.com/zeropwn/dnsdmpstr.git $SCRIPTPATH/dnsdmpstr
fi
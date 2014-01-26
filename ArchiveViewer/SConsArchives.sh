#!/bin/bash

set -e

#-----------------------------------#
#             Functions             #
#-----------------------------------#

function get_scala_home {
    # check if $SCALA_HOME is set
    if [ -z $SCALA_HOME ]; then
        # try to find it at common locations
        dists=('Fedora' 'Ubuntu')
        paths=('/usr/share/scala' '/usr/share/java')
        for indx in 0 1
        do
            SCALA_HOME=${paths[$indx]}  
            if [ -d $SCALA_HOME ]; then
                break
            fi
            SCALA_HOME=''
        done
    fi

    # check if $SCALA_HOME could be found
    if [ -z $SCALA_HOME ]; then
        echo '$SCALA_HOME is not set'
        exit 2
    else
        echo $SCALA_HOME
        return 0
    fi
}

function get_scala_library_path {
    SCALA_HOME=$1
    scala_library=$SCALA_HOME'/scala-library.jar'
    if [ -f $scala_library ] ; then
        echo $scala_library
        return 0
    fi
    # try with lib folder
    scala_library=$SCALA_HOME'/lib/scala-library.jar'
    if [ -f $scala_library ] ; then
        echo $scala_library
        return 0
    else
        echo 'error: scala-library.jar could not be found';
        exit 1
    fi
}

function get_classpath {
    SCALA_HOME=$1
    # Except for Scala the required libraries come
    # with the GUI.
    lib_folder='.'
    guijar=$lib_folder'/SConsArchives.jar'
    libs=$guijar
    scala_library=`get_scala_library_path $SCALA_HOME`
    classpath=$libs':'$scala_library
    echo $classpath
}

#-------------------------------#
#              RUN              #
#-------------------------------#

SCALA_HOME=`get_scala_home`
echo 'SCALA_HOME: '$SCALA_HOME

classpath=`get_classpath $SCALA_HOME`
echo 'CLASSPATH:  '$classpath

# start GUI
java -cp $classpath Starter

exit $?

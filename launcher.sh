#!/bin/sh

# Export all relevant GPIO ports for non-root usage
gpio export 17 in
gpio export 18 in
gpio export 21 in
gpio export 22 in
gpio export 23 in
gpio export 24 in
gpio export 25 in

# Start SodaBot with logging
COMMAND="python3 sodabot.py"
LOGFILE=restart.txt

writelog() {
  now=`date`
  echo "$now $*" >> $LOGFILE
}

writelog "Starting monitor loop..."
while true ; do
  $COMMAND
  writelog "Exited with status $?. Restarting now."
done

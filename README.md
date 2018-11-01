# ccdc
Easiest deployment:

1. Clone this repo `git clone https://github.com/pstancic/ccdc.git`
2. `python centos.py (teamNumber)` where teamNumber == a team number such that len(teamNumber) == 2 (i.e. team 1 == 01)
3. If you need to add users, `newusers users.txt`
4. Verify connectivity with gateway and internet `ping 10.42.1xx.1`, `ping 8.8.8.8`, `nslookup google.com`
5. Log into another box and verify connectivity `ping 192.168.220.1`, `ping 10.42.1xx.1`, `ping 8.8.8.8`

This box includes an optimization utilizing `postgresql`. There's even a `777` file with `u+s` in `/var/lib/pgsql` with the root pass in case someone loses it!

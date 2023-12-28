sudo apt install sysbench -y # For Debian/Ubuntu
# sudo apt-get install sysbench  # For Debian/Ubuntu
# sudo yum install sysbench      # For CentOS/RHEL

### Conduct a read-only transaction Sysbench Benchmark
### --threads=4 specifies the number of threads that Sysbench will use for the test.
### --time=60 sets the duration of the benchmark test in seconds.

sysbench --db-driver=mysql --mysql-db=sakila --mysql-user=anass --mysql_password=2121 --table-size=20000 --tables=7 /usr/share/sysbench/oltp_read_write.lua prepare
sysbench --db-driver=mysql --mysql-db=sakila --mysql-user=anass --mysql_password=2121 --table-size=20000 --tables=7 --threads=18 --max-time=20 /usr/share/sysbench/oltp_read_write.lua run

sysbench --db-driver=mysql --mysql-db=sakila --mysql-user=anass --mysql_password=2121 /usr/share/sysbench/oltp_read_write.lua cleanup
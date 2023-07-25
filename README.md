# pool-performance
Scripts for soak / performance tests of Apache Commons Pool using Commons-Performance.

Scripts in /bin execute runs of Commons-Performance using the configs in /configs for the Commons Pool versions in versions.txt.
Copy or git clone /configs and /bin to a local svn checkout of Commons Performance.

To get Commons Performance:
```
svn checkout http://svn.apache.org/repos/asf/commons/sandbox/performance/trunk/ commons-performance
```
To run all configs against all versions, do
```
bin/pool-compare.sh
```
Results will be written to /results

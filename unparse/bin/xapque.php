#!/usr/bin/php4 -q
<?php

# Calls functions in xapian.module, to act like xapque.py

# Example usages:
# 
# Everything containing "last" and "july"
# ./xapque.py ~/devel/undata xapdex.db/"last july"
# 
# Everything containing "last july" as a phrase
# ./xapque.py ~/devel/undata xapdex.db/"\"last july\""
# 
# Everything said by the Solomon Islands:
# ./xapque.py ~/devel/undata xapdex.db/"nation:solomonislands"
#
# Show all headings
# ./xapque.php ~/devel/undata xapdex.db/ "class:boldline"
#
# Everything underneath one heading ("-" --> "" in id)
# ./xapque.php ~/devel/undata xapdex.db/ "heading:pg001bk02" 

# Some code for testing Xapian module is loaded right
#$funcs = get_defined_functions();
#foreach ($funcs['internal'] as $k=>$v) {
#    print "$v\n";
#}
#print xapian_version_string();
#phpinfo();
#exit;

require "xapian.module";

$undata_path = $argv[1];
if (!$undata_path) {
    die("First parameter is path of undata\n");
}
$db_path = $argv[2];
if (!$db_path) {
    die("Second parameter is relative path of Xapian database\n");
}
$query = $argv[3];
if (!$query) {
    die("Third parameter is query string\n");
}
if ($argv[4]) {
    die("Please put the whole query in the second parameter, quoted\n");
}

$results = xapian_do_search($undata_path, $db_path, $query);
print_r($results);


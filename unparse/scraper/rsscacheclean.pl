#!/usr/bin/perl

use DBI;

open (CONFIG, "/data/vhost/www.undemocracy.com/docs/dbpasswords.py") || die " can't open pw file: $!";
while (my $line =<CONFIG>) {
        #print $line;
        if ($line =~ m#^\s*\##) {
            # comment
        } elsif ($line =~ m#^\s*$#) {
            # empty line
       } elsif ($line =~ m#(\S+)[\s=]+'(\S+)'#) {
            $Config{$1}=$2;
        }
}
close (CONFIG) ;

my $dsn = "DBI:mysql:$Config{'db_name'}:localhost"; # DSN connection string
my $dbh=DBI->connect($dsn, $Config{'db_user'}, $Config{'db_password'}, {RaiseError => 1});
$dbh->do("delete from rsscache");



